// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "./interfaces/IVerifier.sol";

/**
 * @title PrivaxProtocol
 * @notice A privacy-preserving protocol for the Privax platform.
 * It handles deposits and withdrawals of ERC20 tokens, using ZK-SNARKs for withdrawals.
 * Private state (notes/nullifiers) is managed off-chain; this contract emits events.
 */
contract PrivaxProtocol {
    address public admin;
    IERC20 public immutable token;
    IVerifier public immutable verifier;

    mapping(address => bool) public whitelistedRelayers; // For potential future relayer-specific functions

    // Expected number of public inputs for the ZK proof
    // Example: merkleRoot, nullifierHash, recipient, amount, externalNullifier
    uint256 public constant REQUIRED_PUBLIC_INPUTS_COUNT = 5;

    event AdminChanged(address indexed oldAdmin, address indexed newAdmin);
    event RelayerAdded(address indexed relayerAddress);
    event RelayerRemoved(address indexed relayerAddress);
    event DepositOccurred(
        address indexed user,
        address indexed tokenAddress,
        uint256 amount,
        bytes32 commitment
    );
    event WithdrawalOccurred(
        bytes32 indexed nullifierHash,
        address indexed recipient,
        address indexed tokenAddress,
        uint256 amount
    );

    modifier onlyAdmin() {
        require(msg.sender == admin, "Privax: Caller is not the admin");
        _;
    }

    // This modifier is defined as per spec, but not used in core deposit/withdraw
    // as user calls withdraw directly in this showcase.
    modifier onlyWhitelistedRelayer() {
        require(whitelistedRelayers[msg.sender], "Privax: Caller is not a whitelisted relayer");
        _;
    }

    /**
     * @notice Constructor to initialize the contract.
     * @param _tokenAddress The address of the ERC20 token to be used.
     * @param _verifierAddress The address of the ZK-SNARK Verifier contract.
     */
    constructor(address _tokenAddress, address _verifierAddress) {
        require(_tokenAddress != address(0), "Privax: Invalid token address");
        require(_verifierAddress != address(0), "Privax: Invalid verifier address");

        admin = msg.sender;
        token = IERC20(_tokenAddress);
        verifier = IVerifier(_verifierAddress);
        emit AdminChanged(address(0), msg.sender);
    }

    /**
     * @notice Allows the admin to add an address to the relayer whitelist.
     * @param _relayerAddress The address to add to the whitelist.
     */
    function addRelayer(address _relayerAddress) external onlyAdmin {
        require(_relayerAddress != address(0), "Privax: Invalid relayer address");
        require(!whitelistedRelayers[_relayerAddress], "Privax: Relayer already whitelisted");
        whitelistedRelayers[_relayerAddress] = true;
        emit RelayerAdded(_relayerAddress);
    }

    /**
     * @notice Allows the admin to remove an address from the relayer whitelist.
     * @param _relayerAddress The address to remove from the whitelist.
     */
    function removeRelayer(address _relayerAddress) external onlyAdmin {
        require(whitelistedRelayers[_relayerAddress], "Privax: Relayer not whitelisted");
        whitelistedRelayers[_relayerAddress] = false;
        emit RelayerRemoved(_relayerAddress);
    }

    /**
     * @notice Allows the admin to transfer ownership of the contract.
     * @param _newAdmin The address of the new admin.
     */
    function transferOwnership(address _newAdmin) external onlyAdmin {
        require(_newAdmin != address(0), "Privax: New admin cannot be the zero address");
        emit AdminChanged(admin, _newAdmin);
        admin = _newAdmin;
    }

    /**
     * @notice Allows a user to deposit ERC20 tokens into the contract.
     * The user must have approved the contract to spend their tokens beforehand.
     * @param _amount The amount of tokens to deposit.
     * @param _commitment A cryptographic commitment to the note being created (generated off-chain).
     */
    function deposit(uint256 _amount, bytes32 _commitment) external {
        require(_amount > 0, "Privax: Deposit amount must be greater than zero");

        uint256 initialBalance = token.balanceOf(address(this));
        token.transferFrom(msg.sender, address(this), _amount);
        uint256 finalBalance = token.balanceOf(address(this));
        require(finalBalance == initialBalance + _amount, "Privax: Token transfer failed or incorrect amount");

        emit DepositOccurred(msg.sender, address(token), _amount, _commitment);
    }

    /**
     * @notice Allows a user to withdraw ERC20 tokens by providing a ZK-SNARK proof.
     * @param _a The Groth16 proof component a.
     * @param _b The Groth16 proof component b.
     * @param _c The Groth16 proof component c.
     * @param _publicInputs The public inputs for the ZK proof. Expected order:
     *                      _publicInputs[0]: merkleRoot (uint256)
     *                      _publicInputs[1]: nullifierHash (uint256)
     *                      _publicInputs[2]: recipient (uint256 representation of address)
     *                      _publicInputs[3]: amountToWithdraw (uint256)
     *                      _publicInputs[4]: externalNullifier (uint256, e.g., address(this))
     * @param _recipient The address to receive the withdrawn tokens.
     * @param _amountToWithdraw The amount of tokens to withdraw.
     */
    function withdraw(
        uint256[2] calldata _a,
        uint256[2][2] calldata _b,
        uint256[2] calldata _c,
        uint256[] calldata _publicInputs,
        address _recipient,
        uint256 _amountToWithdraw
    ) external {
        require(_amountToWithdraw > 0, "Privax: Withdrawal amount must be greater than zero");
        require(_recipient != address(0), "Privax: Recipient cannot be the zero address");
        require(_publicInputs.length == REQUIRED_PUBLIC_INPUTS_COUNT, "Privax: Incorrect number of public inputs");

        // Validate that recipient and amount in arguments match those in publicInputs
        // This ensures the proof was generated for these specific parameters.
        // Note: Solidity doesn't have a direct uint160 cast, so we cast address to uint256.
        // The ZK circuit should be designed to handle recipient as uint256(uint160(address)).
        require(uint256(uint160(_recipient)) == _publicInputs[2], "Privax: Recipient mismatch in proof inputs");
        require(_amountToWithdraw == _publicInputs[3], "Privax: Amount mismatch in proof inputs");

        bool isValid = verifier.verifyProof(_a, _b, _c, _publicInputs);
        require(isValid, "Privax: Invalid ZK proof");

        // Extract nullifierHash from public inputs (it's a uint256 in _publicInputs)
        bytes32 nullifierHash = bytes32(_publicInputs[1]);

        uint256 initialRecipientBalance = token.balanceOf(_recipient);
        token.transfer(_recipient, _amountToWithdraw);
        uint256 finalRecipientBalance = token.balanceOf(_recipient);
        require(finalRecipientBalance == initialRecipientBalance + _amountToWithdraw, "Privax: Token transfer failed or incorrect amount");

        emit WithdrawalOccurred(nullifierHash, _recipient, address(token), _amountToWithdraw);
    }

    /**
     * @notice Checks if an address is a whitelisted relayer.
     * @param _address The address to check.
     * @return True if the address is whitelisted, false otherwise.
     */
    function isRelayer(address _address) external view returns (bool) {
        return whitelistedRelayers[_address];
    }
} 