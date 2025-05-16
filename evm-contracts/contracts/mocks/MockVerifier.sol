// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "../interfaces/IVerifier.sol";

/**
 * @title MockVerifier
 * @notice Mock verifier for testing purposes
 */
contract MockVerifier is IVerifier {
    bool private _verificationResult = true;
    
    /**
     * @notice Set the result that the verifier should return
     * @param result Boolean value to return on verification
     */
    function setVerificationResult(bool result) external {
        _verificationResult = result;
    }
    
    /**
     * @notice Mock implementation of the verification function
     * @return valid The predetermined verification result
     */
    function verifyProof(
        uint256[2] calldata,
        uint256[2][2] calldata,
        uint256[2] calldata,
        uint256[] calldata
    ) external view override returns (bool) {
        return _verificationResult;
    }
} 