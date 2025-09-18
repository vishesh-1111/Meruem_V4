from contextlib import asynccontextmanager

from beanie import init_beanie
from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi import Response
from .database import  db
from .user.schema import User
from .workspace.schema import Workspace
from .connections.schema import Connection
from .chats.schema import Chat
from .auth.api import router as auth_router
from .workspace.api import router as workspace_router
from .connections.api import router as connections_router
from .chats.api import router as chats_router




@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_beanie(
        database=db,
        document_models=[
            User,
            Workspace,
            Connection,
            Chat
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
    "http://localhost:3001",  # Your frontend development server
    "http://127.0.0.1:3001",  # Alternative localhost
    "https://localhost:3001", # If you use HTTPS locally
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(auth_router,tags=["auth"])
app.include_router(workspace_router,tags=["workspace"])
app.include_router(connections_router,tags=["connections"])
app.include_router(chats_router,tags=["chats"])


# from src.workspace.schema import Workspace
    
# async def F():
#     x=await Workspace.find()
#     print(x)


# F()   


# import asyncio
# from src.workspace.schema import Workspace
    
# async def F():
#     await init_beanie(
#         database=db,
#         document_models=[
#             User,
#             Workspace,
#             Connection,
#             Chat
#         ],
#     )

#     workspaces_cursor = Workspace.find(
#         Workspace.name == "My Workspace",
#         fetch_links=True
#     )
#     x = []
#     async for workspace in workspaces_cursor:
#         x.append(workspace)

#     print(x)

# if __name__ == "__main__":
#     asyncio.run(F())
