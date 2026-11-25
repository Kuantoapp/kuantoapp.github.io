# Registro de cifras del informe

Paso 0 de #468. Cada cifra que usa el informe, con su origen en el repositorio. No hay cifras nuevas: todas están ya publicadas en `app/` o documentadas en `docs/`. «E» = estimado. Sirve para que `dm-trazador-cifras` compruebe el informe contra este registro y el registro contra su origen.

Abreviaturas de origen: **AJ** = `app/datos/analisis.json`; **BI** = `data/processed/bono_inferencia.json` (`python -m mesobra.bono_inferencia`); **INF** = `app/informe.html` de `main` a 25-11 (ya trazado); **MET** = `app/metodologia.html`; **DEC** = `docs/decisiones.md` (fecha); **RD** = `data/README.md`.

## Escala del trabajo (cap. 2)

| Cifra | Origen | E |
|---|---|---|
| 199 zonas: 178 municipios y 21 distritos de Madrid | MET («Las zonas son…»); `app/datos/zonas.geojson` | |
| 89 descargas registradas con su SHA-256 | RD, tabla «Fuentes» (91 filas menos cabecera y ejemplo) | |
| 158 zonas con alquiler publicado; 41 sin él | MET, «Límites» | |
| 11.840 pares zona–destino con peso; 4.239 sin ruta en 120 min | INF, «Simulación», «Límites y validación» | E |
| 42.785 pares de transporte público; 31.606 (73,9 %) sin ruta en 120 min | MET, «Límites» | |
| 16 polos de empleo con nombre | MET | |
| 6 perfiles de sueldo con fuente oficial | INF, «Seis sueldos» | |
| 8 casos completos del neto calculados a mano, de 17.094 a 80.000 € | MET, «Validación» | |

## Esfuerzo de alquiler (cap. 4 y 5)

| Cifra | Origen | E |
|---|---|---|
| 157 de 199 zonas con dato en 2024; zona mediana 15,3 % | INF; AJ `esfuerzo` | |
| Centro y Puente de Vallecas 24,0 %; Usera 23,4; Carabanchel 22,6; Latina 22,3; Villaverde 22,1 | INF; AJ | |
| Chamartín 16,0 %; Moncloa-Aravaca 16,1; Salamanca 19,0; Madrid entero 19,6 | INF; AJ | |
| Villanueva de la Cañada 12,6 %; Algete 12,8; Cobeña 12,9 (≥ 70 testigos) | INF; AJ | |
| Chamartín: alquiler 1.126 €/mes, renta 7.051 €/mes; Centro: 950 y 3.965 (+78 %) | INF; AJ | |
| Cortes de quintil 13,9; 14,8; 16,0; 18,2 %; saltos de 6,7, 8,1 y 13,7 % | INF; DEC 2026-11-20 | |
| 17 de 21 distritos en el quintil alto; 8 con intervalos iguales | INF | |
| El IC 95 % cruza al menos un corte en 89 de 157 zonas | INF; DEC 2026-11-23 | E |
| Margen de la mediana con 70 testigos: ±8 % típico, > ±12 % en algo más de 1 de cada 10 | INF; DEC 2026-11-23 | E |
| Madrid entero: 19,1 % (2015), 21,0 % (2020), 19,6 % (2024); serie anual y banda de los distritos (G4) | AJ `titulares` y `esfuerzo`; INF | |
| Esfuerzo de 2015 y 2024 de cada distrito (G5) | AJ `esfuerzo` | |
| 142 zonas con dato en 2015 y 2024; sube en 68; mediana del cambio −0,06 p. p. | INF | |
| Bajan 29 (2 imprecisas), suben 31 (0), sin cambio claro 82 (31 imprecisas) | INF; DEC 2026-11-23 | E |
| Distritos: 12 suben, 3 bajan, 6 sin cambio claro | INF | E |
| Mayores bajadas: Chinchón 3,1 p. p., Moraleja de Enmedio 2,6; subidas: Salamanca 2,3, Retiro 1,8 | INF | |
| Unas 7 zonas saldrían claras por azar (142 contrastes al 95 %) | DEC 2026-11-23 | E |

## Hogares concretos (cap. 6 y 7)

| Cifra | Origen | E |
|---|---|---|
| Neto por hora: SMI 8,80 €; pareja 12,80; madre 11,41; joven 11,69; enfermera 13,94 | INF; AJ `titulares` | E |
| Pares en que vivir lejos rinde el neto por hora: 1.218 de 8.620 (14,1 %) SMI; 1.268 (14,7 %) teleoperador; 306 de 8.651 (3,5 %) pareja; 846 de 8.620 (9,8 %) madre; 816 de 8.620 (9,5 %) joven; 612 de 8.620 (7,1 %) enfermera | INF; AJ | E |
| Lo que rinde la hora extra, mediana (cuartiles) en €/h: SMI −0,34 (−5,65 a 4,99); teleoperador −0,18 (−5,30 a 5,25); pareja −0,33 (−4,23 a 3,41); madre, joven y enfermera −0,34 (−5,65 a 4,99) (G8) | AJ `titulares` | E |
| Ahorro por hora extra con el SMI: 1,90 a 4,65 € en B3, C1 y C2; −8,30 € en A | INF; AJ | E |
| Zonas con sobrante negativo: SMI 18 de 158 (8 a 33); teleoperador 18 (8 a 30); madre 7 (0 a 14); joven 2 (0 a 8); pareja 0; enfermera 0 (hasta 3) | INF; AJ | E |
| Sobrecarga de inquilinos: 36,0 % [28,6; 43,4]; 562 hogares en la muestra | INF; DEC 2026-11-18 | E |
| Modelo por zona: 47,2 % (47,0–47,3), fuera del intervalo; renta de inquilinos −11 % | DEC 2026-11-18; INF | E |

