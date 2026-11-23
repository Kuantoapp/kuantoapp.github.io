"""Titulares con sueldos de referencia (#93): las dos tesis de la ficha A §8 para perfiles tipo.

Tesis 1: el ahorro de vivir lejos paga la hora de viaje por debajo del neto por hora trabajada.
Tesis 2: con sueldos típicos, en muchas zonas no sobra nada. Todo sale de `mesobra.calculo.calcular`
(modo `tp`) hacia cada destino de `tiempos.json`; aquí solo se agrupa. Veredicto de la tesis 1:
«tesis» si ninguna corona de origen tiene mediana del precio de la hora ≥ neto/hora, si no «plan B»
(regla fijada antes de ver los datos). La tesis 2 se da con la cifra, sin umbral.

Supuestos y sentido de su sesgo (cada perfil lleva la `fuente` de su sueldo):
1. Horas trabajadas al mes = `semanas_mes` × 5 × horas del perfil (8 h, jornada de 40 h del ET art. 34.1,
   BOE-A-2015-11430; la enfermera, 37,5 h): 151,3 h/mes efectivas para los de 8 h (227 días × 8 h ÷ 12). Con las horas pagadas (40 × 52 ÷ 12 =
   173,3) el neto/hora bajaría un 13 % (SMI: 7,68 € en vez de 8,80 €) y más pares lo alcanzarían, en
   contra de la tesis 1 (SMI: 1.544 pares, 14,9 %, frente a 1.316, 12,7 %), sin cambiar el veredicto;
   con jornada real menor (parcial, convenio) sube, a favor de la tesis 1. La ganancia de la EAES
   (y de la EES) incluye el tiempo parcial y aquí se divide por jornada completa: neto/hora más bajo,
   en contra, y bruto de jornada completa infravalorado, más zonas negativas (a favor de la tesis 2).
   La enfermera tiene su jornada: 37,5 h semanales, mínimo de promedio que fija la Ley 6/2011 de la Comunidad de Madrid («no inferior a 37 h 30 min»,
   DA 1.ª.1, BOE-A-2012-2980, vigente; verificado el 2026-11-23), 7,5 h × 5 días. La ley dice «no inferior a»:
   si la real es mayor, el neto/hora bajaría (en contra de la tesis 1). No hay norma de 35 h ni
   jornada anual de 2026 publicada en el BOCM (la última, de 2012, BOCM-20120229-7, la da por turno): la
   semanal es la media de todos los turnos. Con 227 días salen 1.702,5 h/año, un 3,5 % más que las 1.645 h del
   turno diurno de 2012: si la anual real es esa, el neto/hora sube un 3,5 % (a favor de la tesis 1; el modelo
   queda del lado conservador).
2. neto/hora = neto del hogar ÷ (nº de sueldos × horas trabajadas).
3. Pareja, madre y joven: sueldos de 2024 llevados a 2026 con el coste salarial total por trabajador de
   la ETCL de Madrid (×1,0593: media de 2025T3 a 2026T2 sobre media de 2024; 2026 no está completo y el salto
   cubre 1,5 años, no 2: infravalora algo la subida). Supone que la mediana crece como el coste salarial
   medio; si crece menos (la media la tiran los sueldos altos), el bruto queda sobrevalorado: neto/hora más
   alto (a favor de la tesis 1) y menos zonas negativas (contra la 2). El joven mediano es la P50 de la EES 2022 llevada a 2024
   con la media de su tramo (EAES): si el crecimiento se concentró en los sueldos altos, su bruto queda
   sobrevalorado, con neto/hora más alto (a favor de la tesis 1) y menos zonas negativas (contra la 2).
   La madre es la P50 de 2022 de las mujeres del gran grupo 4 de la CNO-11 en Madrid (EES; incluye
   empleos con atención al público, que cobran menos) llevada a 2024 con la mediana de las mujeres de
   Madrid (EAES): supone que la de su ocupación crece como la de todas. De los factores publicados es el
   más alto (con la media nacional de las empleadas de oficina saldría un 0,5 % menos). La enfermera es la
   tabla oficial de 2026 del SERMAS, sin trienios, noches, guardias ni productividad variable: por debajo de lo que
   cobra una enfermera con turnos (neto/hora más bajo y más zonas negativas). Incluye la subida del 1,5 %
   de 2026 (BOCM-20260209-6, art. 25.1), no el 0,5 % condicionado al IPC de 2026 (RDL 14/2025, art. 2.1),
   que se pagaría en 2027 si se aplica: unos 150 € al año menos. Para el Bono (ejercicio 2024) se usa la
   misma fila de la tabla oficial de 2024 (`ENFERMERA_2024`), no la de 2026 deflactada. Con todos los brutos en 2026 ya se pueden
   comparar perfiles entre sí, salvo por las diferencias de jornada y de fuente de cada uno.
4. Alquiler de contratos en vigor declarados, actualizado con el IPC de alquiler (`factor_ipc`) y sin
   `factor_brecha` (no es el de contrato nuevo, #329; suelo del precio): sobrante
   sobrevalorado (contra la tesis 2); diferencias de alquiler menores, precio de la hora más bajo
   (favorece la tesis 1).
5. 69 m² y cesta de gasto medio para todos: sobreestima el gasto de quien vive solo (más negativas).
6. Neto sin deducciones reembolsables ni autonómicas (monoparental infravalorado).
7. Tarifas `vigente_2026` (con el 50 % de descuento, solo vale en 2026), modo `tp`, 2 viajes al día,
   solo viajes al trabajo: transporte barato, favorece «vivir lejos compensa en euros».
8. Abono Joven hasta 25 años (`tarifas.edad_max_joven`).
9. La pareja trabaja en el mismo destino (uno 5 días, otro 2).
10. Precio de la hora frente a la referencia por defecto de `calcular` (la zona con menos horas hacia
    ese destino), que puede no ser el propio destino: `n_ref_distinta` en el log.
11. Solo pares con ruta; las zonas sin alquiler quedan fuera; «mismo tiempo» (< 5 h/mes) aparte.
12. Cada par (origen, destino) pesa igual, sin ponderar por población ni empleo: la mediana la mueven
    los municipios pequeños de C2.
13. Tesis 2: sobrante de una zona = mediana entre los destinos a los que llega (las zonas aisladas
    tienen pocos destinos).
14. «Ejes» = corona del origen (A = Madrid capital).
    # shortcut: mezcla ejes distintos dentro de una corona, definir corredores cuando existan.
15. Los destinos `polo` se excluyen: son una lista elegida a mano (F3-01) y no destinos que cualquier
    zona pueda tener, así que no entran en la mediana por zona.
"""

