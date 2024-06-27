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
    first_name: str | None = None
    last_name: str | None = None


# Not using
class UserCreate(UserBase):
    pass


class UserUpdate(UserBase):
    pass

# Not using


class User(UserBase):
    id: UUID4
    team_id: UUID4
    email: str

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
    repo_url: str
    git_username: str
    git_repository: str


class GitrepoCreate(GitrepoBase):
    is_deleted: bool = False


class GitrepoUpdate(GitrepoBase):
    id: UUID4
    user_id: UUID4


class Gitrepo(GitrepoBase):
    user_id: UUID4
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
    timestamp_transaction_id: str | None = None
    file_name: str
    is_github: bool
    github_type: Literal["Commit", "PR", "Issue"] | None = None
    github_hash: str | None = None
    github_link: str | None = None
    pdf_hash: str | None = None


class NoteCreate(NoteBase):
    id: UUID4
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
    status: Literal["READY", "IN_PROGRESS", "WAITING_FOR_DEPOSIT", "DONE", "CANCELED", "PARTIAL_CANCELED", "ABORTED", "EXPIRED"]
    payment_key: str | None = None
    purchase_datetime: datetime | None = None
    is_canceled: bool = False
    total_amount: int
    purchase_user_id: UUID4
    payment_method: Literal["카드", "가상계좌", "간편결제", "휴대폰", "계좌이체", "문화상품권", "도서문화상품권", "게임문화상품권"] | None = None
    currency: str | None = None


class OrderCreate(OrderBase):
    team_id: UUID4
    order_no: str  # need verification?
    refund_amount: int = 0
    notes: str | None = None


class OrderUpdate(OrderBase):
    pass


class Order(OrderBase):
    id: UUID4
    created_at: datetime
    updated_at: datetime | None

    def to_dict(self):
        result = self.__dict__
        if self.id is None:
            result.pop("id")
        return result
    
class OrderWebhook(BaseModel):
    order_no: str
    status: str | None = None
    payment_key: str
    is_canceled: bool = True
    refund_amount: int = 0
    payment_method: str | None = None
    currency: str | None = None
    notes: str | None = None



class CreateSignature(BaseModel):
    file: str


class TeamBase(BaseModel):
    name: str


class TeamCreate(TeamBase):
    pass


class TeamUpdate(TeamBase):
    pass


class SubscriptionBase(BaseModel):
    team_id: UUID4
    started_at: datetime
    expired_at: datetime
    max_members: int
    is_active: bool = False
    order_no: str


class SubscriptionCreate(SubscriptionBase):
    pass


class SubscriptionUpdate(SubscriptionBase):
    pass
