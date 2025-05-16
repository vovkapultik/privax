#!/bin/bash
. ./scripts/build_constants

PTAU_FILE=""
if [ "$1" ]; then
    PTAU_FILE=$1
else
  echo "Please provide path to the ptau file"
  exit 1
fi

CIRCUIT_NAME=""
if [ "$2" ]; then
    CIRCUIT_NAME=$2
else
  echo "Please provide name of the circuit"
  exit 1
fi

# Setup directories for phase2 ceremony artifacts
mkdir -p ${KEYS_FOLDER_PATH}

# Initialize phase 2 of the ceremony
echo "Initializing phase 2 ceremony with circuit $CIRCUIT_NAME..."
if ! snarkjs zkey new ${BINARIES_FOLDER_PATH}${CIRCUIT_NAME}.r1cs ${PTAU_FILE} ${KEYS_FOLDER_PATH}${CIRCUIT_NAME}_0000.zkey; then
    echo "Failed to initialize phase 2 ceremony"
    exit 1
fi

# Contribute to the phase 2 ceremony
echo "Contributing to phase 2 ceremony..."
if ! snarkjs zkey contribute ${KEYS_FOLDER_PATH}${CIRCUIT_NAME}_0000.zkey ${KEYS_FOLDER_PATH}${CIRCUIT_NAME}_0001.zkey --name="First contribution" -e="$(head -n 4096 /dev/urandom | LC_CTYPE=C tr -dc 'a-zA-Z0-9' | fold -w 32 | head -n 1)"; then
    echo "Failed to contribute to phase 2 ceremony"
    exit 1
fi

# Export verification key
echo "Exporting verification key..."
if ! snarkjs zkey export verificationkey ${KEYS_FOLDER_PATH}${CIRCUIT_NAME}_0001.zkey ${KEYS_FOLDER_PATH}${CIRCUIT_NAME}_verification_key.json; then
    echo "Failed to export verification key"
    exit 1
fi

# Generate Solidity verifier
echo "Generating Solidity verifier..."
if ! snarkjs zkey export solidityverifier ${KEYS_FOLDER_PATH}${CIRCUIT_NAME}_0001.zkey ${KEYS_FOLDER_PATH}${CIRCUIT_NAME}_verifier.sol; then
    echo "Failed to generate Solidity verifier"
    exit 1
fi

# Copy verifier to main directory for convenience
cp ${KEYS_FOLDER_PATH}${CIRCUIT_NAME}_verifier.sol ./verifier.sol

echo "Phase 2 ceremony completed successfully!" 