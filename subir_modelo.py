from huggingface_hub import create_repo, upload_folder

# Crear el repo si no existe
create_repo("modelo_roberta_postventa", repo_type="model", private=True)

# Subir el modelo
upload_folder(
    folder_path="modelo/modelo_roberta_postventa",
    repo_id="Dylan1012/modelo_roberta_postventa",
    repo_type="model",
    commit_message="Primer commit del modelo de clasificación de incidencias"
)
