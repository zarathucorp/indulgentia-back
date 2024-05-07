from pydantic import BaseModel
from typing import List, Union, Optional, Any
from datetime import datetime, date


class AllOptional(BaseModel):
    @classmethod
    def __pydantic_init_subclass__(cls, **kwargs: Any) -> None:
        super().__pydantic_init_subclass__(**kwargs)

        for field in cls.model_fields.values():
            if field.is_required():
                field.default = None

        cls.model_rebuild(force=True)


class UserBase(BaseModel):
    email: str
    sign_route: Optional[str] = None
    billing_key: Optional[str] = None
    billing_expired_at: Optional[date] = None

class UserCreate(UserBase):
    password: str

class UserGet(UserBase, AllOptional):
    id: str
    created: datetime
    last_signin: datetime

    def to_dict(self):
        result = self.__dict__
        if self.id is None:
            result.pop("id")
        return result


class ProjectBase(BaseModel):
    title: str
    grant_number: str
    isRemovable: bool = True
    isDownloadable: bool = True

class ProjectCreate(ProjectBase):
    pass

class ProjectGet(ProjectBase, AllOptional):
    id: str
    PI_id: str
    created_at: datetime
    updated_at: datetime

    def to_dict(self):
        result = self.__dict__
        if self.id is None:
            result.pop("id")
        return result
    

class UserProjectBase(BaseModel):
    user_id: str
    research_id: str

class UserProjectCreate(UserProjectBase):
    pass

class UserProjectGet(UserProjectBase, AllOptional):
    id: str



class GitrepoBase(BaseModel):
    research_id: str
    repo_url: str

class GitrepoCreate(GitrepoBase):
    pass

class GitrepoGet(GitrepoBase, AllOptional):
    id: str
    created_at: datetime
    updated_at: datetime

    def to_dict(self):
        result = self.__dict__
        if self.id is None:
            result.pop("id")
        return result


class BucketBase(BaseModel):
    research_id: str
    title: str
    isDefault: bool = False

class BucketCreate(BucketBase):
    pass

class BucketGet(BucketBase, AllOptional):
    id: str
    created_at: datetime
    updated_at: datetime

    def to_dict(self):
        result = self.__dict__
        if self.id is None:
            result.pop("id")
        return result
    

class NoteBase(BaseModel):
    user_id: str
    notebook_id: str
    title: str
    isGitrepo: bool = False

class NoteCreate(NoteBase):
    file_name: str

class NoteGet(NoteBase, AllOptional):
    id: str
    created_at: datetime
    updated_at: datetime
    file_source_name: str
    file_route: str

    def to_dict(self):
        result = self.__dict__
        if self.id is None:
            result.pop("id")
        return result

