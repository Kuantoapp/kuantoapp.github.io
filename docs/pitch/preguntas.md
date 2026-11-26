# Preguntas probables del jurado y respuestas

Una respuesta corta, en voz alta, y la diapositiva del anexo que la apoya (tecla `A`).

## Rigor (Lorenzo Escot)

**¿El esfuerzo del alquiler está subiendo?** [^serpavi]
- El 19,6 % es de la ciudad de Madrid: alquiler mediano de contratos declarados entre la renta neta media del hogar. [^serpavi]
- De las 142 zonas con dato en los dos años, sube en 68. [^cambio]
- Solo 31 suben más que su margen de error, y la mediana del cambio es casi cero. Lo decimos en el informe: el esfuerzo se mantiene; no se dispara. [^cambio]

**¿Cómo sabéis que el neto está bien?**
- Hemos calculado a mano 8 casos completos, de 17.094 a 80.000 € brutos, con el IRPF estatal y el de Madrid y las cotizaciones de 2026. [^metodo]
- La interpolación de la web se separa menos de 1 € al mes del cálculo exacto. [^metodo]

**¿Qué fiabilidad tiene el alquiler por zona?**
- Es la mediana de contratos declarados (SERPAVI), no de anuncios.
- Las zonas con menos de 70 alquileres declarados se marcan como imprecisas (39 de 158). [^metodo]
- La web enseña la horquilla P25–P75, y donde no hay dato sale en gris, nunca como cero. [^metodo]

**¿p = 0,82 quiere decir que el Bono funciona igual en todas partes?** [^bono]
- Quiere decir que no se aprecia relación entre la proporción aceptada y el esfuerzo del alquiler del municipio. No prueba que no la haya, y hay un indicio de que se pide más donde el alquiler pesa más (estimado). [^bono]
- Publicamos 9 especificaciones, también las que no salen significativas, con el registro previo hecho antes de ver el resultado. [^bono]

**¿Cuánto os fiáis de los tiempos de viaje?**
- Salen de r5py sobre los GTFS del CRTM.
- Se reconstruyen horarios en el 21,5 % de los pares con ruta. [^metodo]
- En una prueba con 494 viajes, el error medio fue de 20,7 minutos (estimado). [^metodo]

## Viabilidad (Olga Quirós)

**¿Quién lo usa y quién lo paga?**
- Lo usa quien busca piso, sobre todo jóvenes.
- También la Administración: Vivienda (dónde no llega el Bono), el CRTM (qué pasa si se acaba el descuento), Juventud y los ayuntamientos.
- Alojarlo cuesta 0 €, porque es una web estática sin servidor. [^sdm]
- Mantenerlo es un calendario: tarifas de cada año, IPC mensual, GTFS y SERPAVI anual.

**¿Y si cambian las tarifas o los datos?**
- `python -m mesobra` comprueba que las descargas coinciden por SHA-256 y regenera todos los ficheros.
- La nota metodológica dice qué caduca y cuándo.

## Datos abiertos e interoperabilidad (Alberto Abella)

**¿Qué conjuntos del catálogo regional usáis?**
- La EPF (cesta básica, dentro del cálculo).
- El Bono Alquiler Joven 2022.
- La población por edad y el Colectivo Empresarial.
- Los GTFS del CRTM, a los que enlaza el catálogo.
- El indicador de renta, como control. [^fuentes]

**¿Smart Data Models, DCAT-AP y MCP son reales o de adorno?**
- Son reales: 1.670 entidades NGSI-LD `KeyPerformanceIndicator`, validadas contra el esquema publicado. [^sdm]
- El catálogo está descrito en DCAT-AP (`app/datos/dcat.jsonld`).
- El servidor MCP tiene tres herramientas, que responden con las mismas cifras de la web. [^sdm]

## Privacidad y método de trabajo

**¿Guardáis el sueldo de alguien?**
- No. No hay servidor, cuentas ni analítica: la cuenta se hace en el navegador.
- La política de seguridad de contenido impide que la página hable con otros dominios.
- Lo único que se guarda en el equipo es si prefieres el tema claro u oscuro.

**¿Lo ha hecho una IA?**
- El código lo escriben agentes, sí. Pero otros agentes lo auditan: un abogado del diablo, un auditor de cálculos normativos y un trazador de cifras, entre otros.
- La CI no deja fusionar nada sin el veredicto del revisor de su área.
- Las decisiones las tomamos nosotros y quedan fechadas en `docs/decisiones.md`.

**¿Por qué no usar ChatGPT directamente?**
- Lo probamos: miró de 4 a 6 zonas y erró el neto un 2,1 % (Gemini) y un 3,9 % (ChatGPT). [^ia]
- Con el MCP, una IA puede usar las cifras de Kuanto en vez de inventarlas. [^ia]

[^serpavi]: SERPAVI (MIVAU) y ADRH (INE), 2024; `docs/informe/cifras.md`.
[^cambio]: `docs/informe/cifras.md`, cap. 4 y 5: sube en 68 de 142; 31 suben más que su error; mediana del cambio −0,06 puntos (estimado).
[^metodo]: `app/metodologia.html` (Validación y Límites) y `docs/informe/cifras.md`, cap. 2 y 12.
[^bono]: `docs/informe/cifras.md`, cap. 8 y 9: GLM, p = 0,82; 9 especificaciones (G7). Estimado.
[^sdm]: `app/datos/sdm` (158 + 1.512 entidades); nota metodológica, «Mantenimiento».
[^fuentes]: `data/README.md` y `docs/decisiones.md` (2026-11-16, requisito del catálogo).
[^ia]: `docs/kuanto-frente-a-ia.md`, prueba del 25-11-2026 con cuatro respuestas.
