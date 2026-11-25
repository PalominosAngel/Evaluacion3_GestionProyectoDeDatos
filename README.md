# Mall Customers Analytics — Segmentación de Clientes

**Evaluación Parcial 3 · Gestión de Proyectos de Datos (SCY1102) · Duoc UC**

Proyecto orientado a la **segmentación de clientes de un centro comercial**, utilizando técnicas de análisis exploratorio, preparación de datos y aprendizaje no supervisado mediante **K-Means**.

El proyecto utiliza el dataset **Mall Customers**, compuesto por 200 clientes, y busca identificar grupos con características similares según **edad, ingreso anual y Spending Score**, con el propósito de generar información útil para apoyar futuras decisiones del área de marketing.

**Integrantes:** María José Álvarez · Benjamín Arratia Santibáñez · Benjamín Díaz · Ángel Palominos Soto

---

## Objetivo del proyecto

El objetivo principal es desarrollar un piloto de segmentación de clientes que permita identificar patrones de comportamiento y perfiles diferenciados dentro de la muestra disponible.

Para ello se consideran tres variables principales en el modelo:

- Edad.
- Ingreso anual.
- Spending Score.

Estas variables son estandarizadas antes de aplicar K-Means, evitando que las diferencias de escala influyan de forma desproporcionada en la formación de los clusters.

El proyecto contempla además:

- Exploración y preparación de los datos.
- Tratamiento y análisis de categorías `Unknown`.
- Selección del número de clusters.
- Aplicación de K-Means.
- Evaluación mediante coeficiente de silueta.
- Descripción de los clusters obtenidos.
- Revisión de su distribución por género.
- Visualización de resultados mediante un dashboard interactivo.

---

## Estructura del proyecto

```text
proyecto/
├── data/
│   └── raw/
│       ├── Mall Customers.xlsx        Fuente original
│       └── mall_customers.csv         Fuente utilizada por la aplicación
│
├── notebooks/
│   └── analisis_exploratorio.ipynb    Exploración, preparación y modelado
│
├── dashboard/
│   └── app.py                         Aplicación Streamlit
│
├── src/
│   ├── data_loader.py                 Carga y preparación de datos
│   ├── model.py                       Modelo K-Means compartido
│   ├── theme.py                       Sistema visual y estilos
│   ├── capture_dashboard.js           Utilidad para capturas
│   ├── render_figures.js              Utilidad para renderizar figuras
│   └── figures/
│
├── images/
│
├── run.sh                             Lanzador macOS / Linux
├── run.bat                            Lanzador Windows
├── requirements.txt
└── README.md
```

---

# Ejecución

## Requisito

Tener instalado **Python 3.11 o superior**:

<https://www.python.org/downloads/>

El proyecto instala automáticamente sus dependencias dentro de un entorno virtual.

---

## Ejecución con un solo comando

1. Descomprimir la carpeta del proyecto.
2. Abrir una terminal dentro de la carpeta.
3. Ejecutar:

| Sistema | Comando |
|---|---|
| macOS / Linux | `./run.sh` |
| Windows PowerShell | `.\run.bat` |
| Windows CMD | `run.bat` |
| Windows | También puede ejecutarse `run.bat` con doble clic |

Durante la primera ejecución se crea el entorno virtual y se instalan las dependencias.

Una vez iniciado, el dashboard estará disponible en:

```text
http://localhost:8501
```

Si el navegador no se abre automáticamente, ingresar manualmente esa dirección.

Para detener la aplicación:

```text
Ctrl + C
```

En macOS o Linux, si aparece `permission denied`, ejecutar una sola vez:

```bash
chmod +x run.sh
```

---

## Qué hace el lanzador

Los archivos `run.bat` y `run.sh`:

1. Detectan una instalación compatible de Python.
2. Crean el entorno virtual `.venv/`.
3. Instalan las dependencias definidas en `requirements.txt`.
4. Ejecutan la aplicación Streamlit.
5. Cargan el dataset desde `data/raw/`.

El dashboard se inicia mediante:

```bash
streamlit run dashboard/app.py
```

---

## Ejecución manual

También es posible iniciar el proyecto manualmente.

### Crear entorno virtual

```bash
python -m venv .venv
```

### Activar entorno

macOS / Linux:

```bash
source .venv/bin/activate
```

Windows:

```powershell
.venv\Scripts\activate
```

### Instalar dependencias

```bash
pip install -r requirements.txt
```

### Ejecutar dashboard

```bash
streamlit run dashboard/app.py
```

