# Interpretar y ajustar cálculos normativos

Cómo leer cada resultado, qué suele estar mal cuando no cuadra y qué ajustar. Las cifras concretas están en los otros ficheros de esta carpeta, con su fuente.

## Diagnóstico por síntoma

| Síntoma | Causa probable | Cómo comprobarlo | Qué ajustar |
|---|---|---|---|
| El neto difiere del simulador de la AEAT en unos euros al año | Redondeo del tipo de retención en otro paso, o gastos deducibles distintos | Compara la base para calcular el tipo, la cuota y el tipo intermedio con los del simulador | El redondeo o el paso concreto, con la cita del algoritmo |
| Difiere en cientos de euros | Escala de otro año o comunidad, reducción por rendimientos del trabajo mal calculada, mínimo personal equivocado | Recalcula a mano la cuota con la escala citada | El parámetro, desde la fuente |
| El neto baja al subir el bruto | Error en la reducción del art. 20 (tramo decreciente), en el límite de retención o en la base máxima | Rejilla de brutos cada 100 € y busca el salto | El tramo; si el salto es legal (umbral de una ayuda), documéntalo |
| Sale retención en un sueldo muy bajo, o una retención alta para ese sueldo | No se aplica la exclusión de retención del art. 81 o el límite del 43 % del art. 85.3. Ojo: que haya retención **puede ser correcto** (el límite del art. 81 puede quedar por debajo del SMI del año) | Caso en el límite del art. 81 y en el SMI, contra el simulador de la AEAT | Aplicar exclusión y límite según el algoritmo |
| El neto mensual no coincide con una nómina real pero el tipo sí | La nómina usa la situación familiar o el contrato que comunicó el trabajador, o regularizó a mitad de año | Pide el tipo de la nómina y la situación comunicada | Ninguno si el tipo cuadra; declara el supuesto |
| Cotización fija en sueldos altos que no cuadra | Base máxima de otro año o sin cotización adicional de solidaridad | Caso por encima de la base máxima | Topes y tipos del año |
| 12 y 14 pagas dan distinto neto anual | La prorrata de extras solo se aplicó en una modalidad | Suma anual en ambas | Prorrata en la base de cotización; retención sobre el total anual |
| Un hogar en el umbral exacto queda fuera de una ayuda | `<` donde la norma dice «no superior a» | Test en el umbral | La comparación |
| Elegibilidad que no cuadra con datos oficiales de concesión | Ingreso o unidad distintos de la convocatoria (persona frente a unidad de convivencia, ejercicio fiscal anterior) | Releer el artículo de requisitos | El ingreso usado |
| Tasa de sobrecarga muy distinta de la oficial | Numerador o denominador distinto (renta bruta frente a disponible, persona frente a hogar, con o sin ayudas, alquiler frente a todos los costes de vivienda) | Reproducir la definición oficial con un hogar tipo | Alinear con la definición o no comparar con la cifra oficial |

## Lectura de resultados

- **Retención no es impuesto.** La retención es un pago a cuenta calculado con la situación que el trabajador comunica; la cuota final sale de la declaración. Para «lo que entra en la cuenta cada mes», la retención es lo correcto; dilo así en la app.
- **Neto mensual frente a anual.** Con 14 pagas, el neto de un mes normal es menor que el anual ÷ 12. Si se compara con un gasto mensual (alquiler, transporte), decide y declara cuál usas; lo coherente para un saldo mensual medio es el **anual ÷ 12**.
- **Saltos legales.** Algunas reglas tienen escalones (perder una ayuda al pasar un umbral). Un salto ahí no es un error, pero hay que mostrarlo porque cambia decisiones.
- **Descuentos temporales.** Si un precio depende de una ayuda con fecha de fin, el resultado tiene dos lecturas: con y sin la ayuda. Muestra las dos o di cuál usas.
- **Umbrales convencionales frente a legales.** El 30 % del esfuerzo es una convención (y criterio de la Ley 12/2023 para zonas tensionadas, sobre la renta media); el 40 % es la definición de Eurostat sobre la renta disponible. No son intercambiables: cita cuál usas.
- **Cifras con fecha.** Toda cifra legal mostrada lleva su año («SMI 2026»). Un resultado sin fecha caduca sin avisar.

## Antes de presentar una cifra legal

1. El parámetro tiene cita y está vigente para la fecha del cálculo.
2. Un caso oficial reproduce el cálculo al céntimo.
3. Los límites están probados.
4. La simplificación está declarada.
5. `dm-auditor-calculos-normativos` dio APTO o APTO CON RESERVAS con las reservas resueltas o declaradas.
