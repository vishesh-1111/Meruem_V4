import os
from contextlib import asynccontextmanager

from beanie import init_beanie
from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from fastapi import Response
from .database import  db
from .user.schema import User
from .auth.api import router as auth_router
load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_beanie(
        database=db,
        document_models=[
            User,
        ],
    )
    yield
    print("Shutting down...")


app = FastAPI(lifespan=lifespan)

# Configure CORS
origins = [
    "http://localhost:3000",  # Your frontend development server
    "http://127.0.0.1:3000",  # Alternative localhost
    "https://localhost:3000", # If you use HTTPS locally
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(auth_router,tags=["auth"])

