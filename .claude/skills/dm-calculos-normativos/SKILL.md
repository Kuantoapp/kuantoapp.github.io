---
description: Implementar, comprobar, simular e interpretar cualquier cálculo que aplica una norma, una tarifa o una convocatoria oficial, y fijar sus parámetros con cita a la fuente primaria. Por ejemplo, bruto a neto (cotizaciones, retención y cuota de IRPF), indicadores legales (SMI, IPREM, IMV, umbral de pobreza, sobrecarga de vivienda, índices de alquiler), requisitos y cuantías de ayudas o subvenciones, tarifas y precios públicos, impuestos y tasas, valor del tiempo. Úsala al escribir o cambiar uno de estos cálculos, al simular un cambio de regla o al dudar de una cifra legal. No es para el análisis espacial (dm-eda-espacial, dm-modelado-espacial).
when_to_use: Calcular el neto desde el bruto, ¿cuánto se retiene de IRPF?, ¿cuánto cotiza el trabajador?, 12 o 14 pagas, ¿cumple los requisitos de esta ayuda?, ¿cuántas veces el IPREM?, ¿cuánto cuesta este título de transporte?, ¿qué pasa si se acaba un descuento o cambia un umbral?, ¿está este hogar sobrecargado?, ¿qué umbral uso, 30 % o 40 %?, ¿cuánto vale una hora de viaje?, añadir un cálculo legal nuevo, actualizar los parámetros al año nuevo, ¿esta cifra legal está bien?
---

# Cálculos normativos

Un cálculo normativo aplica una regla que alguien publicó: una ley, un reglamento, una orden de tarifas o una convocatoria. Aquí no se estima nada: **o coincide con la norma al céntimo, o está mal**. Un error en uno de estos números (el neto de una nómina, un requisito de una ayuda) destruye la credibilidad de todo lo demás.

## Regla de oro

**Ninguna cifra legal sale de la memoria**, ni de la tuya ni de la de otro modelo. Cada parámetro (tipo, tramo, tope, umbral, precio, edad de corte) se toma de la **fuente primaria** y se guarda con su cita: norma, artículo o tabla, identificador BOE o BOCM, fecha de publicación, periodo de vigencia y URL. Lo que no se ha podido comprobar en la fuente se marca `verificado: False` y se dice en la salida.

Las tablas de [referencia/](referencia/) son una **instantánea** de lo investigado el 12/11/2026 para los cálculos que el proyecto preveía entonces, con su fuente y su estado. Son **punto de partida, no fuente**: antes de usar un valor en el código, comprueba que la norma citada sigue vigente para la fecha del cálculo. Si el proyecto necesita un cálculo que no está ahí, sigue el mismo método (sección «Ámbito nuevo o año nuevo»); no hace falta que esté en la referencia para hacerlo bien.

## Antes de empezar: conectar con el desarrollo del proyecto

Esta skill es general. Qué cálculos hacen falta y para qué perfil sale del estado actual del proyecto; no lo supongas ni lo copies de los ejemplos.

1. **Qué se calcula y para quién:** lee `docs/decisiones.md` (idea elegida, perfiles de hogar, año de referencia, simplificaciones aceptadas) y, si hace falta, la ficha vigente en `ideas/`. Las marcas «(verificar)» de las fichas son cifras sin comprobar: no las copies al código.
2. **Qué hay ya hecho:** busca y reutiliza antes de escribir:
   `grep -rniE "irpf|retenci|cotiza|seguridad_social|smi|iprem|imv|bono|tarifa|abono|umbral|sobrecarga|neto|bruto|valor_hora" src tests app`.
   Si ya hay un fichero de parámetros, se amplía; no se crea otro.
3. **Fecha del cálculo:** fija la fecha o el ejercicio al que se aplica la norma (devengo). Una regla vigente hoy puede no serlo en la fecha del dato, y al revés: SMI, IPREM, tarifas y escalas cambian cada año y a veces a mitad de año.
4. **Qué falta por decidir:** si el perfil (edad, situación familiar, tipo de contrato, número de pagas) o la simplificación aceptada no está decidida, **pregunta**; si tienes que suponer, deja el supuesto en el código y en `docs/decisiones.md`.

## Cómo se organiza en el código

- **Un único módulo de parámetros por año**, separado de la lógica (por ejemplo `src/<paquete>/normativa/parametros_2026.py` o un YAML). Cada valor con su cita y su estado:
  ```python
  SS_TRABAJADOR_CC = Parametro(
      0.0470,
      "Orden PJC/297/2026, art. 4.a)",
      "BOE-A-2026-7296",
      "2026-01-01",
      verificado=True,
  )
  ```