import pandas as pd

from mesobra import calculo, parametros_2026
from mesobra.figuras import es

# ET art. 34.1 (BOE-A-2015-11430): jornada ordinaria de 40 h semanales; 5 días de 8 h.
DIAS_SEMANA, HORAS_DIA = 5, 8
JORNADA_SERMAS = (
    37.5  # h/semana, mínimo de promedio: Ley 6/2011 CM, DA 1.ª.1 (BOE-A-2012-2980)
)
FUENTE_CALCULO = (
    "elaboración propia con mesobra.calculo (alquiler del SERPAVI actualizado con el IPC de alquiler del INE (IPC297196) hasta {ipc_hasta}, cesta de la EPF actualizada con el IPC del INE (tablas 76137 y 76127; elaboración propia con datos extraídos del sitio web del INE: www.ine.es), tarifas del CRTM, tiempos con los GTFS del CRTM y OpenStreetMap, neto con la LIRPF y las cotizaciones de 2026); supuesto: jornada de {horas_semana} h "
    "semanales ({norma_jornada}) y 227 días de trabajo al año (Decreto 75/2025)"
)
LLEVADA_A_2026 = (
    "llevada a 2026 con el coste salarial total por trabajador de la Encuesta Trimestral de Coste Laboral (INE, "
    "tabla 6061, Madrid, industria, construcción y servicios; media de 2025T3 a 2026T2 sobre media de 2024: ×1,0593; "
    "supuesto: la mediana crece como la media, y si crece menos el bruto queda sobrevalorado)"
)
FUENTE_SMI = "Real Decreto 126/2026, art. 3.1 (BOE-A-2026-3815): SMI de 17.094 €/año"
FUENTE_EAES = (
    "INE, Encuesta Anual de Estructura Salarial 2024, tabla 28191: mediana de la ganancia anual "
    "en la Comunidad de Madrid, 28.037,75 € (de 2024), "
    + LLEVADA_A_2026
    + ": 29.699,39 €, estimado"
)
FUENTE_MADRE = (
    "INE, Encuesta de Estructura Salarial 2022, tabla 36846: mediana (P50) de la ganancia anual de las mujeres "
    "«empleados contables, administrativos y otros empleados de oficina» (gran grupo 4 de la CNO-11, con los "
    "empleos de atención al público) en la "
    "Comunidad de Madrid, 21.555,32 € (de 2022), llevada a 2024 con la mediana de las mujeres de Madrid de la "
    "Encuesta Anual de Estructura Salarial, tabla 28191 (22.898,14 € en 2022 y 25.362,11 € en 2024, +10,8 %): "
    "23.874,79 € (de 2024), "
    + LLEVADA_A_2026
    + ": 25.289,71 €, estimado (supuesto: la mediana de su ocupación crece como la de todas las mujeres de Madrid)"
)
FUENTE_ENFERMERA = (
    "Orden de 3 de febrero de 2026, instrucciones de nóminas de la Comunidad de Madrid para 2026 "
    "(BOCM-20260209-6), anexo V, tabla 2.1.a de atención hospitalaria, pág. 65: enfermero/a del SERMAS en unidades de hospitalización, "
    "quirófanos, urgencias, UCI y UVI (A2, nivel 21), sueldo base, complementos de destino y específico, "
    "productividad fija y pagas extra, 30.421,38 € al año; sin trienios, noches ni guardias: por debajo de lo "
    "que cobra una enfermera con turnos; jornada de 37,5 h semanales, mínimo de promedio (Ley 6/2011 de la Comunidad de "
    "Madrid, DA 1.ª.1, BOE-A-2012-2980)"
)
FUENTE_JOVEN = (
    "INE, Encuesta de Estructura Salarial 2022, tabla 36850: mediana (P50) de la ganancia anual de 25 a 34 años "
    "en la Comunidad de Madrid, 22.676,37 € (de 2022), llevada a 2024 con la media de ese tramo en Madrid de la "
    "Encuesta Anual de Estructura Salarial, tabla 28201 (26.411,63 € en 2022 y 29.361,99 € en 2024, +11,2 %): "
    "25.209,48 € (de 2024), "
    + LLEVADA_A_2026
    + ": 26.703,50 €, estimado (supuesto: el salto de 2022 a 2024 es sobre todo de 2024)"
)
SMI = float(parametros_2026.SMI_ANUAL)
# INE, ETCL (tabla 6061), coste salarial total por trabajador y mes, Madrid, industria, construcción y servicios:
# los 4 trimestres de 2024 y los 4 últimos publicados (2025T3 a 2026T2). Cuatro trimestres seguidos quitan la
# estacionalidad (el 4.º es el de las pagas extra). Índice fijado antes de calcular (#416).
ETCL_2024 = (2778.27, 2885.14, 2632.96, 2942.93)
ETCL_ULTIMO = (2712.72, 3098.99, 3033.15, 3060.53)
FACTOR_2026 = (sum(ETCL_ULTIMO) / 4) / (sum(ETCL_2024) / 4)  # 1,0593


