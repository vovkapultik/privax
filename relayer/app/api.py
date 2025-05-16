from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel, Field, constr
from typing import Optional, Dict, Any, List
import logging
import asyncio

from .relayer import Relayer
from .blockchain.ethereum import EthereumListener
from .blockchain.solana import SolanaListener

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Initialize relayer
relayer = Relayer()

# Create FastAPI app
app = FastAPI(
    title="Privax Relayer",
    description="API for interacting with privacy protocol relayer",
    version="0.1.0"
)

# Initialize background listeners
ethereum_listener = None
solana_listener = None
background_tasks = set()

# --- Pydantic models for API requests/responses ---

class CommitmentQuery(BaseModel):
    commitment: str = Field(..., description="Hex-encoded commitment value")

class WithdrawalRequest(BaseModel):
    nullifier_hash: str = Field(..., description="Hex-encoded nullifier hash")
    commitment: str = Field(..., description="Hex-encoded commitment being spent")
    recipient: str = Field(..., description="Recipient address")
    token: str = Field(..., description="Token address")
    amount: int = Field(..., description="Amount to withdraw")
    # In a real implementation, you'd also include a ZK proof
    # proof: dict = Field(..., description="Zero-knowledge proof")

class MerkleRoot(BaseModel):
    root: Optional[str] = Field(None, description="Current Merkle root")

class MerklePathResponse(BaseModel):
    leaf_index: int = Field(..., description="Index of the leaf in the tree")
    path_elements: List[str] = Field(..., description="Merkle path elements (sibling hashes)")
    path_indices: List[int] = Field(..., description="Path indices (0=left, 1=right)")

class ZeroCommitmentInfo(BaseModel):
    zero_commitment: str = Field(..., description="The zero commitment hash")
    is_in_tree: bool = Field(..., description="Whether the zero commitment is in the Merkle tree")
    leaf_index: Optional[int] = Field(None, description="The leaf index of the zero commitment if in the tree")

# --- Helper functions ---

async def start_blockchain_listeners():
    """Start blockchain event listeners in the background"""
    global ethereum_listener, solana_listener
    
    # Initialize Ethereum listener if not already running
    if not ethereum_listener or not ethereum_listener.running:
        try:
            ethereum_listener = EthereumListener(relayer)
            task = asyncio.create_task(ethereum_listener.start())
            background_tasks.add(task)
            task.add_done_callback(background_tasks.discard)
            logger.info("Started Ethereum listener")
        except Exception as e:
            logger.error(f"Failed to start Ethereum listener: {str(e)}")
    
    # Initialize Solana listener if not already running
    if not solana_listener or not solana_listener.running:
        try:
            solana_listener = SolanaListener(relayer)
            task = asyncio.create_task(solana_listener.start())
            background_tasks.add(task)
            task.add_done_callback(background_tasks.discard)
            logger.info("Started Solana listener")
        except Exception as e:
            logger.error(f"Failed to start Solana listener: {str(e)}")

# --- API Endpoints ---

@app.on_event("startup")
async def startup_event():
    """Start background tasks on application startup"""
    background_tasks = BackgroundTasks()
    background_tasks.add_task(start_blockchain_listeners)

@app.on_event("shutdown")
async def shutdown_event():
    """Stop background tasks on application shutdown"""
    if ethereum_listener:
        await ethereum_listener.stop()
    if solana_listener:
        await solana_listener.stop()
    logger.info("Stopped blockchain listeners")

@app.get("/", tags=["Health"])
async def root():
    """Health check endpoint"""
    return {"status": "Relayer is running"}

@app.get("/merkle_root", response_model=MerkleRoot, tags=["Merkle Tree"])
async def get_merkle_root():
    """Get the current Merkle root"""
    root = relayer.get_merkle_root()
    return {"root": root}

@app.get("/merkle_path", response_model=MerklePathResponse, tags=["Merkle Tree"])
async def get_merkle_path(commitment: str):
    """
    Get the Merkle path for a commitment
    
    - **commitment**: Hex-encoded commitment value
    """
    try:
        path_info = relayer.get_merkle_path(commitment)
        return path_info
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.post("/withdraw", tags=["Withdrawals"])
async def submit_withdrawal(request: WithdrawalRequest):
    """
    Submit a withdrawal request
    
    In a real implementation, this would verify a ZK proof
    """
    try:
        result = relayer.submit_withdrawal(
            request.nullifier_hash,
            request.commitment,
            request.recipient,
            request.token,
            request.amount
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/nullifier/{nullifier_hash}", tags=["Nullifiers"])
async def check_nullifier(nullifier_hash: str):
    """
    Check if a nullifier has been used
    
    - **nullifier_hash**: Hex-encoded nullifier hash
    """
    is_used = relayer.is_nullifier_used(nullifier_hash)
    return {"nullifier": nullifier_hash, "is_used": is_used}

@app.get("/zero_commitment", response_model=ZeroCommitmentInfo, tags=["Merkle Tree"])
async def get_zero_commitment():
    """Get information about the zero commitment used to initialize the Merkle tree"""
    info = relayer.get_zero_commitment()
    return info 