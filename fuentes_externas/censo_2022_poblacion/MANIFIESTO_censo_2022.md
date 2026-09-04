# Manifiesto — Población Censo 2022 por provincia (para las 47 plazas)

Carpeta destino: `fuentes_externas/censo_2022_poblacion/`

Para cada jurisdicción: entrar al link, buscar la tabla equivalente al "Cuadro 1.1" (Total de
población por departamento/partido/comuna, con la variación intercensal 2010-2022) y guardar el
archivo (PDF o XLSX, lo que ofrezca la página) en esta carpeta con el nombre indicado.

Nota: censo.gob.ar tiene un certificado SSL que mis herramientas de fetch/browser no pueden
validar — hay que bajarlos a mano desde un navegador normal (Chrome/Edge), igual que hiciste con
el de CABA.

| # | Jurisdicción | CPs que cubre (de tus 47) | Link | Nombre de archivo sugerido |
|---|---|---|---|---|
| 0 | CABA (ya la tenés) | 1405, 1406, 1407, 1408, 1425, 1427, 1429, 1430 | (ya descargado) | `caba.pdf` (o el que ya bajaste, solo copialo/movelo acá) |
| 1 | Buenos Aires (provincia) — la más grande, cubre GBA + La Plata + Mar del Plata + Bahía Blanca + Zárate/Campana | 1609, 1613, 1615, 1617, 1653, 1665, 1678, 1686, 1704, 1712, 1716, 1722, 1744, 1752, 1763, 1824, 1828, 1852, 1875, 1881, 1888, 1900, 2800, 2804, 7600, 8000 | https://censo.gob.ar/index.php/datos_definitivos_bsas/ | `buenos_aires.pdf` |
| 2 | Santa Fe (Rosario, Rafaela, Santa Fe capital) | 2000, 2300, 3000 | https://censo.gob.ar/index.php/datos_definitivos_santafe/ | `santa_fe.pdf` |
| 3 | Córdoba | 5000 | https://censo.gob.ar/index.php/datos_definitivos_cordoba/ | `cordoba.pdf` |
| 4 | Tucumán | 4000 | https://censo.gob.ar/index.php/datos_definitivos_tucuman/ | `tucuman.pdf` |
| 5 | Salta | 4400 | https://censo.gob.ar/index.php/datos_definitivos_salta/ | `salta.pdf` |
| 6 | Corrientes | 3400 | https://censo.gob.ar/index.php/datos_definitivos_corrientes/ | `corrientes.pdf` |
| 7 | Chaco (Resistencia) | 3500 | https://censo.gob.ar/index.php/datos_definitivos_chaco/ | `chaco.pdf` |
| 8 | Neuquén | 8300 | https://censo.gob.ar/index.php/datos_definitivos_neuquen/ | `neuquen.pdf` |
| 9 | La Rioja | 5300 | https://censo.gob.ar/index.php/datos_definitivos_larioja/ | `la_rioja.pdf` |
| 10 | San Luis (Villa Mercedes) | 5730 | https://censo.gob.ar/index.php/datos_definitivos_sanluis/ | `san_luis.pdf` |
| 11 | Río Negro (Bariloche) | 8400 | https://censo.gob.ar/index.php/datos_definitivos_rionegro/ | `rio_negro.pdf` |
| 12 | Chubut (Trelew) | 9100 | https://censo.gob.ar/index.php/datos_definitivos_chubut/ | `chubut.pdf` |

**Total: 47/47 CPs cubiertos.** La provincia de Buenos Aires concentra 26 de las 47 plazas (todo
el conurbano + La Plata + costa atlántica + Bahía Blanca), así que esa descarga es la más
importante de todas.

## Después de bajarlos

Una vez que estén los 13 archivos acá, decime y armo la tabla `cp -> departamento/partido/comuna
-> poblacion_real` cruzando cada uno con la lista de correspondencia CP-localidad (ese es el paso
que sigue: comuna/departamento no es lo mismo que código postal).

## Pendiente aparte (no depende de la descarga)

Validar con Equifax la dirección de `score_riesgo` (ver charla del jueves) — sigue sin resolver.