def a_2026(bruto_2024: float) -> float:
    """Bruto de 2024 llevado a 2026 con el coste salarial de la ETCL; estimado."""
    return round(bruto_2024 * FACTOR_2026, 2)


# Los de 2024 se conservan al céntimo de las cifras citadas: EAES t=28191; P50 2022 (t=36850) × media 2024 / 2022
# (t=28201); P50 mujeres, gran grupo 4, Madrid 2022 (t=36846) × mediana mujeres Madrid 2024 / 2022 (t=28191).
EAES_2024 = 28037.75
JOVEN_2024 = round(22676.37 * 29361.99 / 26411.63, 2)
MADRE_2024 = round(21555.32 * 25362.11 / 22898.14, 2)
EAES, JOVEN, MADRE = a_2026(EAES_2024), a_2026(JOVEN_2024), a_2026(MADRE_2024)
# 12 meses de (sueldo + destino + específico + prod. fija + prod. fija A.M.S.) + 2 extras + 2 adicionales
ENFERMERA = round(
    12 * (1199.52 + 592.11 + 177.99 + 1.89 + 289.45) + 2 * 1466.94 + 2 * 177.99, 2
)
# Misma fila en la Orden de nóminas de 2024 (BOCM-20240806-11, anexo V, tabla 2.1.a, pág. 100): 29.098,22 €,
# con el 2 % de 2024 y sin el 0,5 % adicional (RDL 4/2024, art. 6.2), abonable como atrasos en la primera nómina posible (BOCM-20250721-1).
ENFERMERA_2024 = round(
    12 * (1147.35 + 566.36 + 170.25 + 1.81 + 276.85) + 2 * 1403.14 + 2 * 170.25, 2
)
# Para añadir un perfil: una entrada con su `fuente` (sin fuente no entra).
# `sueldos`: (bruto €/año, días a la semana en el destino). `sueldos_2024`: el bruto de 2024 de los que se llevan
# a 2026 y de la enfermera (el Bono mira los ingresos del ejercicio 2024).
PERFILES = [
    {
        "nombre": "Persona sola con el SMI",
        "perfil": "solo",
        "edad": 30,
        "sueldos": [(SMI, 5)],
        "fuente": FUENTE_SMI,
    },
    {
        "nombre": "Teleoperador de 23 años con el SMI",
        "perfil": "solo",
        "edad": 23,
        "sueldos": [(SMI, 5)],
        "fuente": FUENTE_SMI,
    },
    {
        "nombre": "Pareja de 29 años con el sueldo mediano de Madrid",
        "perfil": "pareja",
        "edad": 29,
        "sueldos": [(EAES, 5), (EAES, 2)],
        "sueldos_2024": [(EAES_2024, 5), (EAES_2024, 2)],
        "fuente": FUENTE_EAES,
    },
    {
        "nombre": "Madre sola de 34 años con un hijo y el sueldo mediano de una empleada de oficina o administrativa en Madrid",
        "perfil": "monoparental",
        "edad": 34,
        "sueldos": [(MADRE, 5)],
        "sueldos_2024": [(MADRE_2024, 5)],
        "fuente": FUENTE_MADRE,
    },
    {
        "nombre": "Persona sola de 29 años con el sueldo mediano de su edad en Madrid",
        "perfil": "solo",
        "edad": 29,
        "sueldos": [(JOVEN, 5)],
        "sueldos_2024": [(JOVEN_2024, 5)],
        "fuente": FUENTE_JOVEN,
    },
    {
        "nombre": "Enfermera de 26 años del SERMAS, sin trienios, noches ni guardias",
        "perfil": "solo",
        "edad": 26,
        "sueldos": [(ENFERMERA, 5)],
        "sueldos_2024": [(ENFERMERA_2024, 5)],
        "horas_dia": JORNADA_SERMAS / DIAS_SEMANA,
        "norma_jornada": "Ley 6/2011 de la Comunidad de Madrid, DA 1.ª.1",
        "fuente": FUENTE_ENFERMERA,
    },
]


