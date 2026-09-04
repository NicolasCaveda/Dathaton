# Datathon UCU–ITBA · Kredo Argentina

Carpeta de trabajo del equipo. Acá está la consigna, los datos provistos por Equifax y el
notebook de carga y diagnóstico.

**El problema:** Kredo, fintech de crédito al consumo, entra a Argentina y va a abrir entre
3 y 10 sucursales físicas en los próximos 12 meses. Hay que decidir **dónde, cuántas, en qué
orden, con qué producto y para qué cliente**, y respaldarlo con los datos.

---

## Contenido de la carpeta

```
Dathaton/
├── README.md                             este archivo
├── 202609 - Consigna estudiantes Datathon.docx.pdf
├── 01_carga_y_diagnostico.ipynb          carga, exporta a CSV y diagnostica
├── 02_limpieza_y_maestro.ipynb           limpieza y tabla maestra
├── personas.parquet
├── laboral_ingresos.parquet
├── informacion_crediticia.parquet
├── geografia_hogar.parquet
├── csv/                                  las 4 tablas exportadas, sin transformar
└── maestro_personas.parquet / .csv       UNA FILA POR PERSONA · salida del notebook 02
```

---

## Cómo arrancar

1. Abrir `01_carga_y_diagnostico.ipynb` **desde esta carpeta** (el notebook usa rutas relativas).
2. Correr la celda de la sección 0. Instala `pyarrow` si falta, que es el motor que pandas
   necesita para leer `.parquet`.
3. **Si la celda instaló algo, reiniciar el kernel antes de seguir.** Instalar pyarrow con el
   kernel ya andando y continuar sin reiniciar produce
   `ArrowKeyError: A type extension with name pandas.period already defined`.
4. `Run All`.

La primera corrida tarda unos 3 minutos porque escribe 172 MB de CSV. Las siguientes bajan a
menos de un minuto: la celda de exportación se saltea los archivos que ya existen.

> **Plan B sin instalar nada.** Los CSV ya están en `csv/` y `pd.read_csv` no necesita pyarrow.
> Cambiando `pd.read_parquet(f"{t}.parquet")` por `pd.read_csv(f"csv/{t}.csv")` el notebook
> corre igual, solo más lento.

---

## Qué representan los datos

**Cada fila es una persona en un momento dado.** `id_persona` es un identificador sintético
—no es un DNI, es un código que inventó Equifax para poder unir las tablas sin identificar a
nadie— y `periodo` dice de qué corte es esa foto. Las cuatro tablas comparten esas dos
columnas, y esa es toda la estructura.

No hay tabla de sucursales, ni de localidades, ni de ventas, ni de clientes de Kredo: la
empresa todavía no operó un solo día en Argentina. Lo que hay es una muestra de **674.546
argentinos** mirados desde cuatro ángulos.

### La tensión central

**Los datos son sobre personas; la decisión es sobre lugares.** Todo el trabajo analítico
consiste en traducir de una unidad a la otra.

El puente es una sola columna: `cp`, en `geografia_hogar`. Es lo único que ancla a cada persona
a un territorio. Con ella se puede agarrar cualquier atributo individual y calcular cómo se ve
en promedio en cada código postal. Ahí el dataset deja de ser una lista de gente y se convierte
en **47 mercados candidatos**, cada uno con su perfil.

```
4 tablas          ──join id_persona+periodo──▶   tabla maestra
(personas)                                       674.546 filas, 1 por persona
                                                        │
                                                 agrupar por cp
                                                        ▼
                                                 47 plazas candidatas
                                                 1 fila por código postal
                                                        │
                                                 índice y ranking
                                                        ▼
                                                 cuántas · cuáles · en qué orden
                                                 qué producto · para qué cliente
```

### Qué aporta cada tabla

| Tabla | Qué es | Para qué sirve en la decisión |
|---|---|---|
| `personas` | Demografía: edad y género | La edad media de la plaza cambia el negocio. Entre las 47 plazas va de 36 a 50 años. |
| `laboral_ingresos` | Capacidad de pago y formalidad | Define el **mix de producto**. El prendario necesita recibo de sueldo y garantía; relación de dependencia con ingreso medio-alto es el candidato natural. |
| `informacion_crediticia` | Comportamiento y demanda | Dos cosas: la **calidad** como deudor (score, y `bancarizacion` HIT/THIN — el THIN es el mercado clásico de una fintech) y la **demanda activa** (solicitudes de financiamiento en 6/12/24m). |
| `geografia_hogar` | El ancla territorial | El `cp` es la unidad de decisión. Las variables de hogar sirven para perfilar consumo, pero faltan en el 71% de los registros. |

