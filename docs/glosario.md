# Glosario

Los términos que salen en Kuanto y en su documentación, explicados en una o dos frases. Están ordenados por tema.

## Dinero y normas

- **Sueldo bruto:** lo que figura en el contrato antes de descontar nada, en euros al año.
- **Sueldo neto:** lo que llega a la cuenta después de restar las cotizaciones y el IRPF. Kuanto lo da al mes: el neto del año entre 12, aunque cobres en 14 pagas.
- **Cotizaciones:** la parte del sueldo que el trabajador paga a la Seguridad Social y que financia pensiones, desempleo y bajas.
- **IRPF:** el impuesto sobre la renta. Cada mes, la empresa te retiene una parte de la nómina como adelanto del impuesto; al hacer la declaración se calcula lo que de verdad te toca pagar en el año (la cuota) y te devuelven o pagas la diferencia. Kuanto usa la cuota anual, no la retención. El motivo está en la [nota metodológica](https://kuantoapp.github.io/metodologia.html#titulo-cuota).
- **SMI (salario mínimo interprofesional):** el sueldo mínimo que fija el Gobierno cada año. Interviene en el cálculo del neto de los sueldos bajos.
- **IPREM:** un índice oficial que sirve para fijar quién puede pedir una ayuda. Por ejemplo, el Bono Alquiler Joven exige ingresos de hasta tres veces el IPREM (fuente: [informe de análisis](https://kuantoapp.github.io/informe.html#titulo-simulacion), BOCM-20250110-20).
- **Bono Alquiler Joven:** una ayuda al alquiler para jóvenes de 18 a 35 años, regulada por el RD 42/2022 y convocada por la Comunidad de Madrid. El informe compara dónde se pidió y se concedió con dónde más cuesta el alquiler.
- **Cesta básica:** lo que gasta un hogar en comida, luz, gas, agua, teléfono e Internet. Sale de la Encuesta de Presupuestos Familiares y se ajusta al tamaño del hogar.
- **Unidades de consumo:** la forma de comparar hogares de distinto tamaño. El primer adulto cuenta 1, cada persona adicional de 14 años o más 0,5 y cada menor de 14 años 0,3; Kuanto cuenta cada hijo como 0,3 (escala OCDE modificada; fuente: [nota metodológica](https://kuantoapp.github.io/metodologia.html#titulo-supuestos)). Por ejemplo, una pareja con un hijo pequeño suma 1 + 0,5 + 0,3 = 1,8: gasta como 1,8 personas que vivieran solas, no como 3, porque comparten casa, nevera y facturas.
- **Esfuerzo de alquiler:** la parte del ingreso que se va en el alquiler (alquiler ÷ neto). Con 1.617 € netos y 896 € de alquiler, el esfuerzo es del 55 %: más de la mitad del sueldo (estimado; el ejemplo de Getafe de [Cómo funciona](como-funciona.md#un-ejemplo)).
- **Sobrecarga:** cuando un hogar dedica a la vivienda más del 40 % de su renta (fuente: [informe de análisis](https://kuantoapp.github.io/informe.html#titulo-sobrecarga), ECV 2025 del INE).
- **Lo que sobra:** neto menos alquiler, menos transporte y menos cesta básica, en euros al mes. Es la cifra principal de Kuanto.

## Fuentes de datos

- **SERPAVI:** el Sistema Estatal de Referencia del Precio del Alquiler de Vivienda, del Ministerio de Vivienda y Agenda Urbana. Da el precio del metro cuadrado de los alquileres declarados a Hacienda, por municipio, distrito y sección censal.
- **ADRH:** el Atlas de Distribución de Renta de los Hogares del INE. Da la renta de los hogares y la población por sección censal.
- **EPF:** la Encuesta de Presupuestos Familiares del INE, que mide en qué gastan los hogares.
- **ECV:** la Encuesta de Condiciones de Vida del INE. Con ella se calcula la sobrecarga de los inquilinos.
- **IPC:** el Índice de Precios de Consumo del INE. Kuanto lo usa para llevar a hoy precios de años anteriores.
- **GTFS:** el formato estándar en que los operadores publican rutas, paradas y horarios del transporte público. Kuanto usa los del Consorcio Regional de Transportes de Madrid (CRTM).
- **OpenStreetMap:** un mapa libre hecho por voluntarios. Kuanto toma de él las calles y los edificios.
- **BOE y BOCM:** el Boletín Oficial del Estado y el de la Comunidad de Madrid, donde se publican las normas y las tarifas.

## Territorio y transporte

- **Zona:** cada uno de los 199 lugares que compara Kuanto: los 178 municipios distintos de la capital y los 21 distritos de Madrid (fuente: [`zonas.geojson`](../app/datos/LEEME.md#zonasgeojson)).
- **Sección censal:** la unidad territorial más pequeña de las estadísticas del INE: un trozo de barrio o un pueblo pequeño. Kuanto las agrega en zonas.
- **Centro de población:** el punto de cada zona desde el que se miden los viajes. Es el centro de donde vive la gente, no el centro geográfico: en un municipio grande con mucho monte, el centro geográfico puede caer en pleno campo, lejos de cualquier casa y de cualquier parada.
- **Corona tarifaria:** cada anillo del mapa de tarifas del CRTM. Las zonas de Kuanto están en A, B1, B2, B3, C1 y C2 (fuente: [`zonas.geojson`](../app/datos/LEEME.md#zonasgeojson)). El precio del abono depende de las coronas que cruzas.
- **r5py:** la biblioteca de Python que calcula los tiempos de viaje en transporte público y en coche a partir de los horarios y del mapa de calles.

## Kuanto por dentro

- **Estimado:** la marca de las cifras que salen de un modelo o de un supuesto en vez de un dato publicado tal cual.
- **Horquilla:** el rango entre un alquiler barato y uno caro de la misma zona, que da un sobrante alto y uno bajo. Técnicamente son los cuartiles 25 y 75 (en una zona estimada, el intervalo de la estimación si es más ancho): de cada cuatro pisos de la zona, uno cuesta menos que el extremo barato, uno más que el caro y dos están entre medias.
- **Zona de referencia:** la zona con la que se compara el resto en el precio de la hora. Por defecto es la zona desde la que menos tardas en llegar al trabajo, y en el formulario se puede cambiar, por ejemplo por donde vives ahora.
- **Precio de la hora:** cuánto dinero ganas (o pierdes) al mes por cada hora más de viaje si vives en una zona en vez de en la de referencia. Es lo que pinta el mapa al abrir. Explicado con un ejemplo en [Cómo funciona](como-funciona.md#qué-quiere-decir-127--por-cada-hora-extra).
- **API estática:** los ficheros de datos que publica Kuanto en la web, que cualquiera puede descargar y que la propia web lee. No hay servidor ni base de datos detrás.
- **MCP (Model Context Protocol):** un estándar para que un asistente de IA use herramientas externas. El servidor MCP de Kuanto permite preguntar a un asistente con las mismas cifras que la web.
- **Smart Data Models:** un esquema común para publicar indicadores urbanos de forma que otras plataformas los entiendan. Kuanto publica en él sus indicadores de alquiler y esfuerzo.
- **SHA-256:** la huella digital de un fichero. Si dos personas tienen la misma huella, tienen exactamente el mismo fichero.
