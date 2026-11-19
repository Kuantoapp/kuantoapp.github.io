"""Simulación del criterio del Bono Alquiler Joven con transporte en casos tipo (#101, ficha A §7.4).

Para cada perfil de `titulares.PERFILES` y cada municipio con alquiler, dice si sería elegible con el criterio
que aplica Madrid (`bono_vigente`) y con dos alternativas declaradas (`alquiler_transporte` y `horas_viaje`).
Todo sale de `mesobra.calculo.calcular` (modo `tp`) hacia cada destino de zona de `tiempos.json`, con
`app/datos/tarifas.json` (generada el 2026-11-16, escenario `vigente_2026`: descuento del RDL 17/2025, que solo
vale en 2026; 227 días de trabajo al año). Salida: tabla `simulacion` (`contratos.py`). Es una simulación:
todas las filas van `estimado` y ser elegible no es cobrar (decisión 18).

Decisiones y sentido de su sesgo:
1. Criterio vigente: RD 42/2022 en la ronda «2024» de Madrid (BOCM-20250110-20, FAQ 2024). Sigue en tramitación
   (BOCM-20260922-16); sin convocatoria del RD 326/2026 en Madrid. Texto completo del Acuerdo en BDNS 805618, doc. 1505247.
2. IPREM «referido a 14 pagas» (Acuerdo, art. 4.4): 8.400 € (DA 90.ª.d Ley 31/2022, BOE-A-2022-22128, fijado «durante
   2023»; sin cambios en el consolidado del 18-11-2026 y prorrogado: RDL 9/2024, RDL 1/2025 y RDL 3/2026, preámbulos).
   El art. 4.4 pide el IPREM del ejercicio de los ingresos (2024 o 2025): el mismo valor. Umbral 3 × IPREM = 25.200 €,
   «iguales o inferiores».
3. Edad de 18 a 35 años incluidos (RD 42/2022, art. 6.1.a, BOE-A-2022-802). Los 5 perfiles (23 a 34) cumplen: sin efecto.
4. Topes (art. 8; Acuerdo CG 26-12-2024, art. 5 y Anexo II, leído en bruto): vivienda 600 € (900 € en 55 municipios) y
   habitación 300 € (450 €), «hasta». `TOPE_900_2024` = `bono.TOPE_900` (ronda 2022) + 26 municipios nuevos.
5. Cuantía: min(250 € × personas beneficiarias, renta) (RD art. 11; Acuerdo, arts. 4.1.d y 8.1): en la pareja de 29
   las dos pueden ser beneficiarias (mismo sueldo, cada una cumple sola); en los demás, una. Sin límites de duración.
6. Se supone que cada perfil cumple el resto de requisitos (fuente regular de ingresos, sin exclusiones del art. 6.2)
   y que garaje, trastero y gastos van en la renta del SERPAVI, sin la valoración del 80, 95 o 75 % de la FAQ p. 12:
   sobreestima los elegibles.
7. Cada parámetro va en `Decimal` con su cita, arriba de este módulo (`parametros_2026.py` queda fuera de la issue).
8. «Ingresos» = base imponible general (supuesto de la referencia §5): bruto − cotización − 2.000 € (art. 19.2.f) −
   reducción del art. 20, como `neto.cuota_irpf`. La norma no fija la medida («rentas anuales», «información del
   IRPF»; Acuerdo, arts. 4.1.d y 4.4) y decide a la pareja y a la madre: con la base (24.215 y 24.427 €) entran; con el
   bruto (28.038 y 28.264 €), no. Se presentan siempre con la sensibilidad `ingresos="bruto"`.
9. Cuentan solo los ingresos de la persona solicitante, el primer sueldo: Acuerdo, art. 4.1.d, si conviven jóvenes sin
   parentesco de 1.er grado o todos de hasta 35 años y firma el contrato (la pareja de 29); la madre suma su hijo, sin
   ingresos; en habitación, solo la persona arrendataria. El RD suma los de los convivientes: con esa regla la pareja
   queda fuera (sensibilidad `hogar`).
10. Se usa el bruto de referencia del perfil (de 2024 a 2026) y no el del ejercicio que mira la convocatoria: cuanto
    más antiguo es el sueldo real, más bajo sería y más perfiles entrarían. La cotización y el art. 20 son los de 2026:
    en la pareja y la madre el art. 20 es 0 y la diferencia es de pocos euros frente a un margen de 773 a 985 €.
11. Vivienda de 69 m² para los 5 perfiles; los 3 «solo» se repiten como habitación con el hogar `comparte` (alquiler
    repartido entre `personas_comparten`), aproximación a la renta de una habitación. 69 m² sobreestima la renta de
    quien vive solo: menos entran por el tope. La habitación (un tercio del piso) es una cota inferior de su renta.
12. Alquiler P50 del SERPAVI con `factor_ipc`: suelo del precio (parque de contratos, no oferta nueva); más entran
    por el tope y menos por esfuerzo (sensibilidad con el P75).
13. Las alternativas sustituyen el tope y mantienen edad e ingresos. `alquiler_transporte`: (alquiler + transporte) ÷
    neto ≥ 30 %; `horas_viaje`: ese esfuerzo + horas de viaje ÷ horas trabajadas ≥ 30 % (valora la hora de viaje al
    neto por hora). El 30 % es el corte de `sobrecarga_30` (#100), fijado antes de ejecutar con datos reales; el 40 %
    va como sensibilidad. Misma cuantía; son simulados e ilustrativos, no una propuesta. Lo que cambia frente a
    `bono_vigente` sale sobre todo de quitar el tope; `cambios` separa los municipios que cruzan el umbral solo al
    sumar el transporte (`por_transporte`). Con el 30 %, el término de horas (mediana a un destino cualquiera de la
    región, no al trabajo de nadie) basta para pasar el umbral en casi todos: `horas_viaje` es un criterio de lejanía.
    En la pareja, la renta es la de una persona y el esfuerzo el del hogar: no se compara entre criterios.
14. Transporte: modo `tp`, 2 viajes al día, tarifas `vigente_2026` (el descuento solo vale en 2026: favorece el
    transporte barato). El de 23 años usa el Abono Joven (hasta 25 años), tarifa plana por corona.
15. Municipio = mediana de sus zonas, y cada zona = mediana entre destinos de zona (los polos fuera, como en
    `titulares`), sin ponderar por empleo ni población. Horas trabajadas al mes = `semanas_mes` × 5 × 8 por sueldo
    (151,3 h). Pares sin ruta o sin alquiler quedan fuera; los municipios sin alquiler no tienen fila.
16. `perfil` = identificador por perfil y tipo de vivienda (`smi_30`, `smi_30_habitacion`...): choca con el enumerado
    de `api_estatica.PERFILES` (#103).
17. `estimado` = True siempre: el alquiler es una mediana estimada, no un contrato.
18. Ser elegible no es cobrar: la concesión va por orden de llegada hasta agotar el crédito. Sin personas ni coste.
"""

