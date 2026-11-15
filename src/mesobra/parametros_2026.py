"""Parámetros legales de 2026 para el neto de un trabajador por cuenta ajena en la Comunidad de Madrid.

Cada cifra cita su norma; la referencia es `.claude/skills/dm-calculos-normativos/referencia/nomina-bruto-a-neto.md`.
Vigentes desde el 01/01/2026; contrastados con el texto consolidado del BOE el 15/11/2026
(dm-auditor-calculos-normativos, #79). Si cambia el año, se rehace entera.
"""

from decimal import Decimal as D

# Cotización del trabajador, contrato indefinido: 4,70 + 1,55 + 0,10 + 0,15 (Orden PJC/297/2026, arts. 4.a, 33.2.a.1.º, 33.2.c y 16; BOE-A-2026-7296)
TIPO_COTIZACION = D("0.065")
# Base máxima mensual (Orden PJC/297/2026, art. 2.1; BOE-A-2026-7296)
BASE_MAXIMA_MES = D("5101.20")
# Solidaridad, parte del trabajador: (desde, tipo) marginal sobre la retribución mensual (Orden PJC/297/2026, art. 17.1; BOE-A-2026-7296)
SOLIDARIDAD = (
    (D("5101.20"), D("0.0019")),
    (D("5611.32"), D("0.0021")),
    (D("7651.80"), D("0.0024")),
)

# Otros gastos deducibles (LIRPF, art. 19.2.f; BOE-A-2006-20764)
GASTOS_OTROS = D(2000)
# Reducción por rendimientos del trabajo (LIRPF, art. 20.1, redacción del RDL 4/2024; BOE-A-2006-20764)
RED20_FIJA = D(7302)
RED20_UMBRAL_1 = D(14852)
RED20_PENDIENTE_1 = D("1.75")
RED20_UMBRAL_2 = D("17673.52")
RED20_TRAMO_2 = D("2364.34")
RED20_PENDIENTE_2 = D("1.14")
RED20_UMBRAL_3 = D("19747.50")

# Escala general estatal: (base desde, cuota acumulada, tipo) (LIRPF, art. 63.1; BOE-A-2006-20764)
ESCALA_ESTATAL = (
    (D(0), D(0), D("0.095")),
    (D(12450), D("1182.75"), D("0.12")),
    (D(20200), D("2112.75"), D("0.15")),
    (D(35200), D("4362.75"), D("0.185")),
    (D(60000), D("8950.75"), D("0.225")),
    (D(300000), D("62950.75"), D("0.245")),
)
# Escala autonómica de Madrid (DL 1/2010, art. 1; BOCM-m-2010-90068)
ESCALA_MADRID = (
    (D(0), D(0), D("0.085")),
    (D("13362.22"), D("1135.79"), D("0.107")),
    (D("19004.63"), D("1739.53"), D("0.128")),
    (D("35425.68"), D("3841.42"), D("0.174")),
    (D("57320.40"), D("7651.10"), D("0.205")),
)

# Mínimo del contribuyente, estatal (LIRPF, art. 57; BOE-A-2006-20764)
MINIMO_ESTATAL = D(5550)
# Mínimo del contribuyente en Madrid (DL 1/2010, art. 2.a; BOCM-m-2010-90068)
MINIMO_MADRID = D("5956.65")
# Mínimo por 1.º y 2.º descendiente, estatal (LIRPF, art. 58; BOE-A-2006-20764)
DESCENDIENTES_ESTATAL = (D(2400), D(2700))
# Mínimo por 1.º y 2.º descendiente en Madrid (DL 1/2010, art. 2 bis; BOCM-m-2010-90068)
DESCENDIENTES_MADRID = (D("2575.85"), D("2897.83"))

# Umbral de la DA 61.ª.1.a) LIRPF, fijado en literal; coincide con el SMI anual de 2026 (RD 126/2026, art. 1)
SMI_ANUAL = D(17094)
# Deducción por percepción del SMI (LIRPF, DA 61.ª, redacción del RDL 5/2026, art. 28; BOE-A-2026-3810)
DEDUCCION_SMI = D("590.89")
DEDUCCION_SMI_PENDIENTE = D("0.2")
DEDUCCION_SMI_LIMITE = D("20048.45")
