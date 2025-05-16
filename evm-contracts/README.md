# Privax Protocol

A privacy-preserving protocol for the Privax platform, utilizing ZK-SNARKs for secure and private token transfers on Ethereum.

## Overview

The Privax Protocol is a key component of the Privax platform that enables confidential and private token transfers using zero-knowledge proofs. The protocol allows users to:

- Deposit ERC20 tokens with a cryptographic commitment
- Withdraw tokens by providing a valid ZK-SNARK proof
- Manage trusted relayers through a whitelist system

## Project Structure

```
evm-contracts/
├── contracts/
│   ├── interfaces/
│   │   └── IVerifier.sol         # Interface for the ZK-SNARK verifier
│   ├── mocks/
│   │   ├── MockERC20.sol         # Mock ERC20 token for testing
│   │   └── MockVerifier.sol      # Mock verifier for testing
│   └── PrivaxProtocol.sol        # Main Privax protocol contract
├── scripts/
│   └── deploy.js                 # Deployment script
└── test/
    └── PrivaxProtocol.test.js    # Test file
```

## Environment Setup

Create a `.env` file based on the following template:

```
# Network API keys
INFURA_API_KEY=your_infura_api_key
ALCHEMY_API_KEY=your_alchemy_api_key

# Contract verification
ETHERSCAN_API_KEY=your_etherscan_api_key

# Deployment account private key (without 0x prefix)
PRIVATE_KEY=your_private_key_without_0x_prefix

# Contract addresses for deployment on testnets/mainnet
TOKEN_ADDRESS=0x0000000000000000000000000000000000000000
VERIFIER_ADDRESS=0x0000000000000000000000000000000000000000
```

## Installation

```bash
npm install
```

## Running Tests

```bash
npx hardhat test
```

## Deployment

### Local Development Network

```bash
npx hardhat node
npx hardhat run scripts/deploy.js --network localhost
```

### Testnet Deployment

```bash
npx hardhat run scripts/deploy.js --network sepolia
```

## Contract Verification

After deployment, verify the contract on Etherscan:

```bash
npx hardhat verify --network sepolia CONTRACT_ADDRESS TOKEN_ADDRESS VERIFIER_ADDRESS
```

## Privax Protocol Usage

1. **Deposit**: Users can deposit Privax tokens into the protocol by calling the `deposit` function with an amount and a commitment.
   
2. **Withdraw**: Users can withdraw tokens by providing a valid ZK-SNARK proof through the `withdraw` function, ensuring complete privacy.

3. **Admin functions**: The Privax platform admin can add/remove relayers and transfer ownership.

## Security Features

The Privax Protocol implements several security features:

- Zero-knowledge proofs for private transactions
- Cryptographic commitments for deposits
- Nullifier hashes to prevent double-spending
- Admin controls for platform governance

## License

MIT