from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import question_router

app = FastAPI(
    title="Question Answering API",
    description="API simples para processar perguntas usando LangChain",
    version="1.0.0"
)

# Configuração do CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir routers
app.include_router(question_router.router)

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
