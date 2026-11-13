# Métodos y controles de las tablas de paso

Contenido: notación · construir la tabla (área, dasimétrico, puntos) · cobertura · aplicarla a extensivas e intensivas · controles · pureza · errores frecuentes.

## Notación

- `i`: unidad de origen; `j`: unidad de destino; `k`: pieza de la superposición `i ∩ j`.
- `a_ij`: cantidad de la variable auxiliar en la pieza (población, viviendas, portales o, como último recurso, área).
- Peso por origen: `w_ij = a_ij / Σ_j a_ij` (suma 1 en cada origen; columna `peso`). Reparte lo que tiene el origen.
- Peso por destino: `v_ij = a_ij / Σ_i a_ij` (suma 1 en cada destino; columna `peso_destino`). Promedia lo que llega al destino.
- Cobertura del origen: `Σ_j a_ij / a_i`, con `a_i` el total del origen entero. Menor que 1 si parte del origen cae fuera de los destinos.

## Construir la tabla

Las tres funciones devuelven la tabla y la cobertura de cada origen. Todas en CRS métrico.

```python
import geopandas as gpd


def pesos(t, id_o, id_d):
    t["peso"] = t["a"] / t.groupby(id_o)["a"].transform("sum")
    t["peso_destino"] = t["a"] / t.groupby(id_d)["a"].transform("sum")
    return t.rename(columns={id_o: "origen", id_d: "destino"})


def piezas_origen_destino(origen, destino, id_o, id_d):
    o = origen[[id_o, "geometry"]].to_crs(25830)
    d = destino[[id_d, "geometry"]].to_crs(25830)
    return o, gpd.overlay(o, d, how="intersection", keep_geom_type=True)


def tabla_paso_area(origen, destino, id_o, id_d, astilla=0.001):
    """Pesos por área. Solo como último recurso: supone población uniforme."""
    o, piezas = piezas_origen_destino(origen, destino, id_o, id_d)
    area_o = o.set_index(id_o).area
    piezas["a"] = piezas.area
    cobertura = (
        piezas.groupby(id_o)["a"].sum().reindex(area_o.index, fill_value=0) / area_o
    )
    # Astillas: piezas menores que una fracción del origen, por bordes que no coinciden
    es_astilla = piezas["a"] < astilla * piezas[id_o].map(area_o)
    print(
        f"astillas: {es_astilla.sum()} piezas, {piezas.loc[es_astilla, 'a'].sum():.0f} m²"
    )
    t = piezas[~es_astilla].groupby([id_o, id_d], as_index=False)["a"].sum()
    return pesos(t, id_o, id_d), cobertura
```

**Dasimétrico con una rejilla de población:** dentro de cada celda se reparte por área, que es mucho más fino que repartir por área el origen entero.

```python
def tabla_paso_dasimetrica(origen, destino, id_o, id_d, rejilla, col_pob):
    o, piezas = piezas_origen_destino(origen, destino, id_o, id_d)
    r = rejilla[[col_pob, "geometry"]].to_crs(25830)
    r["area_celda"] = r.area
    trozos = gpd.overlay(piezas, r, how="intersection", keep_geom_type=True)
    trozos["a"] = trozos[col_pob] * trozos.area / trozos["area_celda"]
    pob_o = gpd.overlay(o, r, how="intersection", keep_geom_type=True)
    pob_o = (
        (pob_o[col_pob] * pob_o.area / pob_o["area_celda"]).groupby(pob_o[id_o]).sum()
    )
    cobertura = (
        trozos.groupby(id_o)["a"].sum().reindex(pob_o.index, fill_value=0) / pob_o
    )
    t = trozos.groupby([id_o, id_d], as_index=False)["a"].sum()
    return pesos(t, id_o, id_d), cobertura
```

Un origen sin población en la rejilla da pesos `NaN` (0/0): `comprobar_tabla` lo detecta. Para esos, peso por área como respaldo, declarado. Con viviendas de edificios (polígonos o puntos con su número de viviendas) se hace igual, sustituyendo la rejilla.

**Puntos** (portales, edificios con su número de viviendas): se asigna a cada punto su origen y su destino y se cuenta (o se suman sus viviendas) por par. Es el método más preciso cuando hay puntos de calidad.

```python
def tabla_paso_puntos(puntos, origen, destino, id_o, id_d, cantidad=None):
    p = puntos.to_crs(25830)
    p["a"] = p[cantidad] if cantidad else 1
    n = len(p)
    p = gpd.sjoin(p, origen[[id_o, "geometry"]].to_crs(25830), predicate="within")
    con_origen = p.groupby(id_o)["a"].sum()
    p = p.drop(columns="index_right")
    p = gpd.sjoin(p, destino[[id_d, "geometry"]].to_crs(25830), predicate="within")
    # Menos puntos que al principio: fuera o justo en un borde; más: polígonos solapados
    print(f"puntos: {n} al principio, {len(p)} con origen y destino")
    cobertura = (
        p.groupby(id_o)["a"].sum().reindex(con_origen.index, fill_value=0) / con_origen
    )
    t = p.groupby([id_o, id_d], as_index=False)["a"].sum()
    return pesos(t, id_o, id_d), cobertura
```