import logging
from decimal import Decimal as D

import pandas as pd

from mesobra import bono, calculo, contratos, neto, parametros_2026, titulares

LOG = logging.getLogger(__name__)
PROCESSED = calculo.RAIZ / "data/processed"

# DA 90.ª.d Ley 31/2022 (BOE-A-2022-22128), prorrogada (RDL 3/2026); 14 pagas por el Acuerdo, art. 4.4.
IPREM = D(8400)
# RD 42/2022, art. 6.1.d (BOE-A-2022-802); Acuerdo, art. 4.1.d: ingresos iguales o inferiores a 3 × IPREM.
UMBRAL_INGRESOS = 3 * IPREM
# RD 42/2022, art. 6.1.a: de 18 a 35 años, ambos incluidos.
EDAD_MIN, EDAD_MAX = 18, 35
# RD 42/2022, art. 11; Acuerdo, art. 8.1: 250 €/mes por persona beneficiaria, sin pasar de la renta.
CUANTIA = D(250)
# RD 42/2022, art. 8; Acuerdo CG 26-12-2024 (BOCM-20250110-20), Anexo II: (tope general, tope en TOPE_900_2024).
TOPES = {"vivienda": (D(600), D(900)), "habitacion": (D(300), D(450))}
UMBRAL = D("0.30")  # corte de `sobrecarga_30` (#100)
CRITERIOS = ("bono_vigente", "alquiler_transporte", "horas_viaje")
IDS = ("smi_30", "teleoperador_23", "pareja_mediana", "madre_oficina", "joven_mediano")
MADRID = "28079"