### Ejemplo de lectura

| | CP 3500 | CP 1425 |
|---|---|---|
| Personas | 21.072 | 24.319 |
| Edad media | 43,3 | 50,3 |
| Pidió crédito en 12m | **48,0%** | 37,8% |
| Score bueno | 36,8% | **85,2%** |

Dos negocios distintos. El 3500 es demanda insatisfecha con riesgo alto: préstamo personal de
monto bajo, aprobación rápida, volumen. El 1425 es lo opuesto: cartera excelente, gente mayor,
poco apetito: prendario, tickets grandes, la sucursal cierra operaciones en vez de captar
volumen. Ese contraste —**calidad de cartera contra demanda activa**— es el eje del ranking.

### Lo que el dataset NO tiene

No hay costos de sucursal, competencia, población total de cada localidad, ventas ni márgenes,
y no hay ubicación dentro de la ciudad: el CP es todo el detalle geográfico que existe.

Eso no es una carencia del ejercicio, es donde entran los supuestos y las fuentes externas, que
la consigna permite explícitamente. Los datos dicen dónde está el mercado; el número de
sucursales sale de un supuesto de cuánto cuesta abrir una y cuántos clientes necesita para
cerrar. Ese supuesto lo pone el equipo y lo tiene que poder defender.

---

## Qué hace `01_carga_y_diagnostico.ipynb`

**Principio: medir antes de tocar.** El notebook no limpia nada, y es deliberado. Si limpiás
mientras explorás, terminás sin saber qué había originalmente ni por qué decidiste cada cosa.
La rúbrica pide justamente lo contrario: detectar los problemas, explicarlos y justificar el
tratamiento. La limpieza va en un segundo notebook, con las decisiones ya tomadas.

| Sección | Qué hace |
|---|---|
| **0. Dependencias** | Instala `pyarrow` si falta, en el intérprete del kernel. |
| **1–2. Carga y exportación** | Levanta los cuatro parquet y los escribe en `csv/`. La exportación se saltea si el CSV ya existe y es más nuevo que el parquet. |
| **3. Perfil por tabla** | `perfil()` recorre columna por columna: tipo, % de nulos, cardinalidad y valores más frecuentes. Con eso solo aparecen tres tipos de problema: columnas con demasiados nulos, columnas sin varianza, y categorías mal codificadas. |
| **4. Cobertura temporal** | ¿Es un panel o un corte transversal apilado? Se agrupa por persona y se cuenta cuántos períodos distintos tiene cada una. |
| **5. Chequeos de coherencia** | Buscar cosas que **no pueden ser verdad** y contarlas: más líneas de crédito a 12 meses que a 24, personas jubiladas y en relación de dependencia a la vez, edades que bajan entre períodos. |
| **6. Señal vs. ruido** | Antes de ponderar variables, chequear si discriminan. Para las numéricas: comparar la distribución por CP. Para las categóricas: tabla de contingencia contra una variable con la que deberían relacionarse. |
| **7. Disponibilidad por plaza** | En vez del promedio de la variable por CP, el **% de no-nulos** por CP. Ahí aparece el hallazgo principal. |
| **8. Tabla maestra y foto de plazas** | Último registro por persona, `left join` desde `personas`, score unificado. 674.546 filas, una por persona, y de ahí el agregado por `cp`. |
| **10. Hallazgos consolidados** | Tabla resumen para pegar en el log de decisiones. |

---

## Qué hace `02_limpieza_y_maestro.ipynb`

Toma los cuatro `.parquet` crudos y produce **`maestro_personas.parquet`** (15 MB, el formato
de trabajo) y **`maestro_personas.csv`** (195 MB, para abrir en Excel): **674.546 filas, una por
persona, 56 columnas**.

**Nada se borra.** Todos los problemas detectados se marcan con banderas booleanas en lugar de
eliminar filas, así cada analista decide si filtra y el criterio queda explícito en el código
en vez de escondido en una limpieza previa.

Las decisiones de limpieza están todas juntas como constantes al principio del notebook, para
poder discutirlas y cambiarlas en un solo lugar:

