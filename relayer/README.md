# Privax Protocol Relayer

A draft relayer service for privacy protocols that implements the following functionality:

1. Listens to on-chain events from Ethereum, Solana, or other blockchains for:
   - Deposit events: `DepositOccurred(address indexed user, address indexed token, uint256 amount, bytes32 commitment)`
   - Withdrawal events: `WithdrawalOccurred(bytes32 indexed nullifierHash, address indexed recipient, address indexed token, uint256 amount)`

2. Maintains a Merkle tree of commitments from deposit events

3. Provides API endpoints for:
   - Getting the current Merkle root
   - Getting Merkle paths for commitments
   - Submitting withdrawal requests (checking for used nullifiers)

## Setup

### Option 1: Local Setup

1. Clone the repository:
   ```
   git clone <repository-url>
   cd relayer
   ```

2. Create a virtual environment and install dependencies:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. Create a `.env` file with your blockchain provider details:
   ```
   # Blockchain provider URLs
   ETH_RPC_URL=https://mainnet.infura.io/v3/your-project-id
   SOLANA_RPC_URL=https://api.mainnet-beta.solana.com
   
   # Contract addresses
   ETH_CONTRACT_ADDRESS=0x0000000000000000000000000000000000000000
   SOLANA_CONTRACT_ADDRESS=your-program-address
   
   # API configuration
   PORT=8000
   HOST=0.0.0.0
   ```

### Option 2: Docker Setup

1. Clone the repository:
   ```
   git clone <repository-url>
   cd relayer
   ```

2. Create a `.env` file as described above.

3. Build and run with Docker Compose:
   ```
   docker-compose up -d
   ```

   This will:
   - Build the Docker image for the relayer
   - Start the relayer container
   - Mount a volume for persistent data storage
   - Expose the API on port 8000

## Usage

### Running Locally

```
python run.py
```

### Docker Commands

- Start the relayer:
  ```
  docker-compose up -d
  ```

- View logs:
  ```
  docker-compose logs -f
  ```

- Stop the relayer:
  ```
  docker-compose down
  ```

The API will be available at `http://localhost:8000` with the following endpoints:

- `GET /`: Health check
- `GET /merkle_root`: Get the current Merkle root
- `GET /merkle_path?commitment=<hex>`: Get the Merkle path for a commitment
- `POST /withdraw`: Submit a withdrawal request
- `GET /nullifier/{nullifier_hash}`: Check if a nullifier has been used
- `GET /zero_commitment`: Get information about the zero commitment

## API Documentation

When the server is running, API documentation is available at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Development

### Local Development

To start the server in development mode with auto-reload:

```
uvicorn app.api:app --reload --host 0.0.0.0 --port 8000
```

### Docker Development

For development with Docker, we provide a separate `docker-compose.dev.yml` file that includes:
- Hot-reloading: code changes are immediately reflected in the running container
- Source code mounting: the entire codebase is mounted into the container

To use the development Docker setup:

```
docker-compose -f docker-compose.dev.yml up
```

This setup is useful for:
- Testing changes without rebuilding the Docker image
- Ensuring your code works in a containerized environment
- Maintaining parity between development and production environments

## Architecture

- `app/merkle.py`: Implementation of the Merkle tree
- `app/relayer.py`: Core relayer functionality
- `app/blockchain/`: Blockchain event listeners
- `app/api.py`: FastAPI API endpoints
- `app/main.py`: Application entry point
- `app/persistence.py`: State persistence for the relayer

## Data Persistence

The relayer persists its state to the `./data` directory (or the mounted volume in Docker):

- `nullifiers.json`: Set of used nullifier hashes
- `leaves.json`: List of Merkle tree leaves (commitments)
- `deposits.json`: Mapping of commitments to deposit info
- `withdrawals.json`: Mapping of nullifier hashes to withdrawal info

## Technical Details

### Merkle Tree Implementation

The relayer maintains a Merkle tree of deposit commitments. Key features:

- **Zero Commitment**: The tree is initialized with a default "zero commitment" leaf to ensure the tree always has a valid structure, even before any real deposits are made.
- **Persistence**: The tree state is persisted to disk, allowing the relayer to recover after restarts.
- **Path Generation**: The relayer can generate Merkle paths for any commitment in the tree, which are used in zero-knowledge proofs.

### Nullifier Handling

To prevent double-spending, the relayer tracks used nullifiers:

- Each withdrawal includes a nullifier hash
- The relayer checks if the nullifier has been used before
- Once a nullifier is used, it cannot be used again

### API Endpoints

The relayer provides RESTful API endpoints for clients:

- `GET /merkle_root`: Get the current Merkle root
- `GET /merkle_path?commitment=hex`: Get the Merkle path for a commitment
- `POST /withdraw`: Submit a withdrawal request
- `GET /nullifier/{nullifier_hash}`: Check if a nullifier has been used
- `GET /zero_commitment`: Get information about the zero commitment used to initialize the tree