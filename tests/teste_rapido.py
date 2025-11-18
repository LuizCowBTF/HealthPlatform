# Crie um arquivo teste_rapido.py na raiz:
from fastapi import FastAPI
import uvicorn

app = FastAPI()

@app.get("/")
def root():
    return {"message": "✅ Servidor HealthPlatform Online!"}

@app.get("/test-webhook")
def test_webhook():
    return {"status": "test_ok", "message": "Webhook funcionando!"}

if __name__ == "__main__":
    print("🚀 Iniciando servidor teste na porta 8000...")
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)