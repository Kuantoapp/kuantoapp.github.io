# Interpolación y geoestadística

Para variables definidas en un **dominio continuo** (temperatura, contaminación, precio en cualquier punto) observadas solo en algunos puntos. Si los datos son zonas con fronteras (municipios, secciones), el marco es el de la regresión espacial, no este.

## Tres tipos de datos espaciales

| Dominio | Ejemplo | Técnica |
|---|---|---|
| Aleatorio (los puntos son el fenómeno) | Ubicación de desfibriladores o incendios | Patrones de puntos: intensidad, función K o L de Ripley, frente a aleatoriedad completa (CSR) |
| Fijo y continuo | Precipitación, ruido | Geoestadística: semivariograma y kriging |
| Fijo y discreto | Paro municipal, renta por sección | Autocorrelación y regresión espacial |

## Métodos

- **Deterministas:** vecino más próximo (Thiessen o Voronoi), **IDW** (distancia inversa ponderada, con exponente a elegir). Rápidos, sin medida de error.
- **Kriging:** predicción lineal óptima con pesos sacados del semivariograma. Da la **varianza de predicción**.
  - **Ordinario:** supone media constante (estacionariedad).
  - **Universal o regresión-kriging:** si hay tendencia, modela la media con covariables (cualquier modelo predictivo) y aplica kriging a los **residuos**. Es el puente con el ML espacial.

## Semivariograma

- γ(h): mitad de la varianza de la diferencia entre valores separados h. Requiere estacionariedad débil o intrínseca.
- **Pepita (nugget):** γ en h → 0. Variación a escala menor que el muestreo o error de medida.
- **Meseta (sill):** valor máximo; pepita + meseta parcial.
- **Alcance (range):** distancia a la que se llega a la meseta (≈ 95 % en esférico y exponencial). Más allá ya no hay dependencia. **Sirve para elegir el tamaño de bloque o el radio de buffer en la validación.**
- Ajusta un modelo teórico (esférico, exponencial, gaussiano) al semivariograma empírico y revisa la anisotropía (dependencia distinta según la dirección).
- Valida con validación cruzada (en R `krige.cv`; en Python, folds manuales con `pykrige`).
