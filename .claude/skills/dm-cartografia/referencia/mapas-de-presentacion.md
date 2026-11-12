# Mapas para presentar

Basado en el tema 3 del curso y en Chasco (2025). Para mapas que sirven para explorar, ver `dm-eda-espacial`.

## Elegir la clasificación

| Método | Cuándo | Cuidado |
|---|---|---|
| **Cuantiles** | Comparar posiciones; variables más o menos simétricas | Falla con distribuciones muy asimétricas o con muchos valores repetidos: aparecen clases vacías o desiguales |
| **Cortes naturales** (Jenks, Fisher) | Grupos homogéneos dentro de cada clase | La leyenda debe mostrar intervalos semiabiertos `[a, b)` |
| **Intervalos iguales** | Escala con significado propio (euros, minutos) | Con colas largas, casi todo cae en una clase |
| **Head/tail breaks** o escala logarítmica | Colas muy largas (población, número de solicitudes) | Explícalo en la leyenda |
| **Punto medio** | Variables con un centro con significado: 0, un porcentaje de referencia | Con paleta divergente |
| **Continua** | Solo para distribuciones simétricas | Con asimetría, casi todo el mapa sale de un color |

- 5 a 7 clases. Más no se distinguen.
- Compara al menos dos clasificaciones antes de elegir: si el patrón cambia mucho, el mapa engaña.

## Elegir la paleta (ColorBrewer, cols4all)

- **Secuencial:** un solo tono, de claro a oscuro. Para magnitudes en una dirección (precio, tiempo de viaje).
- **Divergente:** dos tonos que se separan desde un centro. Para saldos positivos o negativos, o «por encima / por debajo» de un umbral. Pone el foco en los extremos.
- **Cualitativa:** colores sin orden. Para categorías sin jerarquía (tipo de municipio).
- **Ordinal:** para categorías con orden. Categorías como coronas tarifarias, tramos de renta o niveles de prioridad son ordinales: usa una secuencial por pasos, no una cualitativa.
- El rojo se lee como peligro o alarma. Resérvalo para lo que de verdad lo es, no para un valor neutro.
- Apta para daltónicos: evita el par rojo-verde.

## Lo que engaña al ojo

- **El área pesa más que la población.** Las zonas rurales grandes ocupan mucho mapa con poca gente. Soluciones:
  - **cartograma** contiguo (conserva vecindades), no contiguo (conserva formas) o **de Dorling** (círculos proporcionales en el centroide; el más fácil de leer);
  - **mapa de símbolos graduados:** un círculo por zona proporcional a la población, coloreado por la variable.
- **Tasas de zonas con poca población:** extremos sin significado. Pinta la tasa suavizada (ver `dm-eda-espacial`).

## Casos frecuentes

- Variable con signo o con un umbral con significado (saldo positivo o negativo, porcentaje por encima de una referencia): divergente centrada en ese valor, clasificación por punto medio o intervalos iguales en la unidad original; los umbrales relevantes, marcados en la leyenda.
- Residuos o errores de un modelo: divergente centrada en 0.
- Valores estimados o imputados: trama o borde y la palabra «estimado» al consultar la zona; las que caen fuera del área de aplicabilidad del modelo, diferenciadas.
- Leyenda con unidad y método de clasificación; fuente bajo el mapa; «© OpenStreetMap contributors» si se usa OSM.