def horas_dia(perfil: dict) -> float:
    """Horas de la jornada diaria del perfil; las 8 del ET salvo que el perfil traiga la suya."""
    return perfil.get("horas_dia", HORAS_DIA)


def filas(api: dict, perfil: dict) -> pd.DataFrame:
    """Una fila por (destino, origen) con sobrante, horas y precio de la hora, de cada destino de zona."""
    corona = {
        f["properties"]["zona_id"]: f["properties"]["corona"]
        for f in api["zonas"]["features"]
    }
    # Los polos son una lista elegida a mano y no entran en la mediana por zona (nota 15); solo los de zona.
    destinos = [
        d["destino_id"] for d in api["tiempos"]["destinos"] if d["tipo"] == "zona"
    ]
    sin_brecha = calculo.api_precio_contrato(
        api
    )  # los titulares siguen con el precio de contrato (#329)
    salida = []
    for d in destinos:
        entrada = {
            "hogar": {"perfil": perfil["perfil"], "edad": perfil["edad"]},
            "sueldos": [
                {"destino": d, "dias": dias, "modo": "tp", "bruto": bruto}
                for bruto, dias in perfil["sueldos"]
            ],
        }
        res = calculo.calcular(sin_brecha, entrada)
        for origen, z in res["zonas"].items():
            bajo, alto = z["sobra_banda"] or (None, None)
            salida.append(
                {
                    "destino": d,
                    "origen": origen,
                    "corona": corona[origen],
                    "sobra": z["sobra"],
                    "sobra_bajo": bajo,
                    "sobra_alto": alto,
                    "horas": z["horas"],
                    "precio_hora": z["precio_hora"],
                    "etiqueta": z["etiqueta"],
                    "ref": res["ref"],
                    "neto": z["neto"],
                }
            )
    return pd.DataFrame(salida)


