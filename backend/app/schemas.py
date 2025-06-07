from pydantic import BaseModel
from typing import List, Optional

class UserCreate(BaseModel):
    username: str
    email: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class ProposalCreate(BaseModel):
    topic: str
    sdgs: List[str]
    objectives: str

class Proposal(BaseModel):
    id: int
    topic: str
    content: str

    class Config:
        orm_mode = True

class DonorCallCreate(BaseModel):
    title: str
    description: str
    sdg_tags: List[str]
    keywords: List[str]

class DonorCall(BaseModel):
    id: int
    title: str
    description: str
    sdg_tags: List[str]
    keywords: List[str]

    class Config:
        orm_mode = True
