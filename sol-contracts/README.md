# Privax Protocol

Privax Protocol is a privacy-focused solution built on Solana that enables confidential token transfers using zero-knowledge proofs.

## Features

- **Private Transactions**: Deposit tokens and withdraw them privately using ZK proofs
- **Relayer System**: Support for gas-less private withdrawals via whitelisted relayers
- **Secure Architecture**: Uses ZK proofs to verify transaction validity without revealing sensitive information

## Technical Architecture

Privax Protocol uses the Anchor framework on Solana and incorporates zero-knowledge proof technology for privacy-preserving transactions.

## Development

### Prerequisites

- Rust and Cargo
- Solana CLI tools
- Anchor framework
- Node.js and yarn/npm

### Build and Deploy

```bash
# Build the program
anchor build

# Deploy to localnet
anchor deploy

# Run tests
anchor test
```

## License

[MIT](LICENSE)