# Acuerdo CG 26-12-2024, Anexo II: 55 municipios (texto completo en BDNS 805618, doc. 1505247, «Certificado ACG»,
# leído el 2026-11-19; la FAQ 2024 p. 12 da los mismos 55; la ficha de la sede, 54, sin Moraleja de Enmedio).
TOPE_900_2024 = bono.TOPE_900 | {
    "28002": "Ajalvir",
    "28010": "Alpedrete",
    "28013": "Aranjuez",
    "28014": "Arganda del Rey",
    "28023": "Boalo, El",
    "28026": "Brunete",
    "28032": "Camarma de Esteruelas",
    "28040": "Ciempozuelos",
    "28041": "Cobeña",
    "28045": "Colmenar Viejo",
    "28044": "Colmenarejo",
    "28053": "Daganzo de Arriba",
    "28054": "Escorial, El",
    "28059": "Fuente el Saz de Jarama",
    "28068": "Guadarrama",
    "28073": "Humanes de Madrid",
    "28084": "Mejorada del Campo",
    "28089": "Moraleja de Enmedio",
    "28090": "Moralzarzal",
    "28096": "Navalcarnero",
    "28104": "Paracuellos de Jarama",
    "28129": "San Agustín del Guadalix",
    "28131": "San Lorenzo de El Escorial",
    "28132": "San Martín de la Vega",
    "28144": "Soto del Real",
    "28167": "Velilla de San Antonio",
}
# Anexo II del Acuerdo, transcripción literal (con sus erratas «Carmarma» y «Paracuellos del Jarama»).
NOMBRES_ANEXO_II = [
    "Ajalvir",
    "Alcalá de Henares",
    "Alcobendas",
    "Alcorcón",
    "Algete",
    "Alpedrete",
    "Aranjuez",
    "Arganda del Rey",
    "Arroyomolinos",
    "Boadilla del Monte",
    "Boalo, El",
    "Brunete",
    "Carmarma de Esteruelas",
    "Ciempozuelos",
    "Cobeña",
    "Collado Villalba",
    "Colmenar Viejo",
    "Colmenarejo",
    "Coslada",
    "Daganzo de Arriba",
    "Escorial, El",
    "Fuenlabrada",
    "Fuente el Saz de Jarama",
    "Galapagar",
    "Getafe",
    "Guadarrama",
    "Humanes de Madrid",
    "Leganés",
    "Madrid",
    "Majadahonda",
    "Mejorada del Campo",
    "Moraleja de Enmedio",
    "Moralzarzal",
    "Móstoles",
    "Navalcarnero",
    "Paracuellos del Jarama",
    "Parla",
    "Pinto",
    "Pozuelo de Alarcón",
    "Rivas-Vaciamadrid",
    "Rozas de Madrid, Las",
    "San Agustín del Guadalix",
    "San Fernando de Henares",
    "San Lorenzo de El Escorial",
    "San Martín de la Vega",
    "San Sebastián de los Reyes",
    "Soto del Real",
    "Torrejón de Ardoz",
    "Torrelodones",
    "Tres Cantos",
    "Valdemoro",
    "Velilla de San Antonio",
    "Villanueva de la Cañada",
    "Villanueva del Pardillo",
    "Villaviciosa de Odón",
]


def base_imponible(bruto: float | D) -> D:
    """Base imponible general: bruto − cotización − 2.000 € − reducción del art. 20 (como `neto.cuota_irpf`)."""
    # shortcut: duplica neto.py:86-87 (la issue no deja tocar neto); extraer a neto cuando se pueda tocar.
    bruto = D(str(bruto))
    rnt = max(bruto - neto.cotizacion(bruto), D(0))
    gastos = min(parametros_2026.GASTOS_OTROS, rnt)
    return max(rnt - gastos - neto._reduccion_art20(rnt), D(0))


def tope(municipio_id: str, tipo: str) -> D:
    """Renta máxima subvencionable: `tipo` es `vivienda` o `habitacion`."""
    return TOPES[tipo][municipio_id in TOPE_900_2024]


