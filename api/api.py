import uuid, os

from fastapi import FastAPI, BackgroundTasks, status, Form
from starlette.responses import JSONResponse
from starlette.staticfiles import StaticFiles

from .ad_generator import AdGenerator

app = FastAPI()


job_store = {}

@app.get("/")
async def read_root():
    return {"Hello": "World"}

@app.post("/new_job")
async def new_job(background_tasks: BackgroundTasks,
                  product: str = Form(...),
                  audience: str = Form(...),
                  goal: str = Form(...)) -> JSONResponse:

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

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            'status': job.status,
            'concept 0': job.concept0['url']
        }
    )


os.makedirs('static', exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")
