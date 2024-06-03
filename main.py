import os
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import uvicorn

from router.auth import auth
from router.admin import admin
from router.dashboard import dashboard
from router.user import user
from router.payment import payment

load_dotenv(verbose=True)

app = FastAPI()

origins = [
    "http://localhost",
    "http://localhost:3000",
    # "https://dev.rndsillog.com",
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

app.include_router(auth.router)
app.include_router(admin.router)
app.include_router(dashboard.router)
app.include_router(user.router)
app.include_router(payment.router)


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
