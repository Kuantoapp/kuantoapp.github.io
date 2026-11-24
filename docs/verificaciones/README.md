# Verificaciones

Antes de usar un dato, una norma o una licencia, el equipo comprobó cada afirmación en la fuente original: la web del publicador, el fichero descargado o el boletín oficial. Esta carpeta guarda esas comprobaciones con su evidencia. Es para quien quiera saber hasta qué punto está contrastado lo que dice Kuanto.

## Cómo leerlas

Cada fichero es una tabla de afirmaciones con su estado:

- **VERIFICADO:** el publicador dice lo mismo.
- **FALSO:** el publicador lo contradice. Al lado va el texto corregido y qué cambia para el proyecto.
- **NO VERIFICADO** o **SIN EVIDENCIA:** no se encontró publicado donde debería estar.

Las referencias como «§16 de la ficha» o «F0-04» remiten a la [ficha de la idea](../../ideas/plan1/idea-definitiva/propuesta-A-unificada.md) y a las issues del repositorio, porque las verificaciones se hicieron para corregir esa ficha antes de construir nada. El código cita estos ficheros donde usa lo comprobado.

## Qué se comprobó

| Fichero | Qué se comprobó | Qué se corrigió gracias a ello |
|---|---|---|
| [`renta-vivienda.md`](renta-vivienda.md) | El Bono Alquiler Joven, la renta del INE por sección, la sobrecarga de los inquilinos, el régimen de tenencia, el IPC del alquiler, la cesta de la EPF y la población joven por municipio | El dataset del Bono no dice por qué se rechazaron las solicitudes, y la falta de presupuesto no es la única causa. La tasa de sobrecarga de los inquilinos de la Comunidad no está publicada, así que se calcula con los microdatos de la ECV. Un dataset de tenencia que citaba la ficha no existe con ese identificador |
| [`movilidad-interoperabilidad.md`](movilidad-interoperabilidad.md) | La licencia del CRTM, los distritos de Madrid, Smart Data Models, la encuesta de movilidad del CRTM, los datos de movilidad del Ministerio de Transportes y el valor del tiempo | La encuesta de movilidad de 2018 no publica una matriz de viajes utilizable; los datos del Ministerio no tienen licencia CC BY; las guías de evaluación no valoran el tiempo como decía la ficha |
| [`transporte-colectivos.md`](transporte-colectivos.md) | Los precios de 2026 de cada título y colectivo en el BOCM, la familia numerosa, el abono de Renfe y la discapacidad | No hay descuento del CRTM para familias monoparentales en 2026, así que ese colectivo paga la tarifa ordinaria |
| [`licencia-ine.md`](licencia-ine.md) | Qué licencia tienen los datos del INE y qué cita exigen | Confirma CC BY 4.0, que es la licencia de los datos que Kuanto deriva del INE |

Cada fichero dice su fecha de consulta y su método. Las hizo el agente `dm-verificador-fuentes`, y después se volvió a leer en bruto cada cifra citada. Las dudas de fuentes que surgen después se resuelven igual y quedan en el [registro de decisiones](../decisiones.md).