| Constante | Qué controla | Valor actual |
|---|---|---|
| `ORDEN_PERIODOS` | Cuál es el registro "más reciente" | 2025-06 < 2025-12 < 2026-06 |
| `DESCARTAR_SIN_PERIODO` | Qué hacer con las filas de crédito sin fecha | `False` (se conservan y se marcan) |
| `TOL_EDAD_ANIOS` | Desvío a partir del cual una edad se considera error de tipeo | `2` años |
| `EDAD_MAX_PLAUSIBLE` | Valor al que se imputan las edades más altas | `90` |
| `PCT_TOPE` | Percentil de topeo de líneas de crédito | `0.99` (tope = 14 líneas) |
| `COLS_A_DESCARTAR` | Columnas que salen del maestro | `es_pasivo`, `tiene_obra_social_o_prepaga` |
| `COLS_ESTABLES` | Qué campos se completan desde períodos previos | `genero`, `cp`, composición del hogar |
| `REESCRIBIR_CSV` | Fuerza a regenerar el CSV de 195 MB | `False` |
| `UMBRAL_PLAZA_CIEGA` | Cobertura mínima para considerar que la plaza tiene el bloque | `0.05` |

### Cómo se trata la edad

Dos pasos, en orden. **Primero se corrige:** los períodos están separados por seis meses, así
que la edad de una persona solo puede subir 0 o 1 año entre observaciones consecutivas. Para
cada persona con más de un período se calcula la edad de referencia —la mediana de sus edades
ajustadas por el tiempo transcurrido— y toda observación que se desvíe más de 2 años se
reemplaza por el valor reconstruido. Eso corrige casos como 42 → 43 → **19**, donde la mayoría
de las observaciones deja claro cuál es la edad real: se corrigieron **852 observaciones de 791
personas**.

**Después se topea:** lo que siga por encima de 90 se imputa a 90. Son **9.749 personas** con
edades internamente consistentes (100 → 101 → 102) pero implausibles, y sin un segundo período
con qué contrastarlas no hay forma de saber si son reales. Se conserva `edad_original` y quedan
las banderas `edad_corregida_por_tipeo` y `edad_topeada`.

### Fuentes externas: población y competencia

Dos columnas que no vienen de Equifax y se pegan a nivel plaza, así que todas las personas de
un mismo `cp` comparten el valor.

**`cantidad_habitantes_cp`** — población del Censo 2022, de
`fuentes_externas/censo_2022_poblacion/poblacion_por_cp.csv`. Ese archivo trae una columna
`metodo` que documenta cómo se estimó cada valor (departamento completo, localidad censal, o
reparto proporcional entre barrios en CABA). Las 47 plazas suman **12.477.195 habitantes**.

**`cantidad_competidores`** — sucursales de la competencia dentro de cada plaza, desde
`Locaciones competidor.xlsx`, que solo trae `id_locacion`, `latitud` y `longitud`. Las siete
coordenadas se geocodificaron una por una contra Nominatim/OpenStreetMap; el resultado quedó
fijo dentro del notebook para que corra sin conexión.

El empalme se hace **por ciudad, no por código exacto**. El sistema CPA moderno subdivide las
ciudades grandes —Córdoba capital usa 5000, 5001, 5002— mientras que el dataset tiene un único
código por plaza. Un competidor en Alta Córdoba tiene CPA 5001 pero está dentro de la plaza
5000, que agrupa a toda la ciudad, así que suma. El que cayó en Mendoza no, porque Mendoza no
es una de las 47 plazas. Resultado: **6 de 7 competidores contados, en 5 plazas**.

Las plazas sin competencia quedan en **0, no en nulo**: el cero es información y un nulo
rompería cualquier promedio.

### El hallazgo que habilita la población

**La penetración de la muestra va de 1,1% a 31,5% según la plaza.** No es pareja ni cerca: la
mediana es 4,4% y el máximo es veintiocho veces el mínimo.

| CP | En la muestra | Habitantes | Penetración |
|---|---|---|---|
| 1828 | 19.210 | 61.072 | **31,5%** |
| 1425 | 24.311 | 81.349 | 29,9% |
| 2300 | 2.090 | 190.577 | 1,1% |
| 1763 | 2.202 | 207.478 | **1,1%** |

Por tamaño de muestra, el CP 1828 parece nueve veces más grande que el 1763. Por población
real, el 1763 es tres veces y media más grande que el 1828.

**41 de las 47 plazas cambian de puesto** al rankear por población en lugar de por muestra. El
CP 1425 cae del puesto 8 al 36; el 1828, del 15 al 42. La correlación de rangos entre ambos
criterios es +0,771: alta, pero muy lejos de 1.

Conclusión operativa: **rankear plazas por cantidad de personas en el dataset está mal**. El
tamaño de mercado se calcula sobre la población, y la muestra sirve para estimar tasas —
porcentaje bancarizado, porcentaje que pidió crédito, mix de ingreso— que después se aplican a
esa población.

