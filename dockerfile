# Imagen base con python y pip
FROM python:3.10-slim

# Establecer directorio de trabajo
WORKDIR /app

# Copiar las dependencias necesarias
COPY requirements.txt .

# Instalar las dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el resto código de la app
COPY . .

# Abrir el puerto que utiliza uvicorn
# Dejo el 8080 porque es el que permite Google Cloud Run
EXPOSE 8080

# Comando para iniciar la api
CMD ["uviconr", "main:app", "--host", "0.0.0.0", "--port", "8080"] 