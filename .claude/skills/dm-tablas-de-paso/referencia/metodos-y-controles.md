# Métodos y controles de las tablas de paso

Contenido: notación · construir la tabla (superposición y puntos) · aplicarla a extensivas e intensivas · controles · pureza · errores frecuentes.

## Notación

- `i`: unidad de origen; `j`: unidad de destino; `k`: pieza de la superposición `i ∩ j`.
- `a_ij`: cantidad de la variable auxiliar en la pieza (población, viviendas, portales o, como último recurso, área).
- Peso por origen: `w_ij = a_ij / Σ_j a_ij` (suma 1 en cada origen). Reparte lo que tiene el origen.
- Peso por destino: `v_ij = a_ij / Σ_i a_ij` (suma 1 en cada destino). Promedia lo que llega al destino.

## Construir la tabla

**Superposición con variable auxiliar en polígonos o rejilla** (dasimétrico). Si la auxiliar viene en otra capa (una rejilla de población), se superpone primero con las piezas y se reparte por área *dentro de cada celda*, que es mucho más fino que repartir por área el origen entero.

```python
import geopandas as gpd


def tabla_paso_area(origen, destino, id_o, id_d, astilla=1.0):
    """Pesos por área (m²). Solo como último recurso o dentro de celdas pequeñas."""
    o = origen[[id_o, "geometry"]].to_crs(25830)
    d = destino[[id_d, "geometry"]].to_crs(25830)
    piezas = gpd.overlay(o, d, how="intersection", keep_geom_type=True)
    piezas["a"] = piezas.area
    piezas = piezas[piezas["a"] > astilla]  # astillas por bordes que no coinciden
    t = piezas.groupby([id_o, id_d], as_index=False)["a"].sum()
    t["peso"] = t["a"] / t.groupby(id_o)["a"].transform("sum")
    return t.rename(columns={id_o: "origen", id_d: "destino"})
```

**Puntos** (portales, edificios con su número de viviendas): se asigna a cada punto su origen y su destino con `sjoin` y se cuenta (o se suma el número de viviendas) por par. Es el método más preciso cuando hay puntos de calidad, y el natural para el código postal si los portales lo traen.

```python
def tabla_paso_puntos(puntos, origen, destino, id_o, id_d, cantidad=None):
    p = puntos.to_crs(25830)
    p = gpd.sjoin(p, origen[[id_o, "geometry"]].to_crs(25830), predicate="within")
    p = p.drop(columns="index_right")
    p = gpd.sjoin(p, destino[[id_d, "geometry"]].to_crs(25830), predicate="within")
    p["a"] = p[cantidad] if cantidad else 1
    t = p.groupby([id_o, id_d], as_index=False)["a"].sum()
    t["peso"] = t["a"] / t.groupby(id_o)["a"].transform("sum")
    return t.rename(columns={id_o: "origen", id_d: "destino"})
```

Orígenes sin ningún punto se quedan fuera: lístalos y decide (peso por área como respaldo, declarado).

## Aplicarla

**Extensiva** (recuento o suma): `y_j = Σ_i w_ij · y_i`.

```python
def pasar_extensiva(tabla, datos, col):
    m = tabla.merge(datos[["origen", col]], on="origen", validate="many_to_one")
    return (m["peso"] * m[col]).groupby(m["destino"]).sum()
```

**Intensiva** (tasa, media, porcentaje):

1. Lo correcto: pasa el numerador y el denominador como extensivas y divide en el destino (`tasa_j = Σ_i w_ij·num_i / Σ_i w_ij·den_i`).
2. Si solo hay la tasa: media ponderada con `v_ij` (peso por destino) calculado con la auxiliar que hace de denominador (población para una tasa por habitante, hogares para una renta media por hogar). Nunca la media simple de las tasas de origen.

**Mediana o percentil:** no hay fórmula exacta. Aproximación con la media ponderada de las medianas, marcada como «estimado» y con la pureza al lado; o, si existen, distribuciones por tramos o microdatos.

## Controles

```python
import numpy as np


def comprobar_tabla(tabla, origenes, destinos, por="origen"):
    suma = tabla.groupby(por)["peso"].sum()
    assert np.allclose(suma, 1, atol=1e-6), suma[~np.isclose(suma, 1, atol=1e-6)]
    assert not tabla.duplicated(["origen", "destino"]).any()
    assert tabla["peso"].between(0, 1).all()
    sin_destino = set(origenes) - set(tabla["origen"])
    sin_origen = set(destinos) - set(tabla["destino"])
    return sin_destino, sin_origen  # cada código de estas listas, explicado o corregido
```

Además: total de una extensiva conocida igual antes y después (`np.isclose`), y comparación con un total oficial del destino si existe (segunda vía). Si la diferencia con el oficial es grande, el peso no representa lo que se reparte.

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
| Repartir una tasa o una media con `w_ij` | Las intensivas no se suman | Numerador y denominador, o `v_ij` |
| Pesos por área en zonas con parques, polígonos o vías | Supone población uniforme | Auxiliar de población, viviendas o portales |
| Superponer en EPSG:4326 | Áreas en grados, distintas según la latitud | CRS métrico (EPSG:25830) |
| Límites de dos fuentes distintas | Astillas y orígenes partidos que no lo están | Umbral de astilla y renormalizar; mismo origen cartográfico si es posible |
| Unir años de seccionado por código | Un código puede cambiar de geometría | Superposición entre años |
| Auxiliar de otro año muy distinto | Los pesos describen otra población | Año de la auxiliar lo más cercano al dato, declarado |