### Los dos "score" no son lo mismo

`score_riesgo` se normalizó en dos pasos: sacar el prefijo `SCORE_` (convivían `SCORE_ALTO` y
`ALTO` como si fueran niveles distintos) y mapear a `score_ordinal` de 1 a 5. La dirección se
verifica sobre los datos, no se asume: la correlación de Spearman con el ingreso da **+0,395**,
o sea que **ALTO es mejor perfil, no más riesgo**, pese al nombre de la columna.

`score_fraude` **no se tradujo a ordinal, a propósito**: el 85% de la muestra es "MUY BAJO", así
que no discrimina entre plazas. Si tuviera ordinal, alguien lo mete en el índice y suma ruido
con apariencia de señal. **Ojo con la polaridad: acá ALTO es malo**, al revés que en
`score_riesgo`. Promediarlos juntos no significa nada.

`score_riesgo_promedio_hogar` traía el mismo problema y peor: **tres grafías del mismo nivel**
conviviendo (`MEDIO-ALTO`, `MEDIO_ALTO`, `SCORE_MEDIO_ALTO`) más una categoría `NO_DEFINIDO`.
Se aplicó la misma regla que al individual —unificar prefijo y separador— y `NO_DEFINIDO` pasó
a nulo. Pasó de 13 valores distintos a 5, y quedó `score_hogar_ordinal` para poder promediarlo.

### Código postal ambiguo

**8.913 personas (1,3%) figuran en dos códigos postales distintos dentro del mismo período**, y
no son barrios vecinos: hay casos de CABA contra Salta, o Córdoba contra Rosario. El
desduplicado se queda con la fila más completa y, cuando empatan en cantidad de nulos, con la
primera que aparece.

Decisión del equipo: se mantiene ese criterio y **se marca con la bandera `cp_ambiguo`**. Las
personas quedan en el maestro, pero se pueden excluir con un filtro de cualquier cálculo por
plaza donde la asignación importe.

### Relleno desde períodos anteriores

Si el último registro de una persona tiene menos datos que uno anterior, se completan **solo
los atributos que no deberían cambiar**: `genero`, `cp`, `cantidad_personas_hogar`,
`cantidad_menores_hogar` y `edad_promedio_hogar`. Todo lo que evoluciona —ingreso, score,
situación laboral, demanda de crédito— queda con el valor del último período, sin tocar.

Quedaron fuera del relleno a propósito `score_riesgo_promedio_hogar` y
`categoria_ingreso_lider_hogar`: son del bloque de hogar, pero evolucionan igual que el score y
el ingreso individuales, así que completarlos sería mezclar dos momentos distintos. Se
recuperaron **1.272 valores** que de otro modo se habrían perdido.

### Sobre el CSV

El `.parquet` se regenera en cada corrida porque es barato. El `.csv` pesa 195 MB y tarda
varios minutos, así que solo se escribe si falta, si quedó más viejo que los datos crudos, o si
ponés `REESCRIBIR_CSV = True`. **Si cambiás una regla de limpieza y querés el CSV actualizado,
tenés que activar ese flag**: el parquet solo no alcanza para quien trabaje desde el CSV.

### Situación laboral

Los flags quedan **como vienen**, incluso cuando hay más de uno en TRUE: no se deriva una
etiqueta única ni se aplica ninguna prioridad. Que alguien figure en relación de dependencia y
como monotributista a la vez puede ser real —recibo de sueldo más facturación por cuenta
propia— y son **13.952 personas**. La bandera `laboral_multiple` las identifica.

Las columnas `es_pasivo` y `tiene_obra_social_o_prepaga` se descartan del maestro por decisión
del equipo.

### Columnas que agrega

Además de los atributos originales normalizados, el maestro trae tres grupos nuevos:

- **Derivadas para el análisis** — `ingreso_ordinal` y `score_ordinal` (1 a 5, para poder
  promediar), `pidio_credito_12m`, `es_thin`, `grupo_etario`, `lineas_activas_12m_cap`.
- **Banderas de calidad** — `edad_corregida_por_tipeo`, `edad_topeada`, `laboral_multiple`,
  `cp_ambiguo`, `lineas_incoherentes`, `credito_sin_periodo`, `tiene_datos_hogar`, más
  `edad_original` para poder auditar cualquier cambio.
- **Disponibilidad por plaza** — `plaza_tiene_ingreso` / `_laboral` / `_score`,
  `cobertura_*_plaza`, `patron_plaza` y `plaza_completa`. Cada persona se lleva pegada la
  información de qué bloques tiene **su plaza**, para que ninguna agregación posterior compare
  plazas que no son comparables.