---

# Fuente de datos

El proyecto utiliza el dataset **Mall Customers**, compuesto por:

| Archivo | Registros | Variables |
|---|---:|---:|
| `Mall Customers.xlsx` | 200 | 7 |
| `mall_customers.csv` | 200 | 7 |

Las variables originales son:

```text
CustomerID
Gender
Age
Education
Marital Status
Annual Income (k$)
Spending Score (1-100)
```

El archivo `.xlsx` se conserva como fuente original.

El archivo `.csv` contiene la misma información y es utilizado por la aplicación para facilitar la carga de datos.

---

# Preparación de los datos

La preparación se realiza principalmente desde:

```text
src/data_loader.py
```

El proceso mantiene los **200 registros originales** y evita realizar eliminaciones automáticas que puedan afectar la representatividad de la muestra.

---

## CustomerID

`CustomerID` se conserva únicamente como identificador.

No participa en el modelo K-Means, debido a que no representa una característica del comportamiento del cliente.

---

## Gender

La variable de género se conserva para análisis descriptivo y revisión posterior de la distribución de los clusters.

**Gender no participa en el entrenamiento del modelo K-Means.**

Esto permite analizar posteriormente si los segmentos presentan concentraciones relevantes por género sin utilizar esta característica directamente para construir los clusters.

---

## Education y Marital Status

Las variables:

```text
Education
Marital Status
```

contienen registros con categoría:

```text
Unknown
```

Estos valores se conservan en el dataset.

No afectan directamente al modelo K-Means porque ninguna de estas variables se utiliza para construir los clusters.

Su presencia se mantiene documentada como una limitación de calidad de los datos.

---

# Variables utilizadas para K-Means

El modelo utiliza exclusivamente:

```text
Age
Annual Income (k$)
Spending Score (1-100)
```

Estas variables representan tres dimensiones relevantes del perfil del cliente:

- **Edad:** característica demográfica.
- **Annual Income:** capacidad económica aproximada.
- **Spending Score:** comportamiento relativo de gasto.

---

# Estandarización de variables

Antes de ejecutar K-Means, las tres variables se estandarizan.

Esto es necesario porque se encuentran en escalas diferentes.

Por ejemplo:

- Edad puede encontrarse entre aproximadamente 18 y 70 años.
- Ingreso anual presenta otra escala numérica.
- Spending Score se encuentra entre 1 y 100.

Sin estandarización, una variable con valores numéricamente mayores podría tener una influencia excesiva sobre las distancias utilizadas por K-Means.

El proceso transforma las variables para que tengan escalas comparables antes del entrenamiento.

---

# Modelo de segmentación

El modelo se encuentra centralizado en:

```text
src/model.py
```

Este módulo contiene la lógica de segmentación utilizada tanto por:

```text
notebooks/analisis_exploratorio.ipynb
```

como por:

```text
dashboard/app.py
```

De esta forma, el notebook y el dashboard utilizan **exactamente la misma implementación del modelo**, evitando diferencias entre los resultados analíticos y los resultados visualizados.

---

# Selección del número de clusters

Se evaluaron distintas configuraciones de K-Means utilizando valores de:

```text
k = 2 a 10
```

Para comparar las alternativas se utilizaron:

- Inercia.
- Método del codo.
- Coeficiente de silueta.

La inercia permite observar cómo disminuye la distancia interna de los clusters al aumentar `k`.

El coeficiente de silueta permite evaluar simultáneamente:

- Cohesión dentro de cada cluster.
- Separación entre clusters.

---

## Modelo seleccionado

La configuración utilizada finalmente es:

```text
K-Means
k = 6
```

El modelo obtuvo un coeficiente de silueta aproximado de:

```text
0,427
```

Dentro de las configuraciones evaluadas, `k = 6` presentó el mejor coeficiente de silueta.

Por este motivo se seleccionó como configuración principal del proyecto.

---

# Interpretación del coeficiente de silueta

El coeficiente de silueta puede tomar valores entre:

```text
-1 y 1
```

De forma general:

- Valores cercanos a **1** indican clusters bien separados.
- Valores cercanos a **0** indican cierto solapamiento.
- Valores negativos pueden indicar asignaciones poco consistentes.

El resultado aproximado de:

```text
0,427
```

indica una estructura de segmentación moderada y utilizable para fines exploratorios, aunque no implica una separación perfecta entre todos los clientes.

---

# Descripción de clusters

Luego de construir el modelo se genera un perfil agregado para cada cluster.

