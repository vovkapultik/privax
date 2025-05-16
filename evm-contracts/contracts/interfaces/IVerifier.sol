// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

/**
 * @title IVerifier
 * @notice Interface for the ZK-SNARK Verifier contract.
 */
interface IVerifier {
    /**
     * @notice Verifies a ZK-SNARK proof.
     * @param a The Groth16 proof component a.
     * @param b The Groth16 proof component b.
     * @param c The Groth16 proof component c.
     * @param publicInputs The public inputs to the circuit.
     * @return valid True if the proof is valid, false otherwise.
     */
    function verifyProof(
        uint256[2] calldata a,
        uint256[2][2] calldata b,
        uint256[2] calldata c,
        uint256[] calldata publicInputs
    ) external view returns (bool valid);
} 