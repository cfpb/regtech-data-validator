from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from routers import validate_router

from util.global_data import read_geoids, read_naics_codes
from validator.create_schemas import get_schemas

# HOWTO
# run: uvicorn main:app --host 0.0.0.0 --port 8080 --reload

app = FastAPI()
# get our schems
app.schemas = get_schemas(read_naics_codes(), read_geoids())


# custom exception handlers
@app.exception_handler(Exception)
async def api_exception_handler(request: Request, err: Exception):
    """
    handle exception/error that is triggered by incorrect data format

    Args:
        request (Request): HTTP request
        err (Exception): the actual exception object

    Returns:
        returns JSON Response with status code and message
    """
    error_code = (400,)
    error_msg = str(err)
    if type(err) is ValueError:
        error_code = 422
    elif type(err) is AttributeError:
        error_code = 500
        error_msg = f"Internal Server Error. Type: {str(type(err))}"

    return JSONResponse(
        status_code=error_code,
        content=[{"response": error_msg}],
    )


# add anonymous validation endpoints
app.include_router(validate_router, prefix="/v1")
