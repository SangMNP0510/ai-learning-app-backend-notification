from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.api.routes import notification_router
from app.config.firebase import db
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:8000",
        "http://localhost:8000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(notification_router.router)

# Serve thư mục web
app.mount("/admin", StaticFiles(directory="admin", html=True), name="admin")

@app.get("/")
async def root():
    collections = db.collections()
    names = [c.id for c in collections]

    return {
        "status": "ok",
        "collections": names,
    }