"""Simulación del criterio del Bono Alquiler Joven con transporte en casos tipo (#101, #301, ficha A §7.4).

Para cada perfil de `titulares.PERFILES` y cada municipio con alquiler, dice qué parte de sus ocupados sería
elegible con el criterio que aplica Madrid (`bono_vigente`) y con dos alternativas declaradas
(`alquiler_transporte` y `horas_viaje`), y si lo es el municipio (`elegible` = al menos el 50 % de sus ocupados).
Todo sale de `mesobra.calculo.calcular` (modo `tp`) hacia cada destino de zona de `tiempos.json`, con
`app/datos/tarifas.json` (generada el 2026-11-16, escenario `vigente_2026`: descuento del RDL 17/2025, que solo
vale en 2026; 227 días de trabajo al año). Salida: tabla `simulacion` (`contratos.py`). Es una simulación:
todas las filas van `estimado` y ser elegible no es cobrar (decisión 26).

Método de #301 (registro previo en `docs/decisiones.md`, 2026-11-19, fijado antes de ejecutar con los pesos). Se
evalúa cada par (zona de residencia z, destino d) y no la media del municipio: z es elegible para d si cumple edad,
ingresos y (alquiler(z) + T(z, d) + VTT × H(z, d)) ÷ neto ≥ `CORTE`; `alquiler_transporte` es igual con VTT = 0.
T es el transporte al mes del hogar y H las horas de viaje al mes de más frente a la zona ref(d) con menos minutos
hacia d: H = máx(0, horas(z, d) − horas(ref(d), d)), con las horas del propio `calcular`. pct(z) = Σ_d w(z, d) ·
1[elegible(z, d)] × 100 y el del municipio, la mediana de pct entre sus zonas. `bono_vigente` no depende del
destino: su pct es 100 o 0.

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
7. Cada parámetro va con su cita, arriba de este módulo (`parametros_2026.py` queda fuera de la issue).
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
13. Las alternativas sustituyen el tope y mantienen edad e ingresos; misma cuantía; son simulados e ilustrativos, no
    una propuesta. Lo que cambia frente a `bono_vigente` sale sobre todo de quitar el tope. En la pareja, la renta es
    la de una persona y el esfuerzo el del hogar: no se compara entre criterios.
14. Corte 45 % (`CORTE`): el índice H+T del CNT (vivienda + transporte ≤ 45 % de la renta del hogar = 30 % + 15 %;
    H+T Index Methods, nov. 2022, p. 4); referencia estadounidense, no norma. Es la revisión del 30 % de #296
    (`sobrecarga_30`, #100), que se fijó antes de ver resultados: con el 30 %, el término de horas bastaba para pasar
    el umbral en casi todos los municipios. El 45 % se eligió tras ver esos datos, así que el registro previo de
    #301 se escribió antes de ejecutar con los pesos y se publica la curva de cortes de 25 % a 50 %, con el 30 %
    marcado, y los criterios de #296 como sensibilidad (`simulacion_296`).
15. VTT = 0,325 × coste laboral total por hora de la Comunidad de Madrid (INE, ETCL4391, media de 2025T3–2026T2:
    30,0175 €/h) = 9,76 €/h; banda de la proporción 0,25 a 0,40 (7,50 a 12,01 €/h: CE CBA Guide 2014, p. 90, y
    Vademécum 2021-2027, p. 55; HEATCO, España 0,34 a 0,38). Madrid y no la media nacional (ETCL4443, 25,8225 €/h →
    8,39 €/h) porque el producto se ofrece en las condiciones de DataMad: con la nacional entran menos. Valorar el
    tiempo de viaje con una fracción del salario es un supuesto, no un dato.
16. Pesos w(z, d): matriz de residencia × trabajo del INE (`matriz_trabajo`, ocupados de 2023), destinos de la
    Comunidad con municipio conocido, renormalizados. «No consta» y fuera de la región se excluyen y se declara su
    masa por municipio (se marca si pasa del 25 %): se supone que quienes trabajan fuera o sin municipio conocido
    reparten igual su destino, y quien trabaja en otra provincia puede vivir en el borde (sin comprobar). Las celdas suprimidas (< 5) no
    se imputan: no se distinguen de los ceros y repartir 2,5 a cada par ausente daría a un municipio pequeño más
    ocupados que los reales; los pequeños destinos pierden peso y los grandes lo ganan. El lugar de trabajo puede ser
    la sede de la empresa y no el centro real (sin comprobar): sobrepesa a Madrid y sus distritos centrales.
17. Madrid como destino se reparte entre sus 21 distritos por los ocupados de 2023 del Colectivo Empresarial
    (`matriz_trabajo.leer_cuotas_distritos`, sin «no consta distrito»), igual para todos los orígenes: ignora que
    cada origen trabaja más cerca, e infla las horas de quien vive junto a pocos distritos (más elegibles). Madrid
    como origen usa la fila del municipio en sus 21 distritos: no distingue entre distritos de residencia.
18. Pares sin tiempo (null: más de 120 min o sin ruta) con w > 0: 120 min (`TP_IMPUTADO`), cota inferior provisional
    hasta #311; subestima horas y por tanto los elegibles. Como `calcular` da con ello transporte y horas, no hace
    falta código de tarifas aparte. Los pares con w = 0 se quedan sin tiempo.
19. ref(d) = la zona con menos minutos hacia d entre las que tienen tiempo; H mide el viaje de más frente a la
    mejor ubicada, que puede no ser asequible: sobreestima H si nadie puede vivir allí. H = 0 para la propia ref.
20. `elegible` del municipio = pct ≥ 50 % (`PCT_MINIMO`), la mayoría de sus ocupados; es un convenio de lectura, no
    de la norma. El municipio es la mediana de sus zonas, sin ponderar por población.
21. Sensibilidad: regla histórica de colocación adecuada del art. 301 LGSS (RDLeg 8/2015, redacción original; la
    sustituyó el 02-03-2023 la Ley 3/2023, que no fija criterios de desplazamiento): ida y vuelta mayor del 25 % de
    la jornada diaria (8 h) o coste del desplazamiento mayor del 20 % del salario mensual (bruto del primer sueldo
    ÷ 12; el coste de un solo trabajador, T ÷ n.º de sueldos). Va a la tabla de sensibilidades, no al contrato.
22. Transporte: modo `tp`, 2 viajes al día, tarifas `vigente_2026` (el descuento solo vale en 2026: favorece el
    transporte barato). El de 23 años usa el Abono Joven (hasta 25 años), tarifa plana por corona.
23. Horas trabajadas al mes = `semanas_mes` × 5 × 8 por sueldo (151,3 h; solo en `simulacion_296`). Pares sin alquiler
    quedan fuera; los municipios sin alquiler o sin pesos no tienen fila.
24. `perfil` = identificador por perfil y tipo de vivienda (`smi_30`, `smi_30_habitacion`...): choca con el enumerado
    de `api_estatica.PERFILES` (#103).
25. `estimado` = True siempre: el alquiler es una mediana estimada, no un contrato.
26. Ser elegible no es cobrar: la concesión va por orden de llegada hasta agotar el crédito. Sin personas ni coste.
"""