def requisitos(edad: int, ingresos: D, renta: D, maximo: D | None) -> list[str]:
    """Requisitos que fallan con su artículo; vacía = cumple. `maximo` None = sin tope (criterios alternativos)."""
    f = []
    if not EDAD_MIN <= edad <= EDAD_MAX:
        f.append("edad (RD 42/2022, art. 6.1.a)")
    if ingresos > UMBRAL_INGRESOS:
        f.append("ingresos > 3 × IPREM (RD art. 6.1.d; Acuerdo, art. 4.1.d)")
    if maximo is not None and renta > maximo:
        f.append("renta > tope (RD art. 8; Acuerdo, art. 5 y Anexo II)")
    return f


def fallos(r: dict, criterio: str, ingresos: str, umbral: D) -> list[str]:
    """Requisitos que fallan en una fila de `_municipios` con `criterio` (único sitio donde se decide)."""
    renta = D(str(r["renta"]))
    limite = tope(r["municipio_id"], r["tipo"]) if criterio == "bono_vigente" else None
    f = requisitos(r["edad"], D(str(r[ingresos])), renta, limite)
    if criterio != "bono_vigente":
        carga = (r["renta"] + r["transporte"]) / r["neto"]
        if criterio == "horas_viaje":
            carga += r["horas"] / r["horas_trab"]
        if carga < float(umbral):
            f.append(f"esfuerzo < {umbral} (criterio alternativo, {criterio})")
    return f


def variantes() -> list[tuple[str, dict, str, str]]:
    """(id, perfil, hogar, tipo): una por perfil, más la habitación de los que viven solos."""
    salida = []
    for pid, p in zip(IDS, titulares.PERFILES, strict=True):
        salida.append((pid, p, p["perfil"], "vivienda"))
        if p["perfil"] == "solo":
            salida.append((f"{pid}_habitacion", p, "comparte", "habitacion"))
    return salida


def tabla_zonas(api: dict) -> pd.DataFrame:
    """Una fila por (variante, zona) con alquiler, transporte, neto y horas (mediana entre destinos de zona)."""
    zona_mun = {
        f["properties"]["zona_id"]: f["properties"]["municipio_id"]
        for f in api["zonas"]["features"]
    }
    destinos = [
        d["destino_id"] for d in api["tiempos"]["destinos"] if d["tipo"] == "zona"
    ]
    horas_mes = (
        api["tarifas"]["semanas_mes"] * titulares.DIAS_SEMANA * titulares.HORAS_DIA
    )
    filas = []
    for pid, p, hogar, tipo in variantes():
        # ingresos de quien solicita (decisión 9), de todo el hogar (sensibilidad) y bruto (sensibilidad)
        bases = [float(base_imponible(b)) for b, _ in p["sueldos"]]
        fijos = {
            "perfil": pid,
            "tipo": tipo,
            "edad": p["edad"],
            "ingresos_base": bases[0],
            "ingresos_bruto": p["sueldos"][0][0],
            "ingresos_hogar": sum(bases),
            "horas_trab": horas_mes * len(p["sueldos"]),
            # la pareja de 29: cada una firma y cumple sola (Acuerdo, art. 4.1.d); habitación: una
            "beneficiarios": len(p["sueldos"]) if tipo == "vivienda" else 1,
        }
        for d in destinos:
            entrada = {
                "hogar": {"perfil": hogar, "edad": p["edad"]},
                "sueldos": [
                    {"destino": d, "dias": dias, "modo": "tp", "bruto": bruto}
                    for bruto, dias in p["sueldos"]
                ],
            }
            for zona, z in calculo.calcular(api, entrada)["zonas"].items():
                filas.append(
                    fijos
                    | {
                        "zona_id": zona,
                        "municipio_id": zona_mun[zona],
                        "alquiler": z["alquiler"],
                        "alquiler_p75": z["alquiler_p75"],
                        "transporte": z["transporte"],
                        "neto": z["neto"],
                        "horas": z["horas"],
                    }
                )
    df = pd.DataFrame(filas)
    medidas = ["alquiler", "alquiler_p75", "transporte", "horas"]
    completas = df.dropna(subset=medidas)
    LOG.info(
        "pares completos: %d de %d (sin alquiler: %d; sin ruta: %d)",
        len(completas),
        len(df),
        df["alquiler"].isna().sum(),
        df["transporte"].isna().sum(),
    )
    fijas = [c for c in df.columns if c not in medidas and c != "zona_id"]
    return completas.groupby(["zona_id", *fijas], as_index=False)[medidas].median()


