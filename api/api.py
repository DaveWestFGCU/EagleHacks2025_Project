import uuid

from fastapi import FastAPI, status, Form
from starlette.responses import JSONResponse
from .ad_generator import AdGenerator

app = FastAPI()


job_store = {}

@app.get("/")
async def read_root():
    return {"Hello": "World"}

@app.post("/new_job")
async def new_job(keywords: str = Form(...)) -> JSONResponse:
    """
    Starts a new job.
    :param keywords: Keyword(s) to build the ad around.
    :return:
    """

    job_id = str(uuid.uuid4())
    while job_id in job_store:
        job_id = str(uuid.uuid4())

    job_store[job_id] = AdGenerator(job_id, keywords)

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
    if job_id in job_store:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={'message': f"Job {job_id} not found."}
        )

    job = job_store[job_id]

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={'status': job.status}
    )


# TODO: Figure out how to return an image.
@app.get("job/{job_id}/advertisement{ad_number}")
async def get_advertisement(job_id: str, ad_number: int):
    """
    Returns a generated image
    :param job_id:
    :param ad_number:
    :return:
    """
    if job_id not in job_store:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={'message': "Job not found."}
        )

    job = job_store[job_id]

    if job.status != 'Complete':
        return JSONResponse(
            status_code=status.HTTP_202_ACCEPTED,
            content={'message': "Let me cook."}
        )

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={'image': "Use your imagination."}
    )