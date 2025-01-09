import os
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from uvicorn.config import LOGGING_CONFIG

from router.auth import auth
from router.admin import admin
from router.dashboard import dashboard
from router.user import user
from router.payment import payment
from router.validate import validate
from router.demo import demo


load_dotenv(verbose=True)

ROOT_PATH = str(os.getenv("ROOT_PATH"))

app = FastAPI(root_path=ROOT_PATH)

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
    expose_headers=["content-disposition", "x-note-id"],
)

app.include_router(auth.router)
app.include_router(admin.router)
app.include_router(dashboard.router)
app.include_router(user.router)
app.include_router(payment.router)
app.include_router(validate.router)
app.include_router(demo.router)

# Logging configuration
LOGGING_CONFIG["formatters"]["default"]["fmt"] = "%(asctime)s [%(name)s] %(levelprefix)s %(message)s"
LOGGING_CONFIG["formatters"]["access"][
    "fmt"] = '%(asctime)s [%(name)s] %(levelprefix)s %(client_addr)s - "%(request_line)s" %(status_code)s'

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000,
                reload=True)