- **La lógica no contiene cifras legales**: solo lee parámetros. Cambiar de año es cambiar de fichero, no tocar funciones.
- **Dinero con `decimal.Decimal`** y el redondeo que diga la norma (normalmente al céntimo, mitad hacia arriba); el tipo de retención, como lo redondee el algoritmo oficial. `float` solo para agregados estadísticos, nunca para una cifra individual que se va a comparar al céntimo.
- **Funciones puras** (entrada → salida, sin leer ficheros ni red), vectorizables después sobre un DataFrame.
- **Requisitos que se explican:** una función de elegibilidad devuelve si cumple **y qué requisito falla** (con su artículo), no solo `True` o `False`. Así se puede contar por qué queda fuera cada caso.
- **Escenarios con las mismas funciones:** para simular un cambio de regla (otro umbral, un descuento que se acaba, un criterio nuevo), se pasa otro conjunto de parámetros a la misma función, con nombre propio (`escenario="sin_descuento"`). Nunca se copia la función para cambiar una cifra. El escenario oficial y el simulado se presentan juntos y el simulado se etiqueta como tal.

## Flujo para implementar un cálculo

1. **Identifica la norma exacta y su versión vigente** en la fecha del cálculo: texto consolidado del BOE, orden de tarifas, convocatoria. Si hay un algoritmo oficial publicado (el de retenciones de la AEAT), **ese es el procedimiento**, no la ley resumida.
2. **Transcribe los parámetros** al módulo de parámetros con su cita. Si [referencia/](referencia/) ya tiene el valor, compruébalo en la fuente antes de copiarlo.
3. **Implementa los pasos en el mismo orden que la norma**, con sus nombres (base, reducción, mínimo, cuota, tipo). Los redondeos, en el paso en que los hace la norma: redondear antes o después cambia céntimos.
4. **Casos de referencia antes que el código final:** al menos tres casos resueltos por la propia fuente (ejemplo de la norma, simulador oficial, nómina real anonimizada) como tests con tolerancia de un céntimo. Si el simulador oficial no da el caso, el test lo dice y queda marcado.
5. **Casos límite:** cada umbral exacto y un céntimo a cada lado (tramos, mínimo exento de retención, base mínima y máxima, renta máxima de una ayuda, precio máximo del alquiler, edad de corte el día del cumpleaños), 12 y 14 pagas, contrato temporal e indefinido, cambio de norma a mitad de año.
6. **Propiedades que deben cumplirse siempre** (tests con muchos valores, por ejemplo con `hypothesis` o una rejilla): ver la tabla de abajo.
7. **Declara las simplificaciones** en el código, en la app y en `docs/decisiones.md`: retención frente a cuota final del IRPF, situación familiar supuesta, deducciones que no se aplican, descuentos que dependen de una ayuda temporal.

## Ámbito nuevo o año nuevo

Cuando el proyecto pida un cálculo que la referencia no cubre, o cambie el año:

1. **Localiza la fuente primaria** del ámbito: BOE (texto consolidado y su versión en la fecha del cálculo), boletín autonómico, sede del organismo que lo aplica (AEAT, Seguridad Social, INE, consorcio de transportes, ayuntamiento) o la convocatoria. Prensa, blogs o asesorías solo sirven para encontrarla.
2. **Comprueba cambios recientes:** reales decretos-leyes que modifican la norma y si se convalidaron o derogaron, prórrogas presupuestarias, cambios a mitad de año. Son la causa más frecuente de cifras desfasadas.
3. **Transcribe** al módulo de parámetros del año con su cita y su estado; lo no confirmado, `verificado=False`.
4. **Casos de referencia** de la propia fuente, como en el flujo de abajo.
5. **Actualiza la referencia** de esta skill si el ámbito se va a reutilizar: un fichero por tema con la fecha de consulta, la tabla de valores con fuente y estado, y una sección final «No verificado». Para años nuevos, se crea la tabla nueva; la del año anterior se conserva mientras haya datos de ese año.

Para una búsqueda larga en la web, delega en un subagente que lea las fuentes y devuelva la tabla con citas; tú revisas el resultado y lo pasas al código.

## Contrastar cada resultado con lo que debe dar

Un resultado solo se acepta cuando coincide con la fuente o la diferencia está explicada y comprobada. El bucle es:

1. **Antes de ejecutar**, escribe qué esperas: el valor del caso oficial o, si no lo hay, el orden de magnitud y el signo según la norma.
2. **Ejecuta** y compara con el caso de referencia y con los **valores de control** de abajo.
3. **Si no cuadra**, no ajustes hasta que cuadre: localiza el paso que diverge (base, reducción, mínimo, tramo, redondeo, vigencia) comparando el intermedio con la fuente.
4. **Corrige** solo ese paso, con la cita que lo justifica, y vuelve al paso 2.
5. **Corrobora** con una segunda vía: otro caso oficial, el simulador de la AEAT, una nómina real, o el cálculo inverso (del neto al bruto).
6. **Registra** en `docs/decisiones.md` lo que se ajustó y por qué.

