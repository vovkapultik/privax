# Privax Protocol Withdraw Circuit

A zero-knowledge protocol for private deposits and withdrawals using circom and zk-SNARKs.

## Overview

This project implements a privacy-preserving system that allows users to:

1. **Deposit** funds by creating a commitment (a hash of amount and secrets)
2. **Withdraw** funds later by providing a zero-knowledge proof that:
   - They know the secrets used to create a commitment in the Merkle tree
   - The commitment is part of the Merkle tree (via Merkle proof)
   - They haven't withdrawn these funds before (via nullifier)

The system ensures:
- **Privacy**: No one can link deposits to withdrawals
- **Security**: Only the rightful owner of a deposit can withdraw
- **Non-double spending**: Each deposit can only be withdrawn once

## Project Structure

```
├── circuits/              # Circom circuit files
│   ├── circuit.circom     # The withdrawal circuit implementation
│   └── main.circom        # Main entry point for the circuit
├── build/                 # Generated build files
│   ├── binaries/          # Compiled circuit binaries
│   ├── keys/              # zk-SNARK proving and verification keys
│   ├── proofs/            # Generated proofs
│   └── ptau/              # Powers of Tau files
├── inputs/                # Input files for circuits
│   └── main_input.json    # Sample input for the withdrawal circuit
├── scripts/               # Helper scripts for circuit compilation and proof generation
│   ├── build_constants    # Constants for build paths
│   ├── compile.sh         # Script to compile circuits
│   ├── proof_generate.sh  # Script to generate and verify proofs
│   ├── ptau_fetch.sh      # Script to download Powers of Tau
│   ├── ptau_phase2.sh     # Script for phase 2 ceremony
│   └── witness.sh         # Script to generate witness
├── tests/                 # Test files
│   └── withdraw.test.ts   # Tests for the withdrawal circuit
└── utils/                 # Utility functions
    └── merkleTree.ts      # Implementation of Merkle tree and related functions
```

## How It Works

### Deposit Process
1. User generates random secrets (`secret` and `nullifierSecret`)
2. User creates a commitment `H(amount, secret, nullifierSecret)`
3. User sends funds along with the commitment to the contract
4. Commitment is added to the Merkle tree

### Withdrawal Process
1. User creates a zk-SNARK proof showing they know:
   - The secrets for a valid commitment in the tree
   - The Merkle path from the commitment to the root
2. User also provides a nullifier hash `H(nullifierSecret, 1)` 
3. The contract verifies the proof and checks if the nullifier has been used
4. If valid, the contract sends funds to the recipient and records the nullifier

## Prerequisites

- Node.js v14+
- Circom 2.1.5
- Solidity 0.8.17+

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/zk-commitment-protocol.git
cd zk-commitment-protocol
```

2. Install dependencies:
```bash
yarn install
```

## Usage

### Build the Circuit and Generate Proofs

The project includes scripts to handle the full workflow:

```bash
# Compile the circuit
yarn compile

# Download Powers of Tau parameters
yarn ptau:fetch

# Generate Phase 2 keys
yarn ptau:phase2

# Generate witness
yarn witness:generate

# Generate and verify proof
yarn proof:generate

# Or, run everything at once
yarn build
```

### Running Tests

```bash
yarn test
```

## Development

- To modify the circuit, edit `circuits/circuit.circom`
- To change the inputs, modify `inputs/main_input.json`
- To adjust test cases, update `tests/withdraw.test.ts`

## Security Considerations

- The security of this system relies on the secrecy of the user's secrets
- The Merkle tree implementation should be carefully audited in production
- Proper trusted setup ceremonies should be conducted for real applications

## License

MIT

## Acknowledgments

- Circom team for the amazing ZK circuit compiler
- SnarkJS for the proving system implementation