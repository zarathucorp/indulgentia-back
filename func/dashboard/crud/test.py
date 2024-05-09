import json
from fastapi.responses import JSONResponse
from pydantic import UUID4
import uuid

from database.supabase import supabase
from database import schemas
from func.dashboard.crud.project import *


# Testing
test_user_id = uuid.UUID("5083a3f3-c9b7-4458-a826-e7bc8374991f", version=4)
data = supabase.auth.sign_in_with_password({"email": "koolerjaebee@gmail.com", "password": "1q2w3e$r"})
new_project = schemas.ProjectCreate(PI_id=test_user_id, title="test", grant_number="12-1234-12", isRemovable=True, isDownloadable=True)

create_project(new_project)

test_project_id = uuid.UUID("02865c6e-859d-48c9-8dbb-33501887a445", version=4)

read_project(test_project_id)
read_project_list(test_user_id)

test_project = schemas.ProjectUpdate(id=test_project_id, PI_id=test_user_id, title="test2", grant_number="12-1234-12-2", isRemovable=True, isDownloadable=False)
update_project(test_project)
delete_project(test_project_id)

response = supabase.table("gitrepo").select("*").execute()
