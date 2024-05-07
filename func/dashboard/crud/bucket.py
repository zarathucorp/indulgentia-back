import json
from fastapi.responses import JSONResponse
from gotrue.errors import AuthApiError

from database.supabase import supabase
from database import schemas