Para cada segmento se analizan:

- Número de clientes.
- Edad promedio.
- Ingreso anual promedio.
- Spending Score promedio.

Esto permite traducir los resultados del algoritmo a perfiles comprensibles desde una perspectiva de negocio.

El número asignado a cada cluster:

```text
Cluster 0
Cluster 1
Cluster 2
...
```

es únicamente un identificador técnico y **no representa un orden de importancia ni prioridad comercial**.

---

# Revisión de género y posibles sesgos

Después de construir los clusters se analiza cómo se distribuyen hombres y mujeres dentro de cada segmento.

Este análisis se realiza posteriormente al entrenamiento.

La variable `Gender`:

```text
NO se utiliza para formar los clusters.
```

Su utilización se limita a revisar si los resultados presentan concentraciones relevantes entre grupos.

Esto permite detectar posibles patrones que deberían ser considerados antes de utilizar los segmentos para decisiones comerciales.

---

# Limitaciones del análisis

Los resultados deben interpretarse considerando las siguientes limitaciones:

### Tamaño de la muestra

El dataset contiene solamente:

```text
200 clientes
```

Por lo tanto, los resultados corresponden a un piloto y no necesariamente representan a toda la población de clientes de un centro comercial.

---

### Variables disponibles

El modelo utiliza únicamente:

- Edad.
- Ingreso anual.
- Spending Score.

No existen variables como:

- Frecuencia real de compra.
- Monto histórico de transacciones.
- Productos adquiridos.
- Visitas al centro comercial.
- Recencia de compra.
- Uso de promociones.

Esto limita la profundidad comercial de los segmentos.

---

### Spending Score

El dataset entrega directamente el `Spending Score`.

El proyecto no dispone del detalle transaccional utilizado originalmente para construir dicho indicador.

Por lo tanto, el modelo interpreta esta variable como una medida disponible del comportamiento de gasto.

---

### Categorías Unknown

Existen valores `Unknown` en Education y Marital Status.

Aunque estas variables no participan en K-Means, su presencia representa una limitación de calidad que debe permanecer documentada.

---

### K-Means

K-Means construye clusters utilizando distancias respecto de centroides.

Por esta razón, el resultado depende de:

- Las variables seleccionadas.
- La transformación aplicada.
- El número de clusters.
- La estructura geométrica de los datos.

Los segmentos obtenidos deben considerarse una herramienta de apoyo al análisis y no una clasificación absoluta de los clientes.

---

# Notebook de análisis exploratorio

El archivo:

```text
notebooks/analisis_exploratorio.ipynb
```

documenta el proceso completo de análisis.

Incluye:

1. Carga del dataset.
2. Exploración inicial.
3. Revisión de tipos de variables.
4. Análisis descriptivo.
5. Revisión de categorías `Unknown`.
6. Selección de variables para clustering.
7. Estandarización.
8. Evaluación de diferentes valores de `k`.
9. Método del codo.
10. Coeficiente de silueta.
11. Entrenamiento del modelo K-Means.
12. Descripción de clusters.
13. Distribución de clusters por género.
14. Limitaciones del análisis.

El notebook utiliza la misma lógica implementada en:

```text
src/model.py
```

garantizando consistencia con el dashboard.

---

# El dashboard

El dashboard permite explorar tanto las características generales de los clientes como los resultados obtenidos mediante K-Means.

Está construido con:

```text
Streamlit
Plotly
pandas
scikit-learn
```

---

## Indicadores principales

El encabezado presenta indicadores generales que se recalculan al aplicar filtros.

Entre ellos:

| KPI | Descripción |
|---|---|
| Clientes seleccionados | Número de clientes disponibles después de aplicar filtros |
| Edad promedio | Edad media de la selección |
| Ingreso promedio | Ingreso anual promedio |
| Spending Score promedio | Índice medio de comportamiento de gasto |
| Participación femenina | Porcentaje de mujeres |
| Educación predominante | Nivel educacional más frecuente |
| Estado civil predominante | Estado civil más frecuente |
| Registros con Unknown | Presencia de información desconocida en Education o Marital Status |

---

# Vistas del dashboard

## 1. Perfil de clientes

Permite responder:

> ¿Cómo está compuesta la muestra analizada?

Incluye visualizaciones relacionadas con:

- Género.
- Edad.
- Educación.
- Estado civil.
- Calidad de información.

Su objetivo es comprender la composición general del dataset antes de analizar los segmentos.

---

## 2. Ingreso y gasto

Permite estudiar la relación existente entre:

