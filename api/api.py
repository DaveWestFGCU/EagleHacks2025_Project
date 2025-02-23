import uuid, os

from fastapi import FastAPI, BackgroundTasks, status, Form
from contextlib import asynccontextmanager
from starlette.responses import JSONResponse
from starlette.staticfiles import StaticFiles

from .ad_generator import AdGenerator
from .logging_setup import listener


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Defines the logic before FastAPI starts up and after it shuts down.
    """
    listener.start()
    yield
    listener.stop()

app = FastAPI()


job_store = {}

@app.get("/")
async def read_root():
    """
    Endpoint for checking API is working without starting a job.
    """
    return {"message": "Hello, World!"}

@app.post("/new_job")
async def new_job(background_tasks: BackgroundTasks,
                  product: str = Form(...),
                  audience: str = Form(...),
                  goal: str = Form(...)) -> JSONResponse:
    """
    Endpoint for creating a new job.
    :param background_tasks: Function(s) to run after responding.
    :param product:
    :param audience:
    :param goal:
    :return:
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


@app.get("/job/{job_id}")
async def poll_job(job_id: str):
    """
    Polling endpoint that returns the status of an ongoing job.
    :param job_id:
    :return:
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

    content = {'status': job.status,}
    for i, ad_path in enumerate(job.image_locations):
        content[f'{i}'] = ad_path

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=content
    )


try:
    app.mount("/static", StaticFiles(directory="api/static"), name="static")

except RuntimeError:
    os.makedirs('./api/static', exist_ok=True)
    app.mount("/static", StaticFiles(directory="api/static"), name="static")