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
├── personas.parquet
├── laboral_ingresos.parquet
├── informacion_crediticia.parquet
├── geografia_hogar.parquet
└── csv/                                  las 4 tablas exportadas, sin transformar
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