| Comprobación | Lo correcto | Si no se cumple |
|---|---|---|
| Neto frente a bruto | `0 < neto ≤ bruto`; el neto **crece** con el bruto (salvo saltos legales documentados) | Tramo, reducción o redondeo mal aplicados |
| Tipo efectivo de retención | No decrece con el bruto; entre 0 y el límite legal | Escala mal transcrita o reducción del art. 20 mal calculada |
| Cotización del trabajador | Suma de tipos × base, con la base acotada entre la mínima y la máxima del grupo | Tipos o topes de otro año; base sin prorrata de extras |
| 12 frente a 14 pagas | Mismo neto **anual**; distinto neto mensual | Prorrata de pagas extra mal hecha |
| Caso oficial (simulador, ejemplo de la norma) | Igual al céntimo | Paso divergente: compara intermedios |
| Umbral exacto de una ayuda | El caso en el umbral cae del lado que dice la norma («hasta», «inferior a», «no superior a») | Comparación `<` frente a `≤` invertida |
| Múltiplos de IPREM o SMI | Con el IPREM o SMI **del ejercicio que dice la norma** y con 12 o 14 pagas según indique | Año o modalidad equivocados |
| Tarifas | Precio del título de la zona del origen y del destino, con o sin descuento según la fecha | Zona mal asignada o descuento caducado |
| Esfuerzo o sobrecarga | Mismo numerador y denominador que la definición citada (renta neta o bruta, del hogar o de la persona, con o sin ayudas) | Indicador no comparable con la cifra oficial |

Guía de lectura y errores frecuentes: [interpretar-resultados.md](referencia/interpretar-resultados.md).

## Al terminar: dejar el trabajo conectado

- Lógica en `src/`, parámetros en su módulo por año y tests con los casos de referencia en `tests/`, según `AGENTS.md`.
- Las simplificaciones y el año de los parámetros, en `docs/decisiones.md` y visibles en la app («cálculo de retención 2026, no cuota final»).
- Antes de dar el cálculo por bueno o de abrir el PR, pide la revisión de `dm-auditor-calculos-normativos`.

## Errores que invalidan un resultado

- Una cifra legal escrita a mano en la lógica, sin cita, o copiada de prensa, de una asesoría o de un LLM.
- Parámetros de otro año o de una norma derogada; IPREM de 12 pagas donde la norma pide 14, o al revés.
- Presentar la **retención** como el IRPF que se paga al final, o aplicar la escala de la declaración donde va la de retenciones.
- Mezclar retención y declaración: la **retención** de la nómina usa solo la escala única del art. 101 LIRPF y los mínimos estatales (sin escala autonómica); la **cuota final** usa escala estatal más la de la comunidad, con sus mínimos. Usar la escala de Madrid en la nómina, o la de otra comunidad en la declaración, es un error.
- Base de cotización sin topes o sin prorrata de pagas extra.
- Requisito de una ayuda evaluado con un ingreso distinto del que cuenta la convocatoria (individual frente a unidad de convivencia, bruto frente a base imponible, ejercicio equivocado).
- Un descuento temporal (por ejemplo, de transporte) tratado como permanente sin decirlo.
- Indicador de esfuerzo con un denominador distinto del oficial y comparado con la cifra oficial.
- Sin tests de casos límite: los errores de estos cálculos viven en los umbrales.

## Referencia

Instantánea del 12/11/2026 (España y Comunidad de Madrid). Cada fichero empieza con su contenido y termina con lo que quedó sin verificar.

| Tema | Fichero |
|---|---|
| Bruto a neto: cotizaciones y retención de IRPF (estatal y Madrid) | [nomina-bruto-a-neto.md](referencia/nomina-bruto-a-neto.md) |
| SMI, IPREM, IMV, renta mínima, umbral de pobreza, sobrecarga, IRAV, zonas tensionadas, salarios | [indicadores-y-umbrales.md](referencia/indicadores-y-umbrales.md) |
| Bono Alquiler Joven, Plan Estatal de Vivienda, deducciones por alquiler | [ayudas-vivienda.md](referencia/ayudas-vivienda.md) |
| Tarifas de transporte, valor del tiempo, IBI y Catastro, bono social y pobreza energética | [transporte-tiempo-y-otros.md](referencia/transporte-tiempo-y-otros.md) |
| Cómo leer los resultados y qué ajustar | [interpretar-resultados.md](referencia/interpretar-resultados.md) |
