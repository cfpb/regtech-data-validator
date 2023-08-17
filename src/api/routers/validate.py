from fastapi import APIRouter, Request, UploadFile
from fastapi.responses import JSONResponse

from validator.create_schemas import validate_data_list, validate_raw_csv

# validate router
router = APIRouter()


@router.post("/validate/")
async def validate(request: Request, payload: dict):
    """
    handle validate endpoint

    Args:
        request (Request): request object
        payload (dict): data received from user

    Returns:
        JSON response
    """
    phase1_schema = request.app.schemas[0]
    phase2_schema = request.app.schemas[1]
    response = validate_data_list(phase1_schema, phase2_schema, payload)
    return JSONResponse(status_code=200, content=response)


@router.post("/upload/")
async def upload(request: Request, file: UploadFile):
    """
    handle upload request

    Args:
        request (Request): request object
        file (UploadFile): uploaded file

    Returns:
        JSON response
    """
    contents = file.file.read()
    phase1_schema = request.app.schemas[0]
    phase2_schema = request.app.schemas[1]
    response = validate_raw_csv(phase1_schema, phase2_schema, contents)
    return JSONResponse(status_code=200, content=response)
