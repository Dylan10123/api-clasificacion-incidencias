# API de Clasificación de Incidencias Técnicas

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat&logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?style=flat&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![PyTorch](https://img.shields.io/badge/PyTorch-2.7-EE4C2C?style=flat&logo=pytorch&logoColor=white)](https://pytorch.org/)
[![HuggingFace](https://img.shields.io/badge/HuggingFace-Model-FFD21E?style=flat&logo=huggingface&logoColor=black)](https://huggingface.co/Dylan1012/modelo_roberta_postventa)
[![Accuracy](https://img.shields.io/badge/Accuracy-96.38%25-2ea44f?style=flat)](#rendimiento-del-modelo)
[![GitHub](https://img.shields.io/badge/GitHub-repo-181717?style=flat&logo=github)](https://github.com/Dylan10123/api-clasificacion-incidencias)

API REST para la clasificación automática de incidencias técnicas de clientes mediante un modelo de PLN basado en RoBERTa en español. El sistema procesa ficheros Excel con incidencias diarias y devuelve un informe clasificado y formateado, listo para su revisión.

---

## Arquitectura del sistema

```
Excel de incidencias
        │
        ▼
┌───────────────────┐
│  POST /clasificar │   FastAPI
└───────────────────┘
        │
        ▼
┌───────────────────────────────────────────────┐
│  Preprocesado                                 │
│  Descripción + [SEP] + Acción Correctora      │
└───────────────────────────────────────────────┘
        │
        ▼
┌───────────────────────────────────────────────┐
│  Modelo RoBERTa fine-tuned                    │
│  Dylan1012/modelo_roberta_postventa           │
│  (HuggingFace Hub)                            │
└───────────────────────────────────────────────┘
        │
        ▼
Excel clasificado y formateado
(agrupado por categoría + código de colores)
```

---

## Funcionamiento

1. Se sube un fichero `.xlsx` con las incidencias del día.
2. La API filtra automáticamente las incidencias del **día anterior**.
3. Cada incidencia se procesa concatenando el campo `Descripción` y `Acción Correctora`.
4. El modelo predice la categoría y la confianza de cada predicción.
5. Se devuelve un Excel formateado con las incidencias agrupadas por categoría y las celdas de precisión coloreadas:

| Color       | Significado     |
| ----------- | --------------- |
| 🟢 Verde    | Precisión ≥ 90% |
| 🟡 Amarillo | Precisión ≥ 80% |
| 🔴 Rojo     | Precisión < 80% |

---

## Dataset de entrenamiento

El modelo fue entrenado con **2.634 incidencias reales** anonimizadas, distribuidas en **19 categorías**:

| Categoría                         | Incidencias |
| --------------------------------- | :---------: |
| ERRORES OCPP/PR                   |     261     |
| ERROR_APP                         |     247     |
| MANGUERA ATASCADA EN PR           |     210     |
| TOMA COMO OCUPADO SIN HABER NADIE |     207     |
| RESERVAS                          |     205     |
| CARGA ACTIVA                      |     203     |
| FACTURAS                          |     201     |
| TRANSFER CT                       |     199     |
| SESION ACTIVA INTEROPERABILIDAD   |     191     |
| CORREO DE ACTIVACION              |     191     |
| CAMBIO DE CONTRASEÑA              |     166     |
| ERROR_DEAUTHORIZED                |     124     |
| MAL USO DEL CLIENTE               |     118     |
| RFID_RP                           |     31      |
| ESTADO DE REGISTRO DE CUENTA      |     25      |
| ESTADO DE PR                      |     20      |
| PREAUTORIZACIONES                 |     16      |
| USO DE APP                        |     13      |
| USO DE PR                         |      6      |

> Por motivos de privacidad no se publican los datos de entrenamiento ni información relativa a la empresa o los clientes.

---

## Rendimiento del modelo

El modelo fue evaluado sobre un conjunto de test con una división **80/20** (stratified):

| Métrica                 |              Valor               |
| ----------------------- | :------------------------------: |
| Accuracy                |            **96.38%**            |
| Épocas de entrenamiento |                4                 |
| Modelo base             | `PlanTL-GOB-ES/roberta-base-bne` |

El entrenamiento utilizó pesos de clase balanceados (`compute_class_weight`) para compensar el desbalanceo entre categorías.

---

## Tecnologías utilizadas

| Capa                | Tecnología                           |
| ------------------- | ------------------------------------ |
| API                 | FastAPI + Uvicorn                    |
| Modelo NLP          | Transformers (HuggingFace) — RoBERTa |
| Deep Learning       | PyTorch                              |
| Model Registry      | HuggingFace Hub                      |
| Procesado de datos  | Pandas, NumPy                        |
| Generación de Excel | openpyxl                             |
| Entrenamiento       | scikit-learn, datasets, evaluate     |

---

## Endpoint

### `POST /clasificar`

Recibe un fichero Excel y devuelve otro Excel con las incidencias del día anterior clasificadas.

**Request:**

```
Content-Type: multipart/form-data
Body: file = <archivo.xlsx>
```

**Columnas requeridas en el Excel de entrada:**

| Columna             | Descripción                       |
| ------------------- | --------------------------------- |
| `Descripción`       | Texto de la incidencia reportada  |
| `Acción Correctora` | Solución aplicada                 |
| `Fecha Creación`    | Fecha de la incidencia            |
| `Creado por`        | Agente que registró la incidencia |

**Response:** Fichero `.xlsx` con las incidencias clasificadas, agrupadas por categoría y con formato visual.

---

## Instalación y ejecución local

```bash
# Clonar el repositorio
git clone https://github.com/Dylan10123/api-clasificacion-incidencias.git
cd api-clasificacion-incidencias

# Crear entorno virtual e instalar dependencias
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Configurar token de HuggingFace (necesario para descargar el modelo)
export HUGGINGFACE_HUB_TOKEN=<tu_token>  # Windows: set HUGGINGFACE_HUB_TOKEN=<tu_token>

# Lanzar la API
uvicorn main:app --reload
```

La API estará disponible en `http://localhost:8000`. La documentación interactiva en `http://localhost:8000/docs`.

---

## Entrenamiento del modelo

El script de entrenamiento se encuentra en `modelo/modelo.py`. Requiere un fichero `modelo/df_final.csv` con las columnas `Descripción`, `Acción Correctora` y `categoria`.

```bash
cd modelo
python modelo.py
```

El modelo entrenado se guarda en `modelo/modelo_roberta_postventa/` y puede subirse a HuggingFace Hub con la CLI de `huggingface_hub`.
