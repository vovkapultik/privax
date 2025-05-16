#!/bin/bash
. ./scripts/build_constants

CIRCUIT_NAME=""
if [ "$1" ]; then
    CIRCUIT_NAME=$1
else
  echo "Please provide name of the circuit"
  exit 1
fi

# Generate witness
echo "Generating witness..."
cd ${BINARIES_FOLDER_PATH}${CIRCUIT_NAME}_js
node generate_witness.js ${CIRCUIT_NAME}.wasm ${INPUTS_FOLDER_PATH}${CIRCUIT_NAME}_input.json ${CIRCUIT_NAME}_witness.wtns
cp ${CIRCUIT_NAME}_witness.wtns ../
cd -

echo "Witness generated successfully!" 