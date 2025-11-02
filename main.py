from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from routes.posts import router as posts_router
from database import Base, engine
from websocket_manager import websocket_endpoint

app = FastAPI()

Base.metadata.create_all(bind=engine)

app.include_router(posts_router)
app.mount("/static", StaticFiles(directory="static"), name="static")

# WebSocket endpoint for real-time updates
app.websocket("/ws")(websocket_endpoint)
