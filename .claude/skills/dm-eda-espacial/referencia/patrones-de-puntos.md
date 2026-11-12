# Patrones de puntos

Basado en el tema 4 del curso. Sirve cuando **la ubicación es el dato**: farmacias, centros de salud, paradas, empresas. En «¿Me sobra?» aparece al construir variables de accesibilidad y al estudiar dónde están los servicios; en la idea «Cerca» sería central.

## Conceptos

- **Proceso de puntos:** el mecanismo aleatorio que genera las ubicaciones. **Patrón:** lo observado, una realización del proceso.
- **Marcas:** atributos del evento (tipo de servicio, número de empleados). **Covariables:** atributos del lugar (población, renta, pendiente).
- **Primer orden (intensidad λ(s)):** cuántos puntos se esperan en cada sitio. Global = N / área; local con cuadrantes o con densidad kernel (el ancho de banda decide el suavizado).
- **Segundo orden (interacción):** si los puntos se atraen (agrupación), se repelen (regularidad) o son independientes.
- **Aleatoriedad espacial completa (CSR):** proceso de Poisson homogéneo, con intensidad constante e independencia. Es la hipótesis nula de los tests clásicos.

## Herramientas

| Herramienta | Qué mide | Lectura |
|---|---|---|
| Densidad por cuadrantes o kernel | Intensidad local | Mapa de dónde se concentran |
| Centrografía | Centro medio, dispersión, elipse | Resumen de la ubicación |
| Vecino más próximo, test de Clark-Evans | Distancia media al vecino más cercano frente a CSR | < CSR: agrupados; > CSR: regulares |
| Función **G** | Distribución de distancias al vecino más próximo | Por encima de la esperada: agrupación |
| Función **K** de Ripley | Puntos a cada distancia d, todas las escalas | K > esperada: agrupación a esa escala |
| Función **L** | K transformada para que la esperada sea horizontal | Más fácil de leer: > 0 agrupación, < 0 dispersión |
| DBSCAN | Clústeres por densidad | Agrupaciones de forma libre |

Compara siempre con **envolventes de simulación** (muchas realizaciones de CSR) y no con la curva teórica sola.

## La trampa en datos urbanos

G, K y L **suponen intensidad constante**. Los servicios urbanos siguen a la población: siempre saldrán «agrupados» frente a CSR, y eso no dice nada.

- Usa como referencia la población: **proceso de Poisson no homogéneo** con λ(s) = exp(α + β·población(s)), y las versiones no homogéneas de K y L.
- La pregunta útil para el proyecto es si hay **menos servicios de los que tocarían por población** en una zona: intensidad observada frente a la modelizada con la población. Ese déficit es una variable con significado para el modelo y para el mapa de la Administración.
- Las capas de puntos de interés de datos abiertos pueden estar incompletas fuera de la ciudad (ver `dm-modelado-espacial`). Un «déficit» puede ser falta de dato.

## Python

`pointpats` (PySAL): `PointPattern`, funciones `G`, `F`, `K`, `L` con simulación, centrografía. Densidad kernel con `scipy.stats.gaussian_kde` o `sklearn.neighbors.KernelDensity`, siempre en EPSG:25830. DBSCAN con `sklearn.cluster.DBSCAN` sobre coordenadas en metros. En R (curso): `spatstat` (`ppp`, `Kest`, `Kinhom`, `envelope`, `ppm`).
