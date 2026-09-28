from fastapi import FastAPI

app = FastAPI(title="Path Mirror API")


@app.get("/health")
def health():
    return {"status": "ok", "app": "Path Mirror"}