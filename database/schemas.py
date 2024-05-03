from pydantic import BaseModel
from typing import List, Union, Optional, Any
from datetime import datetime


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
    billing_expired_at: Optional[datetime] = None

class UserCreate(UserBase):
    password: str

class UserGet(UserBase, AllOptional):
    id: int
    created: datetime
    last_signin: datetime

    def to_dict(self):
        result = self.__dict__
        if self.id is None:
            result.pop("id")
        return result


class ResearchBase(BaseModel):
    title: str
    grant_number: str
    isRemovable: bool = True
    isDownloadable: bool = True

class ResearchCreate(ResearchBase):
    pass

class ResearchGet(ResearchBase, AllOptional):
    id: int
    PI_id: int
    created_at: datetime
    updated_at: datetime

    def to_dict(self):
        result = self.__dict__
        if self.id is None:
            result.pop("id")
        return result
    

class UserResearchBase(BaseModel):
    user_id: int
    research_id: int

class UserResearchCreate(UserResearchBase):
    pass

class UserResearchGet(UserResearchBase, AllOptional):
    id: int



class GitrepoBase(BaseModel):
    research_id: int
    repo_url: str

class GitrepoCreate(GitrepoBase):
    pass

class GitrepoGet(GitrepoBase, AllOptional):
    id: int
    created_at: datetime
    updated_at: datetime

    def to_dict(self):
        result = self.__dict__
        if self.id is None:
            result.pop("id")
        return result


class NotebookBase(BaseModel):
    research_id: int
    title: str
    isDefault: bool = False

class NotebookCreate(NotebookBase):
    pass

class NotebookGet(NotebookBase, AllOptional):
    id: int
    created_at: datetime
    updated_at: datetime

    def to_dict(self):
        result = self.__dict__
        if self.id is None:
            result.pop("id")
        return result
    

class NoteBase(BaseModel):
    user_id: int
    notebook_id: int
    title: str
    isGitrepo: bool = False

class NoteCreate(NoteBase):
    file_name: str

class NoteGet(NoteBase, AllOptional):
    id: int
    created_at: datetime
    updated_at: datetime
    file_source_name: str
    file_route: str

    def to_dict(self):
        result = self.__dict__
        if self.id is None:
            result.pop("id")
        return result

