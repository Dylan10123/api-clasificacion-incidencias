from transformers import pipeline

# Cargar el modelo entrenado
modelo_entrenado = pipeline(
    "text-classification",
    model="Dylan1012/modelo_roberta_postventa",
    tokenizer="Dylan1012/modelo_roberta_postventa",
    top_k=None
)

# Entrada del usuario
sep_token = " [SEP] "
descripcion = "PR en fallo de comunicación desde reposo sin mediar acciones previas. Tan solo mensajes de heartbeat en mensajería No disponemos de acceso a webmanager tampoco"
accion = ""
entrada = descripcion + sep_token + accion 

# Obtener predicciones
resultado = modelo_entrenado(entrada)[0]  # [0] porque es una sola entrada

# Mostrar formato: [CATEGORIA] -> [PROBABILIDAD]
print("Probabilidades por categoría:\n")
for pred in sorted(resultado, key=lambda x: x['score'], reverse=True):
    print(f"[{pred['label']}] -> {pred['score'].__round__(4) * 100}%")

# También puedes mostrar la predicción final
print(f"\nCategoría predicha: {max(resultado, key=lambda x: x['score'])['label']}")