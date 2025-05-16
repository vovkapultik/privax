#!/bin/bash
. ./scripts/build_constants

CIRCUIT_NAME=""
if [ "$1" ]; then
    CIRCUIT_NAME=$1
else
  echo "Please provide name of the circuit"
  exit 1
fi

mkdir -p ${PROOFS_FOLDER_PATH}

# Generate proof
echo "Generating proof..."
snarkjs groth16 prove ${KEYS_FOLDER_PATH}${CIRCUIT_NAME}_0001.zkey ${BINARIES_FOLDER_PATH}${CIRCUIT_NAME}_witness.wtns ${PROOFS_FOLDER_PATH}${CIRCUIT_NAME}_proof.json ${PROOFS_FOLDER_PATH}${CIRCUIT_NAME}_public.json

# Verify proof
echo "Verifying proof..."
snarkjs groth16 verify ${KEYS_FOLDER_PATH}${CIRCUIT_NAME}_verification_key.json ${PROOFS_FOLDER_PATH}${CIRCUIT_NAME}_public.json ${PROOFS_FOLDER_PATH}${CIRCUIT_NAME}_proof.json

echo "Proof generated and verified successfully!" 