def resumen(df: pd.DataFrame, neto_hora: float) -> dict:
    """Cifras de las dos tesis a partir de `filas`; función pura."""
    p = df["precio_hora"].dropna()
    if p.empty:
        raise ValueError(
            "sin precio_hora: ningún par con ruta, alquiler y horas distintas"
        )
    por_corona = p.groupby(df["corona"]).agg(mediana="median", n="size")
    por_encima = por_corona.index[por_corona["mediana"] >= neto_hora].tolist()
    zona = (
        df[df["sobra"].notna()]
        .groupby("origen")[["sobra", "sobra_bajo", "sobra_alto"]]
        .median()
    )
    return {
        "neto_hora": neto_hora,
        "n": len(p),
        "mediana": p.median(),
        "q1": p.quantile(0.25),
        "q3": p.quantile(0.75),
        "n_mismo_tiempo": int((df["etiqueta"] == calculo.MISMO_TIEMPO).sum()),
        "n_negativos": int((p < 0).sum()),
        "n_encima": int((p >= neto_hora).sum()),
        "pct_encima": 100 * (p >= neto_hora).mean(),
        "coronas": {c: (r["mediana"], int(r["n"])) for c, r in por_corona.iterrows()},
        "coronas_encima": por_encima,
        "veredicto": "plan B" if por_encima else "tesis",
        "n_zonas": len(zona),
        "n_zonas_negativas": int((zona["sobra"] < 0).sum()),
        # [con el alquiler al P25 (sobrante alto), con el alquiler al P75 (sobrante bajo)]
        "banda_zonas_negativas": [
            int((zona["sobra_alto"] < 0).sum()),
            int((zona["sobra_bajo"] < 0).sum()),
        ],
    }


def resumenes(api: dict) -> list[tuple[dict, dict]]:
    """(perfil, resumen) de cada perfil; el resumen añade `n_ref_distinta` (destinos con otra referencia) e `ipc_hasta`."""
    salida = []
    for perfil in PERFILES:
        horas = api["tarifas"]["semanas_mes"] * DIAS_SEMANA * horas_dia(perfil)
        df = filas(api, perfil)
        r = resumen(df, df["neto"].iloc[0] / (len(perfil["sueldos"]) * horas))
        ref = df.groupby("destino")["ref"].first()
        r["n_ref_distinta"] = int((ref != ref.index).sum())
        r["ipc_hasta"] = api["alquiler"]["meta"]["ipc_hasta"]
        r["n_destinos"] = len(ref)
        salida.append((perfil, r))
    return salida


def titulares(res: list[tuple[dict, dict]]) -> list[dict]:
    """Dos entradas `{"texto", "fuente"}` por perfil; descriptivas, con n y banda, todo «estimado»."""
    salida = []
    for perfil, r in res:
        horas_semana = es(horas_dia(perfil) * DIAS_SEMANA, 1).removesuffix(",0")
        calculo_fuente = FUENTE_CALCULO.format(
            ipc_hasta=r["ipc_hasta"],
            horas_semana=horas_semana,
            norma_jornada=perfil.get("norma_jornada", "ET art. 34.1"),
        )
        fuente = f"{calculo_fuente}; sueldo: {perfil['fuente']}"
        coronas = ", ".join(
            f"{c} {es(m, 2)} € (n = {es(n, 0)})" for c, (m, n) in r["coronas"].items()
        )
        alto, bajo = r["banda_zonas_negativas"]
        salida.append(
            {
                "texto": f"{perfil['nombre']}: neto estimado de {es(r['neto_hora'], 2)} € por hora trabajada. "
                f"En {es(r['n'], 0)} pares origen-destino con ruta, alquiler y más horas que la zona de referencia, vivir lejos de un destino rinde una mediana estimada "
                f"de {es(r['mediana'], 2)} € por hora extra de viaje (cuartiles {es(r['q1'], 2)} a {es(r['q3'], 2)}); "
                f"iguala o supera el neto por hora en {es(r['n_encima'], 0)} pares ({es(r['pct_encima'])} %), "
                f"{es(r['n_negativos'], 0)} salen negativos y otros {es(r['n_mismo_tiempo'], 0)} (mismo tiempo) quedan aparte. "
                f"Mediana por corona de origen: {coronas}. Veredicto: {r['veredicto']}.",
                "fuente": fuente,
            }
        )
        salida.append(
            {
                "texto": f"{perfil['nombre']}: el sobrante mensual estimado, mediana entre los destinos a los que "
                f"llega cada zona, es negativo en {r['n_zonas_negativas']} de {r['n_zonas']} zonas con alquiler "
                f"(entre {alto} y {bajo} con el alquiler en su banda: P25 a P75, ampliado al intervalo si la zona es estimada).",
                "fuente": fuente,
            }
        )
    return salida