import logging
from decimal import Decimal as D
from typing import NamedTuple

import pandas as pd

from mesobra import (
    bono,
    calculo,
    contratos,
    matriz_trabajo,
    neto,
    parametros_2026,
    titulares,
)

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
CRITERIOS = ("bono_vigente", "alquiler_transporte", "horas_viaje")
CRITERIOS_296 = ("alquiler_transporte_296", "horas_viaje_296")
UMBRAL_296 = 0.30  # corte de `sobrecarga_30` (#100), el de #296
# Registro previo de #301 (docs/decisiones.md, 2026-11-19): INE, ETCL4391 (Comunidad de Madrid, coste laboral total
# por hora, media de 2025T3 a 2026T2) y ETCL4443 (nacional, mismo periodo).
COSTE_LABORAL_HORA_MADRID = 30.0175
COSTE_LABORAL_HORA_NACIONAL = 25.8225
# VTT como proporción del coste laboral: CE CBA Guide 2014 p. 90 y Vademécum 2021-2027 p. 55 (banda 0,25 a 0,40).
PROPORCION_COMMUTING = 0.325
BANDA_PROPORCION = (0.25, 0.40)
VTT = PROPORCION_COMMUTING * COSTE_LABORAL_HORA_MADRID  # €/h
BANDA_VTT = tuple(p * COSTE_LABORAL_HORA_MADRID for p in BANDA_PROPORCION)
VTT_NACIONAL = PROPORCION_COMMUTING * COSTE_LABORAL_HORA_NACIONAL
CORTE = 0.45  # índice H+T del CNT (30 % de vivienda + 15 % de transporte), H+T Index Methods, nov. 2022, p. 4
PCT_MINIMO = (
    50.0  # % de ocupados elegibles para que lo sea el municipio (registro previo)
)
TP_IMPUTADO = 120  # min, cota inferior provisional para los pares sin tiempo con flujo, hasta #311
MASA_EXCLUIDA_MAX = 0.25  # se marca a los municipios con más masa excluida
# Art. 301 LGSS, RDLeg 8/2015, redacción original: ida y vuelta > 25 % de la jornada diaria; coste > 20 % del salario.
LGSS_TIEMPO, LGSS_COSTE = 0.25, 0.20
IDS = ("smi_30", "teleoperador_23", "pareja_mediana", "madre_oficina", "joven_mediano")

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


