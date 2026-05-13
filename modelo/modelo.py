import pandas as pd
from sklearn.model_selection import train_test_split
from datasets import Dataset, DatasetDict
import evaluate
from transformers import AutoTokenizer, AutoModelForSequenceClassification, Trainer, TrainingArguments
import numpy as np
import torch
from sklearn.utils.class_weight import compute_class_weight

# Cargar los datos
df_final = pd.read_csv('./df_final.csv')

# Crear columna combinada: Descripción + Acción Correctora
# Ensure text columns are strings and handle NaN values
sep_token = " [SEP] "
df_final['input_text'] = (
    df_final['Descripción'].fillna('') + sep_token + 
    df_final['Acción Correctora'].fillna('')
    )

# Asociar las categorías a índices numéricos
categorias = df_final['categoria'].unique()
label2id = {categoria: idx for idx, categoria in enumerate(categorias)}
id2label = {idx: categoria for categoria, idx in label2id.items()}
df_final['label'] = df_final['categoria'].map(label2id)

# Dividir los datos
train_df, test_df = train_test_split(df_final, test_size=0.2, random_state=42, stratify=df_final['categoria'])

# Crear datasets de Hugging Face
train_dataset = Dataset.from_pandas(train_df[['input_text', 'label']])
test_dataset = Dataset.from_pandas(test_df[['input_text', 'label']])

dataset_dict = DatasetDict({
    'train': train_dataset,
    'test': test_dataset
})

# Calcular los pesos de clase
class_weights = compute_class_weight(
    class_weight='balanced',
    classes=np.unique(train_df['label']),
    y=train_df['label']
)

# Le doy mas paso a la clase de ERRORES OCPP/PR
# class_weights[label2id["ERRORES OCPP/PR"]] *= 1.5

# Convierto a tensor y lo muevo a la GPU si está disponible
weights_tensor = torch.tensor(class_weights, dtype=torch.float)
if torch.cuda.is_available():
    weights_tensor = weights_tensor.to('cuda')

# Cargar modelo y tokenizer
modelo_checkpoint = "PlanTL-GOB-ES/roberta-base-bne"
tokenizer = AutoTokenizer.from_pretrained(modelo_checkpoint)

# Función de tokenización
def tokenize(batch):
    return tokenizer(batch['input_text'], padding='max_length', truncation=True, max_length=512)

tokenized_datasets = dataset_dict.map(tokenize, batched=True)

# Definir el modelo
num_labels = len(categorias)
model = AutoModelForSequenceClassification.from_pretrained(
    modelo_checkpoint,
    num_labels=num_labels,
    id2label=id2label,
    label2id=label2id
)

class WeightedTrainer(Trainer):
    def compute_loss(self, model, inputs, return_outputs=False, **kwargs):
        labels = inputs.pop("labels")
        outputs = model(**inputs)
        logits = outputs.logits
        loss_fn = torch.nn.CrossEntropyLoss(weight=weights_tensor)
        loss = loss_fn(logits, labels)
        return (loss, outputs) if return_outputs else loss

# Enviar modelo a CUDA si está disponible
model.to(torch.device('cuda' if torch.cuda.is_available() else 'cpu'))

# Métrica
accuracy_metric = evaluate.load("accuracy")

def compute_metrics(eval_pred):
    logits, labels = eval_pred
    predictions = np.argmax(logits, axis=-1)
    return accuracy_metric.compute(predictions=predictions, references=labels)

# Argumentos de entrenamiento
training_args = TrainingArguments(
    output_dir="modelo_roberta_postventa",
    eval_strategy="epoch",
    save_strategy="epoch",
    learning_rate=2e-5,
    per_device_train_batch_size=16,
    per_device_eval_batch_size=16,
    num_train_epochs=4,
    weight_decay=0.01,
    logging_steps=50,
    load_best_model_at_end=True,
)

# Crear trainer y entrenar
trainer = WeightedTrainer(
    model=model,
    args=training_args,
    train_dataset=tokenized_datasets['train'],
    eval_dataset=tokenized_datasets['test'],
    compute_metrics=compute_metrics,
)

trainer.train()

# Evaluar
print(trainer.evaluate())

# Guardar
try:
    ruta_modelo = "./modelo_roberta_postventa"
    trainer.save_model(ruta_modelo)
    tokenizer.save_pretrained(ruta_modelo)
    print("✅ Modelo y tokenizer guardados correctamente.")
except Exception as e:
    print("❌ Error al guardar:", e)
