# Verificación: licencia de la información del INE

> Qué licencia tienen los datos del INE y qué cita exigen, comprobado en el aviso legal del INE. Es una de las verificaciones de Kuanto; qué significa cada estado y el resto están en el [índice](README.md).

Sigue a [#147](https://github.com/yeraybc/DataMad-hackaton-2026/issues/147); la decisión está en [`docs/decisiones.md`](../decisiones.md) (entrada del 2026-11-16, «Licencia de los datos derivados del INE: CC BY 4.0»).

- **Fecha de consulta:** 2026-11-16.
- **Método:** la sesión principal leyó en bruto, con `curl` y `python`, el aviso legal del INE, el pie de sus páginas y el final de cada CSV y del zip del seccionado que usa el proyecto. Las páginas se leyeron en HTML estático y las 7 (las 5 tablas, la cartografía y el aviso legal) se renderizaron además con Chrome headless (`--dump-dom`, que ejecuta JavaScript).

## 1. Aviso legal canónico

`https://www.ine.es/aviso_legal` redirige (meta refresh) a `https://www.ine.es/dyngs/AYU/index.htm?cid=125`, la página que también enlaza datos.gob.es en el campo «Licencia» de los conjuntos del INE. Su apartado de reutilización dice CC BY 4.0, y el cuerpo del aviso remite a él toda reutilización. Copia literal del 2026-11-16, primera frase y condiciones:

> La licencia de uso general a aplicar a la información estadística de este sitio web, salvo que se indique lo contrario, es la Creative Commons Reconocimiento 4.0 (CC BY 4.0) que implica la autorización para la reutilización de la información en condiciones no restrictivas, siendo posible la copia, distribución y comunicación pública, así como la producción de obras derivadas, incluso con finalidad comercial citando la autoría. Esta reutilización podrá tener objeto comercial o no comercial y se realizará siempre bajo las siguientes condiciones generales: Debe citarse la fuente de la información objeto de reutilización. Esta cita podrá realizarse de la siguiente manera: Fuente: Sitio web del INE: www.ine.es si no se realiza ningún tratamiento de los datos o bien: Elaboración propia con datos extraídos del sitio web del INE: www.ine.es en caso de que se realice tratamiento de los datos. Debe mencionarse la fecha de la última actualización de la información objeto de reutilización, siempre y cuando estuviera incluida en el original. No se podrá indicar, insinuar o sugerir que el INE participa, patrocina o apoya la reutilización que se lleve a cabo con la información. La utilización de los conjuntos de datos se realizará por parte de los usuarios o agentes de la reutilización bajo su propia cuenta y riesgo, correspondiéndoles en exclusiva a ellos responder frente a terceros por daños que pudieran derivarse de ella. El INE no será responsable del uso que de su información hagan los agentes reutilizadores ni tampoco de los daños sufridos o pérdidas económicas que, de forma directa o indirecta, produzcan o puedan producir perjuicios económicos, materiales o sobre datos, provocados por el uso de la información reutilizada. Los agentes reutilizadores se hallan sometidos a la normativa aplicable en materia de reutilización de la información del sector público, incluyendo el régimen sancionador previsto en el artículo 11 de la Ley 37/2007, de 16 de noviembre, sobre reutilización de la información del sector público. El INE se reserva el derecho a modificar estas condiciones de licencia para la información en cualquier momento y sin previo aviso.

Remisión desde el cuerpo del aviso: «quien desee reutilizar cualquier contenido de este sitio web deberá atenerse a lo dispuesto en el apartado "Reutilización de la información contenida en este sitio web" de este aviso legal». En «Derechos de propiedad intelectual» se exige autorización escrita para reutilizar «el diseño de este sitio web y su código fuente, como los logos, marcas y demás signos distintivos»: se refiere al diseño, el código y los logos, no a los datos.

SHA-256 del texto extraído: `9450eccd93b3aa9d64448bf7ea86806004d91c085d3a9b3a2e35e3d9d69c72d5`. Sirve para comparar en la próxima relectura (comprobado de nuevo el 2026-11-16; releído el 2026-11-21 antes de publicar, mismo SHA-256, sin cambios: [#198](https://github.com/yeraybc/DataMad-hackaton-2026/issues/198)). Para reproducirlo:

```sh
curl -sL 'https://www.ine.es/dyngs/AYU/es/index.htm?cid=125' | python3 -I -c 'import sys,re,html,hashlib;t=re.sub(r"\s+"," ",html.unescape(re.sub(r"<[^>]+>"," ",sys.stdin.read())));i=t.find("La licencia de uso general");j=t.find("Legislación aplicable");print(hashlib.sha256((t[i:j].strip()+"\n").encode()).hexdigest() if i>=0<j else "NO ENCONTRADO: el aviso ha cambiado")'
```

La relectura antes de publicar está en [#198](https://github.com/yeraybc/DataMad-hackaton-2026/issues/198).

## 2. Versión antigua, todavía accesible

`https://www.ine.es/ss/Satellite?L=es_ES&c=Page&cid=1254735849170&p=1254735849170&pagename=Ayuda%2FINELayout` es la que cita `.claude/skills/dm-verificacion-fuentes/referencia/licencias.md` (consultada el 12-11). No nombra ninguna licencia Creative Commons en el texto y añade una condición que la nueva no tiene: «Se prohíbe expresamente desnaturalizar el sentido de la información». El proyecto la cumple igualmente, porque no cambia el sentido de las cifras. Manda la canónica, a la que redirige `/aviso_legal`.

## 3. Pie de las páginas

En todas las páginas revisadas, el enlace y los iconos del pie van a `creativecommons.org/licenses/by/4.0`. En el HTML estático (`curl`), el texto «Este sitio web y su contenido están bajo licencia CC BY-SA 4.0» está solo en el atributo `title` del enlace. Renderizada con JavaScript, la página lo muestra a la vista, y el enlace sigue yendo a BY 4.0. Habla del sitio, no de la información estadística.

## 4. ¿Avisos propios?

El aviso dice «salvo que se indique lo contrario», así que se miró si alguna fuente trae el suyo. En ninguna hay aviso propio: se aplica la general (CC BY 4.0). Vale también para la página renderizada con Chrome headless: en las tablas y en la cartografía, la única mención de licencia es la del pie.

| Fuente | Qué se miró | Resultado |
|---|---|---|
| Tabla 31097 (renta, ADRH) | Página `jaxiT3/Tabla.htm?t=31097` y final del CSV de `data/raw` | Solo el pie general y «© 2026 INE»; el CSV son solo datos, sin notas |
| Tabla 31105 (demográficos, ADRH) | Igual | Igual |
| Tabla 37727 (Gini, ADRH) | Igual | Igual |
| Tabla 68542 (Censo, edad) | Igual | Igual |
| Tabla 76137 (IPC) | Igual | Igual |
| Seccionado 2025 | Página de descarga de cartografía del INE (Satellite `cid=1259952026632`) y lista del zip `ine_seccionado_2025_2026-11-15.zip` | La página solo tiene el pie general; el zip solo trae el shapefile (`.shp`, `.shx`, `.dbf`, `.prj`, `.cpg`, `.sbn`, `.sbx`), sin licencia ni léame |

## 5. Conclusión

Se mantiene CC BY 4.0 para todo lo del INE que usa el proyecto. La relectura antes de publicar (26-11), comparando el SHA-256 del texto, está en [#198](https://github.com/yeraybc/DataMad-hackaton-2026/issues/198).
