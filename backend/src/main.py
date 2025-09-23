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
from .messages.schema import Message
from .auth.api import router as auth_router
from .workspace.api import router as workspace_router
from .connections.api import router as connections_router
from .chats.api import router as chats_router
from .messages.api import router as messages_router
from .stream.api import router as stream_router
from .config import get_frontend_config



@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_beanie(
        database=db,
        document_models=[
            User,
            Workspace,
            Connection,
            Chat,
            Message
        ],
    )
    yield
    print("Shutting down...")


app = FastAPI(lifespan=lifespan)

frontend_config= get_frontend_config()
# Configure CORS
origins = [
     frontend_config["frontend_url"],
     "https://localhost:3000"
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
app.include_router(messages_router,tags=["messages"])
app.include_router(stream_router,tags=["stream"])


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
