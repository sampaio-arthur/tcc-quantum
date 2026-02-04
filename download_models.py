from sentence_transformers import SentenceTransformer

# Definimos o modelo que vamos usar (o MiniLM é ótimo para TCC por ser leve e rápido)
model_name = "all-MiniLM-L6-v2"

print(f"Baixando modelo {model_name} para dentro da imagem...")
SentenceTransformer(model_name)
print("Download concluído!")
