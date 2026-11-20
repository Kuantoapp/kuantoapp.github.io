# Verificaciones: precios del transporte por colectivo (2026)

Evidencia de [#163](https://github.com/yeraybc/DataMad-hackaton-2026/issues/163) (PR [#286](https://github.com/yeraybc/DataMad-hackaton-2026/pull/286)). Sostiene los precios por colectivo de `src/mesobra/transporte.py` y la línea del 18-11 de [decisiones](../decisiones.md).

- **Fecha de consulta:** 2026-11-18, la misma en todas las filas.
- **Método:**
  - La sesión principal descargó los dos BOCM y transcribió sus tablas con `pdftotext -layout`.
  - `dm-verificador-fuentes` comprobó en la fuente primaria las afirmaciones legales (filas 2 a 5).
  - `dm-auditor-calculos-normativos` volvió a descargar los PDF y cruzó cada cifra del código con otra extracción, `pdftotext -table`, que alinea mejor las columnas del 10 viajes y del sencillo.
- **Estados:**
  - VERIFICADO: coincide entera.
  - FALSO: el publicador la contradice.
  - SIN EVIDENCIA: no se encontró, pero ninguna cifra depende de ello.

## 1. Tablas de precios del BOCM

| Documento | Qué trae | SHA-256 del PDF |
|---|---|---|
| BOCM-20251231-2, págs. 65-68: precios con la bonificación del RDL 17/2025 ([PDF del CRTM](https://www.crtm.es/media/s1qi0nmo/bocm-20251231-precios_transporte.pdf)) | Abono 30 días (normal e interzonales), Joven, 10 viajes y sencillo | `11dff8cab49afb680b0663cf37d561e16a5bee5e1a670abddcf3095ff6a63f7d` |
| BOCM-20251231-3, págs. 69-72: tarifas oficiales, sin bonificación ([PDF del CRTM](https://www.crtm.es/media/sjqj4ggj/bocm-20251231-tarifas_transporte.pdf)) | Lo mismo, más el multiviaje de Castilla y León | `c8e8bc79433e65befe1b88be88fdbb35d872ec8a2a8d3ee0f1cb997630388a0c` |

**Estado: VERIFICADO.**

- **Columnas:** las dos resoluciones traen 6 columnas en todas esas tablas: ordinario («Sin descuento» en el abono del -3), discapacidad, FN general, FN especial, FN general + discapacidad y FN especial + discapacidad.
- **Discapacidad:** el umbral es «superior o igual al 65%». En el 10 viajes y el sencillo la columna dice solo «Discapacidad».
- **Sencillo:** no lleva la bonificación del RDL («Quedan fuera del ámbito de aplicación del Real Decreto-Ley [...] los billetes sencillos», pág. 65), pero sí precio por colectivo (pág. 68 del -2 y pág. 71 del -3).
- **Sin colectivo:** la Tarjeta Azul (precio único), los títulos gratuitos y el billete turístico.
- **Cotejo del auditor:** 76 combinaciones de título y escenario de `ABONO_30`, `ABONO_INTERZONAL`, `ABONO_JOVEN`, `DIEZ_VIAJES`, `DIEZ_VIAJES_INTERURBANO`, `UNA_ZONA` y `SENCILLO`, cada una con sus 6 columnas. 0 diferencias.

**Por qué la columna y no un porcentaje:** ningún redondeo sencillo del factor reproduce el BOCM.
- Con «redondear a la baja a 0,10 €» fallan 14 de las 340 celdas de colectivo. Por ejemplo, el abono A para FN especial + discapacidad cuesta 9,70 € y 32,70 × 0,3 = 9,81.
- Con el 50 %, el sencillo de 1,50 € para FN especial sería 0,75 €; el BOCM dice 0,70 €.
- Lo que sí se cumple en todas las celdas, y es lo que comprueba `test_colectivos_en_banda_y_en_orden`:
  - cada precio está entre factor × ordinario − 0,11 € y factor × ordinario;
  - el orden es ordinario > discapacidad = FN general > FN general + discapacidad > FN especial > FN especial + discapacidad.
  - Los factores son 0,8, 0,8, 0,6, 0,5 y 0,3, y se deducen de las tablas: el BOCM no los publica.

## 2. Familia monoparental en Madrid

**Estado: FALSO para 2026.** No hay descuento del CRTM. Queda fuera del cálculo y su colectivo es «ordinario».

- **BOCM:** la palabra «monoparental» no aparece en ninguno de los dos (búsqueda en el texto extraído).
- **CRTM:** la [página de descuentos](https://crtm.es/billetes-y-tarifas/tarifas/descuentos/) no la menciona.
- **Comunidad de Madrid:** según el portal de transparencia, el proyecto de decreto de 2020 que regulaba el título de familia monoparental está en «Archivo/Desistimiento» ([ficha](https://www.comunidad.madrid/transparencia/decreto-que-se-regula-procedimiento-reconocimiento-y-acreditacion-familias-monoparentales-comunidad)). Lo leyó `dm-verificador-fuentes`; el auditor no pudo volver a comprobarlo (SIN EVIDENCIA en su pasada), pero ninguna cifra depende de ello.
- **Desde 2027:** el RDL 35/2026 ([BOE-A-2026-23604](https://www.boe.es/buscar/act.php?id=BOE-A-2026-23604)) añade a la Ley 40/2003 un art. 2.2.c, por el que es numerosa la familia con «una sola» persona progenitora «con dos hijas o hijos», con efectos desde el 1-1-2027 (disposición final 10.2). No se comprobó si el Congreso lo ha convalidado.

## 3. Cuándo es numerosa una familia con 2 hijos

**Estado: VERIFICADO.** Fuente: Ley 40/2003, [BOE-A-2003-21052](https://www.boe.es/buscar/act.php?id=BOE-A-2003-21052), en la redacción vigente en 2026 (la anterior al RDL 35/2026).

- **Art. 2.2, supuestos con 2 hijos:**
  - a) uno o dos ascendientes con al menos un hijo con discapacidad o «incapacitado para trabajar»;
  - b) los dos ascendientes con discapacidad (o uno con grado «igual o superior al 65 por ciento») o incapacitados para trabajar;
  - el padre o la madre con dos hijos, «cuando haya fallecido el otro progenitor»;
  - d) y e) hermanos huérfanos.
- **Categoría:** es general. Excepción: con los dos hijos con discapacidad, cada uno «computará como dos» (art. 4.3), la familia cuenta como de 4 hijos y es especial si la renta por miembro no supera «el 75 por ciento del salario mínimo interprofesional» (art. 4.2).
- **Consecuencia:** el número de hijos no basta para asignar el colectivo. Quien use la tabla (#164) tiene que preguntarlo o dejar «ordinario».

## 4. Abono mensual de Renfe por colectivo

**Estado: VERIFICADO.** No tiene precio por colectivo.

- **Precio:** las preguntas frecuentes de Renfe (`https://www.renfe.com/es/es/promociones/abonos-renfe/abonos-bonificados/preguntas-frecuentes`; sin enlace, sus condiciones lo prohíben) dicen que el «importe de venta del Abono mensual será de 20 €», y el RDL 17/2025 ([BOE-A-2025-26459](https://www.boe.es/diario_boe/txt.php?id=BOE-A-2025-26459)), art. 3.2.a.2.º, fija una «tarifa única 20 euros».
- **Familia numerosa:** de los descuentos, «se podrá aplicar únicamente el de Familia Numerosa», pero no se publica su importe.
- **Discapacidad:** no tiene descuento.
- **Consecuencia:** el código usa 20 € para todos los colectivos. Para familia numerosa es una cota superior.

## 5. Discapacidad del 33 al 64 %

**Estado: VERIFICADO.** El BOCM solo tiene columna para un grado igual o superior al 65 % (fila 1). Del 33 al 64 % se paga el precio ordinario y no se modela aparte.
