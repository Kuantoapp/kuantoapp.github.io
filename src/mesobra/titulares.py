"""Titulares con sueldos de referencia (#93): las dos tesis de la ficha A §8 para perfiles tipo.

Tesis 1: el ahorro de vivir lejos paga la hora de viaje por debajo del neto por hora trabajada.
Tesis 2: con sueldos típicos, en muchas zonas no sobra nada. Todo sale de `mesobra.calculo.calcular`
(modo `tp`) hacia cada destino de `tiempos.json`; aquí solo se agrupa. Veredicto de la tesis 1:
«tesis» si ninguna corona de origen tiene mediana del precio de la hora ≥ neto/hora, si no «plan B»
(regla fijada antes de ver los datos). La tesis 2 se da con la cifra, sin umbral.

Supuestos y sentido de su sesgo (cada perfil lleva la `fuente` de su sueldo):
1. Horas trabajadas al mes = `semanas_mes` × 5 × 8 (jornada de 40 h, ET art. 34.1, BOE-A-2015-11430),
   igual para todos. Con jornada real menor el neto/hora real es mayor: favorece la tesis 1.
2. neto/hora = neto del hogar ÷ (nº de sueldos × horas trabajadas).
3. Sueldos de 2024 (EAES) usados como bruto de 2026: neto infravalorado, más zonas negativas (tesis 2)
   y neto/hora más bajo (contra la tesis 1).
4. Alquiler en euros de 2024 sin IPC, de contratos declarados (suelo del precio): sobrante
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
15. Los destinos `polo` se excluyen: sin corona, `calcular` da error hasta que haya polos con corona
    (F3-01).
"""

import pandas as pd

from mesobra import calculo
from mesobra.figuras import es

# ET art. 34.1 (BOE-A-2015-11430): jornada ordinaria de 40 h semanales; 5 días de 8 h.
DIAS_SEMANA, HORAS_DIA = 5, 8
FUENTE_CALCULO = "elaboración propia con mesobra.calculo (SERPAVI, EPF, CRTM, r5py)"
FUENTE_SMI = "Real Decreto 126/2026, art. 3.1 (BOE-A-2026-3815): SMI de 17.094 €/año"
FUENTE_EAES = (
    "INE, Encuesta Anual de Estructura Salarial 2024, tabla 28191: mediana de la ganancia anual "
    "en la Comunidad de Madrid, 28.037,75 € (de 2024)"
)
FUENTE_OFICINA = (
    "INE, Encuesta Anual de Estructura Salarial 2024, tabla 28186, serie EAES2540: ganancia media anual "
    "de las mujeres empleadas de oficina que no atienden al público, total nacional, 28.264,34 € (de 2024)"
)
SMI, EAES, OFICINA = 17094, 28037.75, 28264.34
# Para añadir un perfil: una entrada con su `fuente` (sin fuente no entra). La enfermera de 26 años
# no entra: el grupo más fino de la EAES (salud y enseñanza, tabla 28186) mezcla medicina y docencia.
# `sueldos`: (bruto €/año, días a la semana en el destino).
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
        "fuente": FUENTE_EAES,
    },
    {
        "nombre": "Madre sola de 34 años con un hijo y sueldo de administrativa",
        "perfil": "monoparental",
        "edad": 34,
        "sueldos": [(OFICINA, 5)],
        "fuente": FUENTE_OFICINA,
    },
]


def filas(api: dict, perfil: dict) -> pd.DataFrame:
    """Una fila por (destino, origen) con sobrante, horas y precio de la hora, de cada destino de zona."""
    corona = {
        f["properties"]["zona_id"]: f["properties"]["corona"]
        for f in api["zonas"]["features"]
    }
    # Los polos no tienen corona: `calcular` fallaría (hasta F3-01); solo los destinos de zona.
    destinos = [
        d["destino_id"] for d in api["tiempos"]["destinos"] if d["tipo"] == "zona"
    ]
    salida = []
    for d in destinos:
        entrada = {
            "hogar": {"perfil": perfil["perfil"], "edad": perfil["edad"]},
            "sueldos": [
                {"destino": d, "dias": dias, "modo": "tp", "bruto": bruto}
                for bruto, dias in perfil["sueldos"]
            ],
        }
        res = calculo.calcular(api, entrada)
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
        "n_encima": int((p > neto_hora).sum()),
        "pct_encima": 100 * (p > neto_hora).mean(),
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
    """(perfil, resumen) de cada perfil; el resumen añade `n_ref_distinta` (destinos con otra referencia)."""
    horas = api["tarifas"]["semanas_mes"] * DIAS_SEMANA * HORAS_DIA
    salida = []
    for perfil in PERFILES:
        df = filas(api, perfil)
        r = resumen(df, df["neto"].iloc[0] / (len(perfil["sueldos"]) * horas))
        ref = df.groupby("destino")["ref"].first()
        r["n_ref_distinta"] = int((ref != ref.index).sum())
        r["n_destinos"] = len(ref)
        salida.append((perfil, r))
    return salida


def titulares(api: dict, res: list[tuple[dict, dict]] | None = None) -> list[dict]:
    """Dos entradas `{"texto", "fuente"}` por perfil; descriptivas, con n y banda, todo «estimado»."""
    salida = []
    for perfil, r in res or resumenes(api):
        fuente = f"{FUENTE_CALCULO}; sueldo: {perfil['fuente']}"
        coronas = ", ".join(
            f"{c} {es(m, 2)} € (n = {es(n, 0)})" for c, (m, n) in r["coronas"].items()
        )
        alto, bajo = r["banda_zonas_negativas"]
        salida.append(
            {
                "texto": f"{perfil['nombre']}: neto estimado de {es(r['neto_hora'], 2)} € por hora trabajada. "
                f"En {es(r['n'], 0)} pares origen-destino con ruta, vivir lejos de un destino rinde una mediana estimada "
                f"de {es(r['mediana'], 2)} € por hora extra de viaje (cuartiles {es(r['q1'], 2)} a {es(r['q3'], 2)}); "
                f"supera el neto por hora en {es(r['n_encima'], 0)} pares ({es(r['pct_encima'])} %), "
                f"{es(r['n_negativos'], 0)} salen negativos y otros {es(r['n_mismo_tiempo'], 0)} (mismo tiempo) quedan aparte. "
                f"Mediana por corona de origen: {coronas}. Veredicto: {r['veredicto']}.",
                "fuente": fuente,
            }
        )
        salida.append(
            {
                "texto": f"{perfil['nombre']}: el sobrante mensual estimado, mediana entre los destinos a los que "
                f"llega cada zona, es negativo en {r['n_zonas_negativas']} de {r['n_zonas']} zonas con alquiler "
                f"(entre {alto} y {bajo} según el alquiler baje al P25 o suba al P75).",
                "fuente": fuente,
            }
        )
    return salida
