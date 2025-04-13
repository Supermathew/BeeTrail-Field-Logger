from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.routers import auth, hives, crops,sync
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from pymongo.errors import ConnectionFailure
import motor.motor_asyncio
from app.config import MONGO_DETAILS, DATABASE_NAME
from fastapi import Depends
from app.dependencies import get_current_user


@asynccontextmanager
async def lifespan(app: FastAPI):

    client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_DETAILS)
    try:
        await client.admin.command("ping")
        print("Database connection successful!")
        app.state.mongo_client = client
        app.state.db = client[DATABASE_NAME]

        await app.state.db["crops"].create_index([("location", "2dsphere")])
        print("2dsphere index ensured on 'crops.location'")

    except ConnectionFailure as e:
        print(f"Database connection failed: {e}")
        raise RuntimeError("Failed to connect to the database.") from e

    yield

    client.close()

    
app = FastAPI(title="BeeTrail Field Logger API", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins, for development.  In production, specify your frontend's origin.
    allow_credentials=True,
    allow_methods=["*"],  # Allows all HTTP methods
    allow_headers=["*"],  # Allows all headers
)

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")


app.include_router(auth.router)

app.include_router(hives.router, dependencies=[Depends(get_current_user)])
app.include_router(crops.router, dependencies=[Depends(get_current_user)])
app.include_router(sync.router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
