from fastapi import APIRouter, HTTPException
from app.models import NoteRequest, NoteResponse
from app.crypto.note import Note

router = APIRouter(prefix="/api/v1", tags=["notes"])

@router.post("/notes", response_model=NoteResponse, summary="Generate a new note")
async def create_note(request: NoteRequest):
    """
    Create a new privacy note with the specified amount.
    
    - **amount**: The amount of tokens in the note (positive integer)
    - **secret** (optional): Custom secret for the note
    - **nullifier_secret** (optional): Custom nullifier secret for the note
    
    Returns a note with commitment and nullifier hash.
    """
    try:
        note = Note(
            amount=request.amount,
            secret=request.secret,
            nullifier_secret=request.nullifier_secret
        )
        return note.to_dict()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to create note: {str(e)}")

@router.get("/health", summary="Health check endpoint")
async def health_check():
    """Simple health check endpoint to verify API is up and running."""
    return {"status": "healthy"} 