def _municipios(zonas: pd.DataFrame) -> pd.DataFrame:
    """Mediana de sus zonas por (perfil, municipio)."""
    medidas = ["alquiler", "alquiler_p75", "transporte", "horas"]
    # las columnas fijas en la clave: si no fueran constantes, saldrían claves repetidas y `validar` fallaría
    claves = [c for c in zonas.columns if c not in medidas and c != "zona_id"]
    return zonas.groupby(claves, as_index=False)[medidas].median()


def _evaluar(
    t: pd.DataFrame,
    ingresos: str = "base",
    alquiler: str = "alquiler",
    umbral: D = UMBRAL,
) -> pd.DataFrame:
    """Contrato `simulacion` para cada fila de `t` (zonas o municipios) y cada criterio."""
    filas = []
    for r in t.assign(renta=t[alquiler]).to_dict("records"):
        for c in CRITERIOS:
            ok = not fallos(r, c, f"ingresos_{ingresos}", umbral)
            maximo = CUANTIA * r["beneficiarios"]
            eur = float(min(maximo, D(str(r["renta"])))) if ok else 0.0
            filas.append((r["perfil"], r["municipio_id"], c, ok, eur, True))
    return pd.DataFrame(
        filas, columns=list(contratos.CONTRATOS["simulacion"]["columnas"])
    )


def simulacion(zonas: pd.DataFrame, **escenario: str | D) -> pd.DataFrame:
    """Tabla `simulacion` por (perfil, municipio, criterio), validada. `escenario`: los de `_evaluar`."""
    df = _evaluar(_municipios(zonas), **escenario)
    contratos.validar(df, "simulacion")
    return df


def cambios(zonas: pd.DataFrame, **escenario: str | D) -> pd.DataFrame:
    """Por perfil y criterio: elegibles, municipios que entran y que salen frente a `bono_vigente`, los que entran
    solo al sumar el transporte (`por_transporte`: fuera con transporte 0) y % de zonas elegibles en Madrid
    (21 distritos). `escenario`: los de `_evaluar`."""

    def tabla(z: pd.DataFrame) -> pd.DataFrame:
        return simulacion(z, **escenario).pivot(
            index=["perfil", "municipio_id"], columns="criterio", values="elegible"
        )

    ok, sin_tr = tabla(zonas), tabla(zonas.assign(transporte=0.0))
    mad = _evaluar(zonas[zonas["municipio_id"] == MADRID], **escenario)
    pct = 100 * mad.groupby(["perfil", "criterio"])["elegible"].mean()
    filas = []
    for perfil, g in ok.groupby(level="perfil"):
        g0 = sin_tr.loc[g.index]
        for c in CRITERIOS:
            filas.append(
                {
                    "perfil": perfil,
                    "criterio": c,
                    "vigente": int(g["bono_vigente"].sum()),
                    "elegibles": int(g[c].sum()),
                    "entran": int((~g["bono_vigente"] & g[c]).sum()),
                    "salen": int((g["bono_vigente"] & ~g[c]).sum()),
                    "por_transporte": int((g[c] & ~g0[c]).sum()),
                    "pct_zonas_madrid": float(pct.get((perfil, c), float("nan"))),
                }
            )
    return pd.DataFrame(filas)


def main() -> None:
    logging.basicConfig(level=logging.INFO)
    api = calculo.leer_api(calculo.RAIZ / "app/datos")
    zonas = tabla_zonas(api)
    sin_alquiler = {
        f["properties"]["municipio_id"] for f in api["zonas"]["features"]
    } - set(zonas["municipio_id"])
    LOG.info("municipios sin fila (sin alquiler o sin ruta): %d", len(sin_alquiler))
    df = simulacion(zonas)
    PROCESSED.mkdir(parents=True, exist_ok=True)
    df.to_csv(PROCESSED / "simulacion.csv", index=False)
    LOG.info("simulacion.csv: %d filas", len(df))
    escenarios = {
        "base": {},
        "ingresos = bruto": {"ingresos": "bruto"},
        "regla del RD (suma del hogar)": {"ingresos": "hogar"},
        "alquiler P75": {"alquiler": "alquiler_p75"},
        "umbral 0,40": {"umbral": D("0.40")},
    }
    for nombre, esc in escenarios.items():
        LOG.info(
            "escenario %s:\n%s", nombre, cambios(zonas, **esc).to_string(index=False)
        )


if __name__ == "__main__":
    main()