def _carga(r: dict, criterio: str, vtt: float) -> float:
    """Esfuerzo que se compara con el corte: (renta + T [+ VTT × H]) ÷ neto; en #296, horas de viaje ÷ horas trabajadas."""
    carga = (r["renta"] + r["transporte"]) / r["neto"]
    if criterio == "horas_viaje":
        carga += vtt * r["horas_extra"] / r["neto"]
    elif criterio == "horas_viaje_296":
        carga += r["horas"] / r["horas_trab"]
    return carga


def _desplazamiento_largo(r: dict) -> bool:
    """Regla histórica del art. 301 LGSS: ida y vuelta > 25 % de la jornada o coste > 20 % del salario mensual."""
    viaje = 2 * r["minutos"] > LGSS_TIEMPO * titulares.HORAS_DIA * 60
    coste = r["transporte"] / r["n_sueldos"] > LGSS_COSTE * r["ingresos_bruto"] / 12
    return viaje or coste


def fallos(
    r: dict, criterio: str, ingresos: str, vtt: float, corte: float
) -> list[str]:
    """Requisitos que fallan en una fila de pares o de municipios con `criterio` (único sitio donde se decide).
    `vtt` en €/h (solo cuenta en `horas_viaje`) y `corte` como fracción del neto."""
    renta = D(str(r["renta"]))
    limite = tope(r["municipio_id"], r["tipo"]) if criterio == "bono_vigente" else None
    f = requisitos(r["edad"], D(str(r[ingresos])), renta, limite)
    if criterio == "lgss_2015":
        if not _desplazamiento_largo(r):
            f.append("desplazamiento corto (art. 301 LGSS, RDLeg 8/2015)")
    elif criterio != "bono_vigente" and _carga(r, criterio, vtt) < corte:
        f.append(f"esfuerzo < {corte} (criterio alternativo, {criterio})")
    return f


def variantes() -> list[tuple[str, dict, str, str]]:
    """(id, perfil, hogar, tipo): una por perfil, más la habitación de los que viven solos."""
    salida = []
    for pid, p in zip(IDS, titulares.PERFILES, strict=True):
        salida.append((pid, p, p["perfil"], "vivienda"))
        if p["perfil"] == "solo":
            salida.append((f"{pid}_habitacion", p, "comparte", "habitacion"))
    return salida


def imputar_tiempos(api: dict, w: pd.DataFrame) -> tuple[dict, set[tuple[str, str]]]:
    """Copia de `api` con `TP_IMPUTADO` minutos en los pares (zona, destino) con w > 0 y `tp` nulo, y esos pares."""
    t = api["tiempos"]
    destinos = [d["destino_id"] for d in t["destinos"]]
    if faltan := set(w["destino"]) - set(destinos):
        raise ValueError(
            f"destinos con peso que no están en tiempos.json: {sorted(faltan)[:5]}"
        )
    zona_mun = {
        f["properties"]["zona_id"]: f["properties"]["municipio_id"]
        for f in api["zonas"]["features"]
    }
    flujo = w.groupby("origen")["destino"].agg(set)
    tp, imputados = [list(fila) for fila in t["tp"]], set()
    for i, z in enumerate(t["origenes"]):
        for j, d in enumerate(destinos):
            if tp[i][j] is None and d in flujo.get(zona_mun[z], ()):
                tp[i][j] = TP_IMPUTADO
                imputados.add((z, d))
    return api | {"tiempos": t | {"tp": tp}}, imputados


