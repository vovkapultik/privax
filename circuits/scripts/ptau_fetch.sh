#!/bin/bash
. ./scripts/build_constants

PTAU_SIZE=""
if [ "$1" ]; then
    PTAU_SIZE=$1
else
  echo "Please provide size of the ptau file to download"
  exit 1
fi

mkdir -p ${PTAU_FOLDER_PATH}

# Download Powers of Tau if not already downloaded
if [ -f "${PTAU_FOLDER_PATH}powers_of_tau_${PTAU_SIZE}.ptau" ]; then
    echo "powers_of_tau_${PTAU_SIZE}.ptau already exists. Skipping."
else
    echo "Downloading powers_of_tau_${PTAU_SIZE}.ptau"
    wget -O "${PTAU_FOLDER_PATH}powers_of_tau_${PTAU_SIZE}.ptau" https://hermez.s3-eu-west-1.amazonaws.com/powersOfTau28_hez_final_${PTAU_SIZE}.ptau
fi 