from pydantic import BaseModel, UUID4
from typing import List, Union, Optional, Any
from datetime import datetime, date


# class AllOptional(BaseModel):
#     @classmethod
#     def __pydantic_init_subclass__(cls, **kwargs: Any) -> None:
#         super().__pydantic_init_subclass__(**kwargs)

#         for field in cls.model_fields.values():
#             if field.is_required():
#                 field.default = None

#         cls.model_rebuild(force=True)


class UserBase(BaseModel):
    email: str
    sign_route: Optional[str] = None
    billing_key: Optional[str] = None
    billing_expired_at: Optional[date] = None

class UserCreate(UserBase):
    password: str

class UserUpdate(UserBase):
    id: UUID4
    password: str

class User(UserBase):
    id: UUID4
    created: datetime
    last_signin: datetime

    def to_dict(self):
        result = self.__dict__
        if self.id is None:
            result.pop("id")
        return result


class ProjectBase(BaseModel):
    PI_id: UUID4
    title: str
    grant_number: str
    isRemovable: bool = True
    isDownloadable: bool = True

class ProjectCreate(ProjectBase):
    pass

class ProjectUpdate(ProjectBase):
    id: UUID4

class Project(ProjectBase):
    id: UUID4
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    def to_dict(self):
        result = self.__dict__
        if self.id is None:
            result.pop("id")
        return result
    

class UserProjectBase(BaseModel):
    user_id: UUID4
    project_id: str

class UserProjectCreate(UserProjectBase):
    pass

class UserProject(UserProjectBase):
    id: UUID4



class GitrepoBase(BaseModel):
    research_id: UUID4
    repo_url: str

class GitrepoCreate(GitrepoBase):
    pass

class GitrepoUpdate(GitrepoBase):
    id: UUID4

class Gitrepo(GitrepoBase):
    id: UUID4
    created_at: datetime
    updated_at: datetime

    def to_dict(self):
        result = self.__dict__
        if self.id is None:
            result.pop("id")
        return result


class BucketBase(BaseModel):
    project_id: UUID4
    user_id: UUID4
    title: str
    isDefault: bool = False

class BucketCreate(BucketBase):
    pass

class BucketUpdate(BucketBase):
    id: UUID4

class Bucket(BucketBase):
    id: UUID4
    created_at: datetime
    updated_at: datetime

    def to_dict(self):
        result = self.__dict__
        if self.id is None:
            result.pop("id")
        return result
    

class NoteBase(BaseModel):
    user_id: UUID4
    bucket_id: UUID4
    title: str
    isGitrepo: bool = False

class NoteCreate(NoteBase):
    file_name: str

class NoteUpdate(NoteBase):
    id: UUID4
    file_name: str

class Note(NoteBase):
    id: UUID4
    created_at: datetime
    updated_at: datetime
    file_source_name: str
    file_route: str

    def to_dict(self):
        result = self.__dict__
        if self.id is None:
            result.pop("id")
        return result

