from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import router

app = FastAPI(
    title="Privax ZK Note Generator API",
    description="API for generating cryptographic notes with commitments and nullifier hashes",
    version="1.0.0",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development only, restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(router)

@app.get("/", tags=["root"])
async def root():
    """Root endpoint with API information."""
    return {
        "name": "Privax ZK Note Generator API",
        "version": "1.0.0",
        "description": "API for generating cryptographic notes with commitments and nullifier hashes",
        "docs_url": "/docs",
    } 