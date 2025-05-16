from pydantic import BaseModel, Field
from typing import Optional

class NoteRequest(BaseModel):
    amount: int = Field(..., description="The amount of tokens in the note", gt=0)
    secret: Optional[str] = Field(None, description="Custom secret (optional)")
    nullifier_secret: Optional[str] = Field(None, description="Custom nullifier secret (optional)")

class NoteResponse(BaseModel):
    amount: int
    secret: str
    nullifier_secret: str
    commitment: str
    nullifier_hash: str

    class Config:
        schema_extra = {
            "example": {
                "amount": 100,
                "secret": "2a3f1e5d8c7b9a0f6e4d2c1b0a9f8e7d6c5b4a3f2e1d0c9b8a7f6e5d4c3b2a1",
                "nullifier_secret": "7d6c5b4a3f2e1d0c9b8a7f6e5d4c3b2a12a3f1e5d8c7b9a0f6e4d2c1b0a9f8e",
                "commitment": "5e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e",
                "nullifier_hash": "0a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a"
            }
        } 