## Bono Alquiler Joven (cap. 8 y 9)

| Cifra | Origen | E |
|---|---|---|
| 51.735 solicitudes, 11.477 aceptadas; 3.352 en «Otro»; 22,2 % / 23,7 % aceptadas | INF | |
| 159 municipios con solicitudes; 134 con esfuerzo; 25 fuera con 74 solicitudes | INF; AJ `bono` | |
| Madrid: 30.961 solicitudes, 7.324 aceptadas, 9,6 por 1.000 jóvenes; municipio mediano 4,0 | INF | |
| NB de solicitudes: p = 0,051; Moran de residuos 0,19 (p = 0,004) | BI `glm.solicitudes` | E |
| SEM het. β ≈ 87, p = 0,043 (k = 5) y 0,048 (k = 8); HAC p = 0,17; r parcial 0,137 (p = 0,118) | BI `espacial`, `pearson_parcial` | E |
| Proporción aceptada no cambia con el esfuerzo: p = 0,82 | BI `glm.aceptadas_sobre_solicitudes` | E |
| Con % de jóvenes en alquiler: β = 46 (p = 0,22) k = 5; β = 34 (p = 0,37) k = 8; 112 municipios | INF; BI `robustez_vivienda_alquilada` | E |
| 16 de 138 municipios fuera del tope (SMI, 69 m²); 14 por menos de 80 €; Madrid por 79,51 € | INF; AJ `simulacion` | E |
| Importes sobre el tope de cada municipio (El Molar 6,81 … Pozuelo 108,24) | INF; AJ; `app/datos/alquiler.json` | E |
| Criterios alternativos: 72, 65 y 14 municipios (12 el joven de 29 años, solo en G12); horas de viaje 112–138, 106–135, 104–134 | INF; AJ | E |
| 8 de los 21 distritos de Madrid, por debajo del tope | INF; DEC | E |
| G7: 9 especificaciones, 5 intervalos tocan el cero; principal en los 112 municipios, p = 0,022 | BI | E |
| Pareja y joven: 122 municipios con base imponible, 0 con bruto | INF; AJ | E |
| Enfermera: supera el límite en 6,84 € (cotización 2026) y 15,57 € (2024) | INF | E |
| Tope: 600 € y 900 € en 55 municipios del Anexo II; ingresos hasta 3 × IPREM = 25.200 € | INF (BOCM-20250110-20) | |
| Valor de la hora de viaje 9,76 € (32,5 % del coste laboral) | INF | E |

## Transporte (cap. 10)

| Cifra | Origen | E |
|---|---|---|
| Fin del descuento: A y B1 9,23–19,67 €; B2 12,18–26,11; B3, C1 y C2 15,26–32,76; joven 9,30 | INF; AJ `simulacion` | E |
| Por abono: C2 35,20 €; joven 10,00 €; el abono se compra unas 11 veces al año | INF | E |

## Calidad del dato (cap. 12)

| Cifra | Origen | E |
|---|---|---|
| Umbral de 70 alquileres declarados; 39 de 158 zonas por debajo | MET; DEC 2026-11-23 | |
| Semiancho del €/m² con 70: 9,7 / 13,3 % (mediana / p90) | DEC 2026-11-23 | E |
| La lognormal se desvía > 5 % del p50 en 15 de 158 zonas | DEC 2026-11-23 | E |
| Horarios reconstruidos: 2.405 de 11.179 pares con ruta (21,5 %); prueba en 494 viajes, cociente 1,06, error medio 20,7 min | MET | E |
| Simulador de tiempos: hasta 7 minutos entre dos pasadas | MET | |
| Neto: interpolación < 1 €/mes del cálculo exacto | MET | |

## Capas derivadas para gráficos (no son cifras del texto)

- **G2**: IC 95 % de cada zona, de `figuras.errores_cambio` y `alquiler.semiancho_lognormal` (método de DEC 2026-11-23).
- **G6**: proporción aceptada de cada municipio = aceptadas / solicitudes, y esfuerzo de 2023 = `necesidad` / `poblacion_joven`, de AJ `bono`. Sin límites binomiales: la escala cuasi-binomial de 1,88 (BI) dice que la dispersión es mayor que la binomial.
- **G7**: IC 95 % = β ± 1,96 · se de cada especificación de BI (todas las de `espacial.k5`, el SEM heterocedástico con 8 vecinos y el control por % de jóvenes en alquiler) y la r parcial con su `ic95`.
- **G12**: municipios que cumplen cada criterio por perfil, recuento de AJ `simulacion`.
