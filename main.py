import uvicorn
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from src.routers.api_router import router as api_router

app = FastAPI(
    title="Cinema",
    description="API для работы с базой данных кинотеатра",
)

app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