def tabla_pares(
    api: dict, w: pd.DataFrame, imputados: set[tuple[str, str]]
) -> pd.DataFrame:
    """Una fila por (variante, zona con alquiler, destino de zona) con alquiler, transporte, neto, horas, minutos,
    `horas_extra` (H), `imputado` y el peso `w` (0 si el municipio no tiene flujo a ese destino). `api` es la de
    `imputar_tiempos`. Falla si un par con w > 0 queda sin transporte u horas."""
    zona_mun = {
        f["properties"]["zona_id"]: f["properties"]["municipio_id"]
        for f in api["zonas"]["features"]
    }
    t = api["tiempos"]
    destinos = [
        (j, d["destino_id"]) for j, d in enumerate(t["destinos"]) if d["tipo"] == "zona"
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
            "n_sueldos": len(p["sueldos"]),
            # la pareja de 29: cada una firma y cumple sola (Acuerdo, art. 4.1.d); habitación: una
            "beneficiarios": len(p["sueldos"]) if tipo == "vivienda" else 1,
        }
        for j, d in destinos:
            entrada = {
                "hogar": {"perfil": hogar, "edad": p["edad"]},
                "sueldos": [
                    {"destino": d, "dias": dias, "modo": "tp", "bruto": bruto}
                    for bruto, dias in p["sueldos"]
                ],
            }
            zonas = calculo.calcular(api, entrada)["zonas"]
            con_tiempo = [
                (t["tp"][i][j], z)
                for i, z in enumerate(t["origenes"])
                if t["tp"][i][j] is not None
            ]
            ref = zonas[min(con_tiempo)[1]]["horas"] if con_tiempo else None
            for i, (zona, z) in enumerate(zonas.items()):
                if z["alquiler"] is None:
                    continue
                h = z["horas"]
                filas.append(
                    fijos
                    | {
                        "zona_id": zona,
                        "municipio_id": zona_mun[zona],
                        "destino": d,
                        "minutos": t["tp"][i][j],
                        "alquiler": z["alquiler"],
                        "alquiler_p75": z["alquiler_p75"],
                        "transporte": z["transporte"],
                        "neto": z["neto"],
                        "horas": h,
                        "horas_extra": None if None in (h, ref) else max(0.0, h - ref),
                        "imputado": (zona, d) in imputados,
                    }
                )
    df = pd.DataFrame(filas).merge(
        w.rename(columns={"origen": "municipio_id"}),
        on=["municipio_id", "destino"],
        how="left",
    )
    df["w"] = df["w"].fillna(0.0)
    incompletos = df[
        (df["w"] > 0) & df[["transporte", "horas", "horas_extra"]].isna().any(axis=1)
    ]
    if not incompletos.empty:
        raise ValueError(f"{len(incompletos)} pares con peso sin transporte u horas")
    LOG.info(
        "pares: %d; con peso: %d; imputados a %d min: %d",
        len(df), (df["w"] > 0).sum(), TP_IMPUTADO, df["imputado"].sum(),
    )  # fmt: skip
    return df


MEDIDAS = ("alquiler", "alquiler_p75", "transporte", "horas")
FIJAS = (
    "perfil", "tipo", "edad", "ingresos_base", "ingresos_bruto", "ingresos_hogar", "horas_trab", "n_sueldos",
    "beneficiarios", "neto", "zona_id", "municipio_id",
)  # fmt: skip


def tabla_zonas(pares: pd.DataFrame) -> pd.DataFrame:
    """Como #296: una fila por (variante, zona) con la mediana entre destinos de zona, sin ponderar y sin los
    pares imputados."""
    completas = pares[~pares["imputado"]].dropna(subset=list(MEDIDAS))
    return completas.groupby(list(FIJAS), as_index=False)[list(MEDIDAS)].median()


def _municipios(zonas: pd.DataFrame, medidas: tuple[str, ...]) -> pd.DataFrame:
    """Mediana de sus zonas por (perfil, municipio)."""
    # las columnas fijas en la clave: si no fueran constantes, saldrían claves repetidas y `validar` fallaría
    claves = [c for c in zonas.columns if c not in MEDIDAS and c != "zona_id"]
    return zonas.groupby(claves, as_index=False)[list(medidas)].median()


class Escenario(NamedTuple):
    """Cómo se mide: ingresos (`base`, `bruto` u `hogar`), columna de alquiler, VTT en €/h y corte (fracción)."""

    ingresos: str = "base"
    alquiler: str = "alquiler"
    vtt: float = VTT
    corte: float = CORTE