```text
Annual Income
```

y:

```text
Spending Score
```

Incluye visualizaciones de dispersión y comparaciones de comportamiento entre clientes.

Esta vista permite identificar visualmente patrones que posteriormente son utilizados por el modelo de segmentación.

---

## 3. Segmentación K-Means

Esta vista presenta los resultados reales del modelo.

Los clientes aparecen clasificados según el cluster asignado por K-Means.

La segmentación utiliza:

```text
Age
Annual Income
Spending Score
```

previamente estandarizados.

El modelo utilizado corresponde a:

```text
k = 6
```

La vista permite observar:

- Distribución espacial de los clusters.
- Tamaño de cada segmento.
- Edad promedio.
- Ingreso promedio.
- Spending Score promedio.
- Composición de los segmentos.
- Distribución por género.

---

# Filtros

El dashboard permite aplicar filtros sobre variables disponibles en el dataset.

Entre ellos:

- Género.
- Educación.
- Estado civil.
- Edad.
- Ingreso anual.
- Spending Score.

Los filtros permiten explorar subconjuntos específicos de clientes sin modificar el dataset original.

---

# Trazabilidad del modelo

El flujo principal del proyecto puede representarse como:

```text
Mall Customers
       ↓
Carga de datos
       ↓
Exploración
       ↓
Preparación
       ↓
Selección de variables
       ↓
Estandarización
       ↓
Evaluación de k
       ↓
K-Means
       ↓
Evaluación con silueta
       ↓
Perfilamiento de clusters
       ↓
Revisión por género
       ↓
Dashboard
```

Esto permite mantener trazabilidad entre el dataset original, el análisis técnico y las visualizaciones finales.

---

# Consistencia entre notebook y dashboard

Una decisión importante del proyecto fue centralizar el modelo en:

```text
src/model.py
```

Tanto el notebook como el dashboard llaman a esta misma implementación.

Esto evita mantener dos versiones independientes del modelo y asegura que:

```text
Notebook = Dashboard
```

en términos de:

- Variables utilizadas.
- Estandarización.
- Número de clusters.
- Asignación de clientes.
- Perfiles generados.

---

# Tecnologías utilizadas

- Python 3.11+
- Streamlit
- pandas
- Plotly
- scikit-learn
- Jupyter Notebook

Las dependencias necesarias para ejecutar el dashboard se encuentran en:

```text
requirements.txt
```

---

# Solución de problemas

| Síntoma | Solución |
|---|---|
| Se requiere Python 3.11 o superior | Instalar una versión actual desde python.org |
| Puerto 8501 ocupado | Cerrar otra instancia de Streamlit o utilizar otro puerto |
| Dashboard no se abre | Abrir manualmente `http://localhost:8501` |
| Instalación de dependencias falla | Revisar conexión a Internet y ejecutar nuevamente `run.bat` |
| `ModuleNotFoundError: sklearn` | Eliminar `.venv` y ejecutar nuevamente `run.bat` para instalar las dependencias actualizadas |
| `WinError 206` | Utilizar una ruta corta para almacenar el proyecto |
| Entorno virtual incompleto | Eliminar `.venv` y volver a ejecutar el lanzador |

---

## WinError 206 en Windows

Windows puede presentar errores si la ruta física del proyecto es demasiado extensa.

Se recomienda evitar rutas como:

```text
C:\Users\usuario\OneDrive\Escritorio\carpetas\muy\largas\proyecto\...
```

y utilizar una ubicación corta, por ejemplo:

```text
C:\SV
```

Luego ejecutar:

```powershell
.\run.bat
```

---

# Alcance actual

El proyecto constituye un **piloto analítico de segmentación de clientes**.

Actualmente permite:

- Explorar los 200 registros.
- Analizar características demográficas.
- Evaluar ingreso y comportamiento de gasto.
- Preparar y estandarizar variables.
- Aplicar K-Means.
- Comparar diferentes valores de `k`.
- Evaluar los clusters mediante coeficiente de silueta.
- Caracterizar los segmentos.
- Revisar su distribución por género.
- Visualizar los resultados mediante un dashboard interactivo.

El proyecto **no automatiza campañas comerciales ni toma decisiones autónomas sobre clientes**.

Los resultados deben ser interpretados como información de apoyo para análisis y decisiones posteriores del área de marketing.

---

**Gestión de Proyectos de Datos — SCY1102**  
**Proyecto de Segmentación de Clientes**  
**Mall Customers · 200 registros · K-Means · k = 6**