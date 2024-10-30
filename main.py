import os
import time
from dotenv import load_dotenv
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
import logging
from typing import Awaitable, Callable

import uvicorn

from router.auth import auth
from router.admin import admin
from router.dashboard import dashboard
from router.user import user
from router.payment import payment
from router.validate import validate

load_dotenv(verbose=True)

app = FastAPI(openapi_url='/api/openapi.json')


origins = [
    "http://localhost",
    "http://localhost:3000",
    "https://dev.rndsillog.com",
    "https://rndsillog.com",
    os.getenv("FRONTEND_URL"),
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# log 설정
logger = logging.getLogger(__name__)
MWCNFunc = Callable[[Request], Awaitable[Response]]


@app.middleware("http")
async def logging_middleware(request: Request, call_next: MWCNFunc) -> Response:
    start = time.time()
    response = await call_next(request)
    duration = (time.time() - start) / 1000
    source = f"{request.client.host}:{request.client.port}"
    resource = f"{request.method} {request.url.path}"
    result = f"{response.status_code} [{duration:.1f}ms]"
    message = f"{source} => {resource} => {result}"
    logger.info(message)
    return response

app.include_router(auth.router)
app.include_router(admin.router)
app.include_router(dashboard.router)
app.include_router(user.router)
app.include_router(payment.router)
app.include_router(validate.router)


if __name__ == "__main__":
    if (os.getenv("RUNNING_MODE") == "dev"):
        uvicorn.run("main:app", host="0.0.0.0", port=8000,
                    reload=True)
    elif (os.getenv("RUNNING_MODE") == "prod"):
        uvicorn.run("main:app", host="0.0.0.0", port=8000,
                    reload=True, log_config='logging.yaml')