def _ok(t: pd.DataFrame, criterio: str, e: Escenario) -> list[bool]:
    return [
        not fallos(r, criterio, f"ingresos_{e.ingresos}", e.vtt, e.corte)
        for r in t.assign(renta=t[e.alquiler]).to_dict("records")
    ]


def _pct_municipios(
    pares: pd.DataFrame, mun: pd.DataFrame, criterio: str, e: Escenario
) -> list[float]:
    """% de ocupados elegibles de cada fila de `mun`: la mediana de sus zonas, cada una Σ_d w · 1[elegible]."""
    if criterio == "bono_vigente":
        return [100.0 * ok for ok in _ok(mun, criterio, e)]
    p = pares[pares["w"] > 0]
    por = [p["perfil"], p["municipio_id"], p["zona_id"]]
    zona = (p["w"] * _ok(p, criterio, e)).groupby(por).sum() / p["w"].groupby(por).sum()
    pct = 100 * zona.groupby(level=["perfil", "municipio_id"]).median()
    return pct.loc[pd.MultiIndex.from_frame(mun[["perfil", "municipio_id"]])].tolist()


def _filas(
    mun: pd.DataFrame, criterio: str, pct: list[float], e: Escenario
) -> list[tuple]:
    filas = []
    for r, p in zip(mun.to_dict("records"), pct, strict=True):
        ok = p >= PCT_MINIMO
        eur = (
            float(min(CUANTIA * r["beneficiarios"], D(str(r[e.alquiler]))))
            if ok
            else 0.0
        )
        filas.append((r["perfil"], r["municipio_id"], criterio, ok, eur, True, p))
    return filas


def _tabla(filas: list[tuple]) -> pd.DataFrame:
    df = pd.DataFrame(
        filas, columns=list(contratos.CONTRATOS["simulacion"]["columnas"])
    )
    contratos.validar(df, "simulacion")
    return df


def simulacion(
    pares: pd.DataFrame,
    criterios: tuple[str, ...] = CRITERIOS,
    **escenario: str | float,
) -> pd.DataFrame:
    """Tabla `simulacion` por (perfil, municipio, criterio), validada. `escenario`: los campos de `Escenario`."""
    e = Escenario(**escenario)
    con_peso = pares[pares["w"] > 0]["municipio_id"].unique()
    zonas = pares.drop_duplicates(["perfil", "zona_id"])[
        [*FIJAS, "alquiler", "alquiler_p75"]
    ]
    mun = _municipios(
        zonas[zonas["municipio_id"].isin(con_peso)], ("alquiler", "alquiler_p75")
    )
    return _tabla(
        [
            f
            for c in criterios
            for f in _filas(mun, c, _pct_municipios(pares, mun, c, e), e)
        ]
    )


def simulacion_296(zonas: pd.DataFrame) -> pd.DataFrame:
    """Sensibilidad: los criterios de #296 (corte del 30 %, mediana de los destinos sin ponderar) sobre `tabla_zonas`.
    El pct es 100 o 0: no hay ocupados."""
    e = Escenario(corte=UMBRAL_296)
    mun = _municipios(zonas, MEDIDAS)
    return _tabla(
        [
            f
            for c in ("bono_vigente", *CRITERIOS_296)
            for f in _filas(mun, c, [100.0 * ok for ok in _ok(mun, c, e)], e)
        ]
    )


def cambios(df: pd.DataFrame) -> pd.DataFrame:
    """Por perfil y criterio: municipios elegibles, pct mediano de ocupados elegibles y municipios que entran y que
    salen frente a `bono_vigente`."""
    ok = df.pivot(
        index=["perfil", "municipio_id"], columns="criterio", values="elegible"
    ).astype(bool)
    pct = df.groupby(["perfil", "criterio"])["pct_ocupados_elegibles"].median()
    filas = []
    for perfil, g in ok.groupby(level="perfil"):
        for c in g.columns:
            filas.append(
                {
                    "perfil": perfil,
                    "criterio": c,
                    "elegibles": int(g[c].sum()),
                    "pct_mediano": float(pct[(perfil, c)]),
                    "entran": int((~g["bono_vigente"] & g[c]).sum()),
                    "salen": int((g["bono_vigente"] & ~g[c]).sum()),
                }
            )
    return pd.DataFrame(filas)


