from fastapi import FastAPI

from app.api.routes import notification_router

from app.config.firebase import db


app = FastAPI()


app.include_router(
    notification_router.router,
)


@app.get("/")
async def root():

    collections = db.collections()

    names = [c.id for c in collections]

    return {

        "status": "ok",

        "collections": names,

    }