La última celda del notebook es un **diccionario de columnas** con la descripción de cada una y
una advertencia explícita sobre las que son ruido. Vale la pena leerlo antes de meter una
columna en el índice de atractivo.

### Un detalle que conviene confirmar

La columna se llama `score_riesgo`, lo que sugeriría que ALTO es malo. Los datos dicen lo
contrario: la correlación de Spearman entre score e ingreso es **+0,395**, y el 99,7% de la
gente de ingreso ALTO está bancarizada. O sea que **ALTO = mejor perfil crediticio**. El
notebook verifica esa dirección sobre los datos en vez de asumirla, pero vale la pena
confirmarlo con los organizadores antes de la presentación.

---

## Hallazgos principales

**1. La falta de datos está organizada por localidad, no por persona.** Hay códigos postales
donde una variable está al 99,8% y códigos postales donde está al 0,4%. No hay término medio.
Solo **29 de las 47 plazas tienen los tres bloques** (ingreso, laboral y score). Tucumán, La
Plata, Salta y el CP 1425 no tienen categoría de ingreso; trece plazas del conurbano y del NEA
no tienen situación laboral.

*Implicancia:* un índice que combine esas variables compara plazas que no son comparables y
castiga en silencio a las ciegas. El ranking va a estar decidido por dónde hay datos, no por
dónde conviene abrir. La salida es construir el índice con las variables presentes en las 47
plazas y usar el resto en una segunda capa que solo compare plazas del mismo patrón.

**2. Dos variables son ruido puro.**
- `distancia_estimada_polo_comercial_km`: uniforme entre 0 y 5 km, con media 2,47–2,55 y desvío
  1,44 en las 47 plazas. Cero nulos y cero información. Es la trampa más tentadora del dataset.
- `segmento_comportamiento_retail`: 25/25/25/25, y al cruzarlo con la categoría de ingreso todas
  las celdas caen entre 24,6% y 25,3%. Está asignado al azar.

**3. `score_riesgo` tiene dos codificaciones conviviendo.** 536.260 registros usan el prefijo
(`SCORE_ALTO`) y 268.965 no (`ALTO`), para los mismos cinco niveles. Sin unificar, cada nivel
queda partido al medio.

**4. No es un panel.** Hay tres cortes, pero el 84,9% de las personas aparece en uno solo. Se
trabaja con el último registro de cada persona.

**5. Otros problemas a resolver.** 70.212 filas de la tabla crediticia sin `periodo`; 30.276
duplicados en `laboral_ingresos`; las columnas de líneas activas a 24 y 36 meses son idénticas
y hay 62.261 filas con 12m > 24m; 27.934 personas con dos situaciones laborales a la vez;
edades de hasta 129 años. En cambio, la escalera de solicitudes 6m/12m/24m **sí** es coherente.

**6. Lo que sí tiene señal.** El score se mueve con el ingreso (67,7% de score alto entre
ingreso ALTO contra 2,2% entre ingreso BAJO) y las variables discriminan fuerte entre plazas:
score bueno de 21,5% a 85,2%, ingreso alto de 6,8% a 34,8%, edad media de 36 a 50 años.

---

## Decisiones pendientes antes del notebook 02

- [ ] **Qué hacer con las 18 plazas ciegas.** Índice de dos capas, imputación con caveat, o
      análisis solo sobre las 29 completas. Es la decisión más importante del día.
- [ ] **Qué período se usa** y qué se hace con las filas de la tabla crediticia sin período.
- [ ] **Regla de prioridad laboral** cuando una persona tiene dos flags en verdadero.
- [ ] **Ventana de líneas de crédito** (12 o 24 meses) y criterio de topeo de outliers.
- [ ] **AMBA: una plaza o muchas.** Buena parte de los 47 CPs son del área metropolitana;
      agregarlos o no cambia el ranking entero. Es una decisión de negocio, no técnica.
- [ ] **Muestra contra población.** El dataset es una muestra de Equifax, no la población. Hay
      que traer población real por localidad y trabajar con tasas en lugar de conteos.

## Próximo paso

El notebook `02_limpieza_y_agregacion.ipynb` aplica esas decisiones y produce las dos salidas
que consume el resto del equipo:

- `maestro_personas.csv` — una fila por persona, con el registro más reciente de cada tabla.
- `plazas.csv` — una fila por CP, con todas las métricas agregadas del mercado.

A partir de ese momento nadie vuelve a leer los `.parquet` crudos.
