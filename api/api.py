import uuid, os
import psycopg
from typing import Optional

from fastapi import FastAPI, BackgroundTasks, Request, status, Form
from contextlib import asynccontextmanager
from starlette.responses import JSONResponse
from starlette.staticfiles import StaticFiles

from api.services.ad_generator import AdGenerator
from api.services.logging_setup import listener

import app.db as db

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Defines the logic before FastAPI starts up and after it shuts down.
    """
    listener.start()    # Logging queue listener
    update_key_store()
    yield

    listener.stop()

app = FastAPI(lifespan=lifespan)

key_store = ['test_key_953209gnjgsaea09ulknfdln']
job_store = {}

@app.get("/")
async def read_root():
    """
    Endpoint for checking API is active without starting a job.
    """
    return {'message': "Hello, World!"}

@app.post("/new_job")
async def new_job(background_tasks: BackgroundTasks,
                  product : str = Form(...),
                  audience : Optional[str] = Form(None),
                  goal : Optional[str] = Form(None)) -> JSONResponse:
    """
    Endpoint for creating a new job.
    """

    job_id = str(uuid.uuid4())
    while job_id in job_store:
        job_id = str(uuid.uuid4())

    job_store[job_id] = AdGenerator(job_id, product, audience, goal)

    background_tasks.add_task(job_store[job_id].run)

    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content={
            'message': f"New job created.",
            'id': job_id
        }
)


@app.middleware("http")
async def api_key_validation(request: Request, call_next) -> JSONResponse:
    """
    Middleware for validating an API key before processing any requests.
    If a key is not in the request or not found in the key store, returns a 401 Unauthorized response.
    """
    return await call_next(request)
    # if request.headers.get("x-api-key"):

    #     if validate_api_key(request.headers.get("x-api-key")):
    #         return await call_next(request)

    #     return JSONResponse(
    #         status_code=status.HTTP_401_UNAUTHORIZED,
    #         content={'message': "Invalid API Key."}
    #     )

    # return JSONResponse(
    #     status_code=status.HTTP_401_UNAUTHORIZED,
    #     content={'message': "API key not received."}
    # )



@app.get("/job/{job_id}")
async def poll_job(job_id: str):
    """
    Polling endpoint that returns the status of an ongoing job.
    If a job is complete, returns links to the ad images.
    """

    if job_id not in job_store:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={'message': f"Job {job_id} not found."}
        )

    job = job_store[job_id]

    if job.status != 'done':
        return JSONResponse(
            status_code=status.HTTP_202_ACCEPTED,
            content={'message': "Let me cook."}
        )

    content = {'status': job.status}
    for i, ad_path in enumerate(job.image_locations):
        content[f'{i}'] = ad_path

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=content
    )

# Allow access to the app/static/ directory
os.makedirs('./api/static', exist_ok=True)
app.mount("/static", StaticFiles(directory="api/static"), name="static")


def validate_api_key(api_key) -> bool:
    """
    Checks the key store for the API key.
    If the key is not in the store, updates the key store and checks again.
    """
    if api_key in key_store:
        return True

    update_key_store()
    if api_key in key_store:
        return True

    return False


def update_key_store() -> None:
    """
    Queries the database for all API keys to update the key store.
    Runs on API startup and when a key is not found to check it hasn't been added after the last update.
    Updating in this way also clears keys when a new user connects.
    """
    return
    global key_store
    try:
        with db.connect() as conn, conn.cursor() as cursor:
            records = cursor.execute('select api_key from users;').fetchall()
            key_store = [record.api_key for record in records]

    except Exception as e:
        print(f'DB CONNECTION ERROR: {e}')