Orígenes sin ningún punto se quedan fuera de la tabla: lístalos y decide (peso por área como respaldo, declarado).

## Cobertura

Los pesos se normalizan con lo que cae en los destinos, así que **un origen que cae en parte fuera reparte todo su valor entre los destinos que toca**. Si la cobertura de un origen es menor que 0,99:

- **Borde que no coincide** entre fuentes (diferencia pequeña): se acepta la normalización.
- **Parte del origen de verdad fuera del ámbito** (otro municipio, fuera de la capa de destino): multiplica su `peso` por la cobertura. El total ya no se conserva, a propósito: lo que queda fuera no se cuenta dentro.

Cada caso se lista y se decide; el criterio, en `docs/decisiones.md`.

## Aplicarla

**Extensiva** (recuento o suma): `y_j = Σ_i w_ij · y_i`.

```python
def pasar_extensiva(tabla, datos, col):
    m = tabla.merge(datos[["origen", col]], on="origen", validate="many_to_one")
    assert m[col].notna().all(), "orígenes sin dato: decide antes de repartir"
    return (m["peso"] * m[col]).groupby(m["destino"]).sum()
```

**Intensiva** (tasa, media, porcentaje):

1. Lo correcto: pasa el numerador y el denominador como extensivas y divide en el destino (`tasa_j = Σ_i w_ij·num_i / Σ_i w_ij·den_i`).
2. Si solo hay la tasa: media ponderada con `peso_destino` (`v_ij`) calculado con la auxiliar que hace de denominador (población para una tasa por habitante, hogares para una renta media por hogar). Nunca la media simple de las tasas de origen.

**Mediana o percentil:** no hay fórmula exacta. Aproximación con la media ponderada de las medianas (sesgada), marcada como «estimado» y con la pureza al lado; o, si existen, distribuciones por tramos o microdatos.

## Controles

```python
import numpy as np


def comprobar_tabla(tabla, origenes, destinos, col="peso"):
    por = "origen" if col == "peso" else "destino"
    assert tabla[col].notna().all(), tabla[tabla[col].isna()]
    suma = tabla.groupby(por)[col].sum()
    assert np.allclose(suma, 1, atol=1e-6), suma[~np.isclose(suma, 1, atol=1e-6)]
    assert not tabla.duplicated(["origen", "destino"]).any()
    assert tabla[col].between(0, 1).all()
    sin_destino = set(origenes) - set(tabla["origen"])
    sin_origen = set(destinos) - set(tabla["destino"])
    return sin_destino, sin_origen  # cada código de estas listas, explicado o corregido
```

Comprueba `col="peso"` y `col="peso_destino"`, y la cobertura (`cobertura[cobertura < 0.99]`). Además: total de una extensiva conocida igual antes y después (`np.isclose`), y comparación con un total oficial del destino si existe (segunda vía). Si la diferencia con el oficial es grande, el peso no representa lo que se reparte.

## Pureza

Parte de lo que llega a cada destino que viene de orígenes enteros (`w_ij ≥ 0,99`):

```python
def pureza(tabla, auxiliar):
    # auxiliar: columnas origen y a_origen (población o viviendas de cada origen)
    t = tabla.merge(auxiliar, on="origen")
    t["llega"] = t["peso"] * t["a_origen"]
    entera = t["llega"].where(t["peso"] >= 0.99, 0)
    return entera.groupby(t["destino"]).sum() / t["llega"].groupby(t["destino"]).sum()
```

Con pureza baja (orientativo: menos del 80 %), el valor del destino depende sobre todo del supuesto de reparto: se presenta como estimado y, si es una cifra clave, con el rango que dan dos pesos distintos (por ejemplo, población frente a viviendas).

## Errores frecuentes

| Error | Por qué está mal | Cómo se evita |
|---|---|---|
| Repartir una tasa o una media con `peso` | Las intensivas no se suman | Numerador y denominador, o `peso_destino` |
| Pesos por área en zonas con parques, polígonos o vías | Supone población uniforme | Dasimétrico o puntos |
| Superponer en EPSG:4326 | Áreas en grados, distintas según la latitud | CRS métrico (EPSG:25830) |
| Ignorar la cobertura | Un origen que cae en parte fuera infla los destinos que toca | Listar la cobertura < 0,99 y decidir |
| Límites de dos fuentes distintas | Astillas y orígenes partidos que no lo están | Umbral de astilla relativo al origen; mismo origen cartográfico si es posible |
| Unir años de seccionado por código | Un código puede cambiar de geometría | Superposición entre años |
| Auxiliar de otro año muy distinto | Los pesos describen otra población | Año de la auxiliar lo más cercano al dato, declarado |

Si el equipo prefiere una librería, `tobler` (PySAL) implementa la interpolación areal y dasimétrica; no está en el proyecto y añadirla exige justificarla en el PR.
