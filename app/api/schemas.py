from pydantic import BaseModel

class ReviewCreate(BaseModel):
    text: str

class ReviewResponse(ReviewCreate):
    id: int
    text: str

    class Config:
        orm_mode = True

class SearchResult(BaseModel):
    id: int
    text: str
    score: float

class TextRequest(BaseModel):
    text: str
    top_n: int = 3