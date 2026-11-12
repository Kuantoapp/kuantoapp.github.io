---
description: Método de análisis de datos espaciales del proyecto (matrices de pesos W, I de Moran y LISA, regresión espacial SAR/SEM/SDM, validación espacial por bloques o buffer, kriging, mapas coropléticos y CRS). Úsala al escribir o revisar código que cruce datos por municipio, barrio, sección censal o código postal, que impute o prediga valores en el territorio, que valide un modelo con datos geográficos o que pinte un mapa.
when_to_use: Imputar el alquiler en municipios sin dato, calcular sobrecarga por sección, construir retardos espaciales para un modelo de ML, elegir entre validación aleatoria y espacial, comprobar si los residuos tienen patrón espacial, preparar un coroplético para la demo.
---

# Análisis de datos espaciales

Método de la asignatura *Análisis de Datos Espaciales* (Grado en Ciencia de Datos Aplicada, UCM), adaptado a Python y a este proyecto.
Parte del jurado conoce este método: seguirlo y nombrarlo bien (W, I de Moran, LISA, SAR, SEM, validación por bloques) es parte de la defensa.

## Regla de oro

Toda dependencia espacial que el modelo no explique acaba en los residuos. Un modelo con datos territoriales no está terminado hasta que la I de Moran de sus residuos no es significativa, o hasta que se declara por qué no lo es.

## Flujo de trabajo

1. **Unidad y CRS.** Decide la unidad (municipio, barrio, sección censal) y trabaja en **ETRS89 / UTM 30N (EPSG:25830)** para distancias y áreas. EPSG:4326 solo para guardar o servir al mapa web. Une siempre por **código oficial** (INE de municipio y sección, código de barrio municipal), nunca por nombre. Los códigos postales no son una unidad estadística: necesitan tabla de paso. Ver [cartografia-y-mapas.md](referencia/cartografia-y-mapas.md).
2. **Exploración visual.** Coroplético de la variable con una clasificación justificada (cuantiles, Jenks o desviaciones). Para comprobar a ojo si hay patrón, compáralo con el mismo mapa con los valores **barajados** al azar entre zonas. Si representa tasas de zonas con poca población, ojo: el color engaña.
3. **Matriz de pesos W.** Contigüidad reina para polígonos (municipios, barrios); k vecinos o banda de distancia para puntos o zonas muy desiguales. **Normaliza por filas.** Revisa las islas (zonas sin vecinos) antes de seguir. W es la decisión más frágil: prueba al menos dos y comprueba que las conclusiones se mantienen. Ver [pesos-y-autocorrelacion.md](referencia/pesos-y-autocorrelacion.md).
4. **Autocorrelación.** I de Moran global con permutaciones y diagrama de dispersión de Moran. LISA (Moran local) para clústeres alto-alto, bajo-bajo y atípicos; Gi* de Getis-Ord para puntos calientes y fríos.
5. **Modelo.** Primero sin componente espacial. Después I de Moran de los residuos. Si sale significativa:
   - para **explicar** (inferencia): regresión espacial, elegida con los tests LM de Anselin o comparando especificaciones por AIC. Ver [regresion-espacial.md](referencia/regresion-espacial.md);
   - para **predecir** (ML): añade retardos espaciales `Wy` y `WX` como variables y vuelve a mirar los residuos. Ver [prediccion-y-validacion.md](referencia/prediccion-y-validacion.md).
6. **Validación según el escenario de uso.** La partición no es un detalle técnico: define qué pregunta responde la métrica.
   - **Caso A, interpolar** donde hay vecinos con dato: validación aleatoria.
   - **Caso B, extrapolar** a zonas sin ninguna observación cercana: validación por **bloques espaciales** o con **buffer**.
7. **Incertidumbre.** Intervalos de predicción conformales, comprobando la cobertura real en la validación.

## Aplicación a «¿Me sobra?»

| Pieza | Escenario | Qué exige |
|---|---|---|
| Imputar el alquiler de municipios sin dato (corona C) | **Caso B** | Validación por bloques espaciales (grupos de municipios contiguos) o buffer, no aleatoria. `Wy` del test calculado solo con vecinos de train. Comparar con un modelo de referencia simple. Modelo de árboles con distancias derivadas, sin coordenadas en bruto, y variables elegidas con **selección hacia delante con validación por bloques**; kriging o retardo de residuos como mejora, validados por bloques. Intervalo conformal **calibrado por corona** (Mondrian o CQR) y cobertura medida por grupo. |
| Alquiler por barrio en Madrid capital | Caso A | Tabla de paso código postal → barrio con pesos por viviendas, declarada. |
| Sobrecarga por sección censal | — | Moran y LISA de la sobrecarga para el mapa de la Administración. Clústeres alto-alto = zonas prioritarias. |
| Focalizar el Bono | — | LISA **bivariante** de sobrecarga frente a tasa de solicitudes aceptadas: clústeres de mucha sobrecarga con poca ayuda alrededor. Tasas de municipios pequeños suavizadas con Bayes empírico. |
| Variables para imputar | — | Accesibilidad con datos abiertos (distancia o tiempo al punto de interés más cercano, conteos en radios), revisando su cobertura en la corona C. SHAP para explicar cada estimación. |
| Mapas de la demo | — | Primero un mapa de caja para ver atípicos. Coroplético con clasificación explicada en la leyenda, la marca «estimado» visible y paleta apta para daltónicos. |
| Precio de la vivienda en Madrid | — | Montero, Mínguez y Fernández-Avilés (2018) comparan modelos hedónicos espaciales con datos de Madrid. Los no lineales con heterogeneidad espacial predicen mejor. Ver [regresion-espacial.md](referencia/regresion-espacial.md). |

## Errores que invalidan un resultado

- **Fuga espacial en la validación.** `Wy` del conjunto de test calculado con el **propio valor de test** (el `y` que se quiere predecir). Para el test, `Wy` es la media ponderada de los vecinos de **train**.
- Validación aleatoria para presumir de error bajo en el **caso B**.
- Coordenadas o identificadores de zona como variables en el caso B, o variables elegidas por importancia del modelo completo (RFE). El modelo memoriza en vez de predecir, y el mapa muestra artefactos.
- Distancias o áreas calculadas en grados (EPSG:4326).
- Unir tablas por nombre de municipio («Las Rozas de Madrid» frente a «Rozas de Madrid, Las»).
- W sin normalizar por filas, o islas sin tratar (`zero.policy` en R, `silence_warnings` y revisión manual en Python).
- Estimar un modelo SAR por mínimos cuadrados ordinarios: es inconsistente. Hace falta máxima verosimilitud o variables instrumentales.
- Interpretar el coeficiente β de un SAR o un SDM como efecto marginal: hay efectos directos e indirectos.
- Coroplético de valores absolutos (población, número de solicitudes) en vez de tasas, o tasas de municipios diminutos sin suavizar.
- Error o cobertura del intervalo informados solo en global, sin mirarlos por corona y por renta. El modelo suele fallar más justo donde la Administración debe actuar.

## Herramientas en Python

`geopandas` (geometrías y CRS), `libpysal` (W), `esda` (Moran, LISA, Getis-Ord), `spreg` (MCO con tests LM, SAR y SEM por máxima verosimilitud), `mgwr` (GWR), `pykrige` (kriging), `scikit-learn` (`GroupKFold` para bloques), `mapclassify` (clasificación de coropléticos). Equivalencias con R en [python.md](referencia/python.md).

Para interpolación de superficies continuas (no es el caso típico de este proyecto, que usa zonas), ver [interpolacion.md](referencia/interpolacion.md).