def curva(pares: pd.DataFrame) -> pd.DataFrame:
    """Municipios elegibles por perfil y criterio con cada corte de 25 % a 50 % (columnas: el corte)."""
    cortes = [round(0.25 + 0.05 * i, 2) for i in range(6)]
    cols = [
        simulacion(pares, ("alquiler_transporte", "horas_viaje"), corte=c)
        .groupby(["criterio", "perfil"])["elegible"]
        .sum()
        .rename(c)
        for c in cortes
    ]
    return pd.concat(cols, axis=1)


def _imputacion(pares: pd.DataFrame) -> pd.DataFrame:
    """Por municipio de residencia: pares (zona, destino) imputados y masa de w imputada (media de sus zonas)."""
    una = pares[pares["perfil"] == pares["perfil"].iloc[0]]
    i = una[una["imputado"]]
    zonas = i.groupby(["municipio_id", "zona_id"]).agg(
        pares=("w", "size"), masa=("w", "sum")
    )
    return zonas.groupby(level="municipio_id").agg(
        pares=("pares", "sum"), masa=("masa", "mean")
    )


def _log_tabla(titulo: str, t: pd.DataFrame) -> None:
    LOG.info("%s:\n%s", titulo, t.round(3).to_string())


def main() -> None:
    logging.basicConfig(level=logging.INFO)
    api = calculo.leer_api(calculo.RAIZ / "app/datos")
    nombres = {
        f["properties"]["municipio_id"]: f["properties"]["nombre"]
        for f in api["zonas"]["features"]
        if f["properties"]["tipo"] == "municipio"
    } | {"28079": "Madrid"}
    w, excluida = matriz_trabajo.pesos(
        matriz_trabajo.leer_matriz(), matriz_trabajo.leer_cuotas_distritos()
    )
    api_imp, imputados = imputar_tiempos(api, w)
    pares = tabla_pares(api_imp, w, imputados)
    df = simulacion(pares)
    PROCESSED.mkdir(parents=True, exist_ok=True)
    df.to_csv(PROCESSED / "simulacion.csv", index=False)
    LOG.info("simulacion.csv: %d filas", len(df))
    sin_fila = set(nombres) - set(df["municipio_id"])
    LOG.info(
        "municipios sin fila (sin alquiler, sin pesos o sin ruta): %d", len(sin_fila)
    )
    alta = excluida[excluida > MASA_EXCLUIDA_MAX]
    LOG.info(
        "masa excluida (otras provincias o «No consta») > %d %%: %s",
        100 * MASA_EXCLUIDA_MAX,
        {nombres.get(m, m): round(float(x), 3) for m, x in alta.items()},
    )
    _log_tabla("masa excluida por municipio", excluida.describe())
    imp = _imputacion(pares)
    LOG.info(
        "imputados a %d min: %d pares; masa de w por municipio de residencia (media %.4f, máx. %.4f); los 10 mayores:\n%s",
        TP_IMPUTADO, imp["pares"].sum(), imp["masa"].mean(), imp["masa"].max(),
        imp.sort_values("masa", ascending=False).head(10).rename(index=nombres).round(4).to_string(),
    )  # fmt: skip
    _log_tabla(
        "base (corte 0,45, VTT 9,76)", cambios(df).set_index(["perfil", "criterio"])
    )
    _log_tabla("curva de cortes: municipios elegibles", curva(pares))
    sensibilidades = {
        "VTT 7,50": simulacion(pares, vtt=BANDA_VTT[0]),
        "VTT 12,01": simulacion(pares, vtt=BANDA_VTT[1]),
        "VTT nacional": simulacion(pares, vtt=VTT_NACIONAL),
        "LGSS 2015": simulacion(pares, ("bono_vigente", "lgss_2015")),
        "criterios de #296": simulacion_296(tabla_zonas(pares)),
        "ingresos = bruto": simulacion(pares, ingresos="bruto"),
        "regla del RD (suma del hogar)": simulacion(pares, ingresos="hogar"),
        "alquiler P75": simulacion(pares, alquiler="alquiler_p75"),
    }
    for nombre, s in sensibilidades.items():
        _log_tabla(
            f"sensibilidad {nombre}", cambios(s).set_index(["perfil", "criterio"])
        )


if __name__ == "__main__":
    main()
