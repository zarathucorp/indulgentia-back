from pydantic import BaseModel, UUID4
from typing import List, Union, Optional, Any, Literal
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
    team_id: UUID4 | None = None
    signature_path: str | None = None
    is_admin: bool = False


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
    team_id: UUID4
    project_leader: str | None = None
    title: str
    grant_number: str | None = None
    status: str | None = None
    start_date: datetime | None = None
    end_date: datetime | None = None


class ProjectCreate(ProjectBase):
    is_deleted: bool = False


class ProjectUpdate(ProjectBase):
    id: UUID4


class Project(ProjectBase):
    id: UUID4
    created_at: datetime
    updated_at: datetime | None
    is_deleted: bool

    def to_dict(self):
        result = self.__dict__
        if self.id is None:
            result.pop("id")
        return result

# # Duplicated
# class UserProjectBase(BaseModel):
#     user_id: UUID4
#     project_id: str

# class UserProjectCreate(UserProjectBase):
#     pass

# class UserProject(UserProjectBase):
#     id: UUID4


class GitrepoBase(BaseModel):
    bucket_id: UUID4
    user_id: UUID4
    repo_url: str
    git_username: str
    git_repository: str


class GitrepoCreate(GitrepoBase):
    pass


class GitrepoUpdate(GitrepoBase):
    id: UUID4


class Gitrepo(GitrepoBase):
    id: UUID4
    created_at: datetime
    updated_at: datetime | None

    def to_dict(self):
        result = self.__dict__
        if self.id is None:
            result.pop("id")
        return result


class BucketBase(BaseModel):
    project_id: UUID4
    # manager_id: UUID4
    manager_id: str
    title: str
    # is_default: bool = False
    # is_github: bool = False


class BucketCreate(BucketBase):
    is_deleted: bool = False


class BucketUpdate(BucketBase):
    id: UUID4


class Bucket(BucketBase):
    id: UUID4
    created_at: datetime
    updated_at: datetime | None
    is_deleted: bool

    def to_dict(self):
        result = self.__dict__
        if self.id is None:
            result.pop("id")
        return result


class NoteBase(BaseModel):
    user_id: UUID4
    bucket_id: UUID4
    title: str
    # timestamp_authentication: str  # need verification?
    file_name: str
    is_github: bool
    # github_type: Literal["Commit", "PR", "Issue"] | None
    # github_hash: str | None
    # github_link: str | None


class NoteCreate(NoteBase):
    is_deleted: bool = False


class NoteUpdate(NoteBase):
    id: UUID4


class Note(NoteBase):
    id: UUID4
    created_at: datetime
    updated_at: datetime | None
    is_deleted: bool

    def to_dict(self):
        result = self.__dict__
        if self.id is None:
            result.pop("id")
        return result


class OrderBase(BaseModel):
    team_id: UUID4
    order_number: str  # need verification?
    started_at: date
    expired_at: date


class OrderCreate(OrderBase):
    pass


class OrderUpdate(OrderBase):
    id: UUID4


class Order(OrderBase):
    id: UUID4
    created_at: datetime
    updated_at: datetime | None

    def to_dict(self):
        result = self.__dict__
        if self.id is None:
            result.pop("id")
        return result
