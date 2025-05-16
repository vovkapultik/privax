from .merkle import MerkleTree, ZERO_COMMITMENT
from .persistence import RelayerPersistence
import logging
import os

logger = logging.getLogger(__name__)

class Relayer:
    def __init__(self, data_dir=None):
        # Initialize persistence
        self.persistence = RelayerPersistence(data_dir or os.getenv("DATA_DIR", "./data"))
        
        # Load state from disk
        self.used_nullifiers = self.persistence.load_nullifiers()
        self.deposits = self.persistence.load_deposits()
        self.withdrawals = self.persistence.load_withdrawals()
        
        # Load leaves from persistence
        persisted_leaves = self.persistence.load_leaves()
        
        # Initialize Merkle tree
        # If we have persisted leaves, don't initialize with zero commitment
        if persisted_leaves:
            logger.info(f"Initializing Merkle tree with {len(persisted_leaves)} persisted leaves")
            self.merkle_tree = MerkleTree(initialize_with_zero=False)
            for leaf in persisted_leaves:
                self.merkle_tree.add_leaf(leaf)
        else:
            # Initialize with default zero commitment
            logger.info("Initializing Merkle tree with default zero commitment")
            self.merkle_tree = MerkleTree(initialize_with_zero=True)
            # Persist the zero commitment
            self.persistence.save_leaves(self.merkle_tree.leaves)
        
        logger.info(f"Relayer initialized with {len(self.merkle_tree.leaves)} leaves and {len(self.used_nullifiers)} used nullifiers")
        logger.info(f"Current Merkle root: {self.merkle_tree.get_merkle_root()}")

    def process_deposit(self, user_address, token_address, amount, commitment_hex):
        """
        Process a deposit event from the blockchain
        
        Args:
            user_address: The address of the user making the deposit
            token_address: The address of the token being deposited
            amount: The amount being deposited
            commitment_hex: The commitment hash for this deposit
        """
        logger.info(f"Processing deposit: {commitment_hex[:10]}...")
        
        # Store deposit info
        self.deposits[commitment_hex] = {
            "user": user_address,
            "token": token_address,
            "amount": amount,
            "timestamp": None  # Would be set to block timestamp in a real implementation
        }
        
        # Add commitment to Merkle tree
        self.merkle_tree.add_leaf(commitment_hex)
        
        # Persist state
        self.persistence.save_deposits(self.deposits)
        self.persistence.save_leaves(self.merkle_tree.leaves)
        
        logger.info(f"Deposit processed. New Merkle Root: {self.merkle_tree.get_merkle_root()[:10]}...")
        return self.merkle_tree.get_merkle_root()

    def process_withdrawal(self, nullifier_hash_hex, recipient_address, token_address, amount):
        """
        Process a withdrawal event from the blockchain
        
        Args:
            nullifier_hash_hex: The nullifier hash for this withdrawal
            recipient_address: The address receiving the withdrawal
            token_address: The token address being withdrawn
            amount: The amount being withdrawn
        """
        logger.info(f"Processing withdrawal event for nullifier: {nullifier_hash_hex[:10]}...")
        
        # Mark the nullifier as used (even though it's already used on-chain)
        self.used_nullifiers.add(nullifier_hash_hex)
        
        # Store withdrawal info
        self.withdrawals[nullifier_hash_hex] = {
            "recipient": recipient_address,
            "token": token_address,
            "amount": amount,
            "timestamp": None  # Would be set to block timestamp in a real implementation
        }
        
        # Persist state
        self.persistence.save_nullifiers(self.used_nullifiers)
        self.persistence.save_withdrawals(self.withdrawals)
        
        logger.info(f"Withdrawal event processed for nullifier: {nullifier_hash_hex[:10]}...")
        return True

    def is_nullifier_used(self, nullifier_hash_hex):
        """
        Check if a nullifier has been used
        
        Args:
            nullifier_hash_hex: The nullifier hash to check
        
        Returns:
            bool: True if the nullifier has been used, False otherwise
        """
        return nullifier_hash_hex in self.used_nullifiers

    def get_merkle_root(self):
        """
        Get the current Merkle root
        
        Returns:
            str: The current Merkle root hex string
        """
        return self.merkle_tree.get_merkle_root()

    def get_merkle_path(self, commitment_hex):
        """
        Get the Merkle path for a commitment
        
        Args:
            commitment_hex: The commitment to get the path for
            
        Returns:
            dict: The Merkle path information including leaf_index, path_elements, and path_indices
        
        Raises:
            ValueError: If the commitment is not found in the tree
        """
        try:
            return self.merkle_tree.get_merkle_path(commitment_hex)
        except ValueError as e:
            logger.error(f"Error getting Merkle path for {commitment_hex[:10]}...: {str(e)}")
            raise

    def submit_withdrawal(self, nullifier_hash_hex, commitment_hex, recipient_address, token_address, amount):
        """
        Submit a withdrawal request
        
        Args:
            nullifier_hash_hex: The nullifier hash for this withdrawal
            commitment_hex: The commitment being spent
            recipient_address: The address to receive the withdrawal
            token_address: The token address being withdrawn
            amount: The amount being withdrawn
            
        Returns:
            dict: The result of the withdrawal request
            
        Raises:
            ValueError: If the nullifier has already been used or other validation fails
        """
        # Check if nullifier has been used
        if self.is_nullifier_used(nullifier_hash_hex):
            logger.warning(f"Nullifier already used: {nullifier_hash_hex[:10]}...")
            raise ValueError("Nullifier already used")
        
        # Verify the commitment exists in the tree
        try:
            merkle_path = self.get_merkle_path(commitment_hex)
        except ValueError:
            logger.warning(f"Commitment not found in Merkle tree: {commitment_hex[:10]}...")
            raise ValueError("Commitment not found in Merkle tree")
        
        # In a real implementation, additional verification would happen here
        # such as verifying a ZK proof that proves the user owns this note
        
        # Mark the nullifier as used
        self.used_nullifiers.add(nullifier_hash_hex)
        
        # Store withdrawal info
        self.withdrawals[nullifier_hash_hex] = {
            "recipient": recipient_address,
            "token": token_address,
            "amount": amount,
            "commitment": commitment_hex,
            "timestamp": None  # Would be set to current time in a real implementation
        }
        
        # Persist state
        self.persistence.save_nullifiers(self.used_nullifiers)
        self.persistence.save_withdrawals(self.withdrawals)
        
        logger.info(f"Withdrawal request accepted for nullifier: {nullifier_hash_hex[:10]}...")
        
        return {
            "status": "success",
            "merkle_path": merkle_path,
            "nullifier_hash": nullifier_hash_hex,
            "recipient": recipient_address,
            "token": token_address,
            "amount": amount
        }

    def get_zero_commitment(self):
        """
        Get information about the zero commitment
        
        Returns:
            dict: Information about the zero commitment
        """
        return {
            "zero_commitment": ZERO_COMMITMENT,
            "is_in_tree": ZERO_COMMITMENT in self.merkle_tree.leaves,
            "leaf_index": self.merkle_tree.leaves.index(ZERO_COMMITMENT) if ZERO_COMMITMENT in self.merkle_tree.leaves else None
        } 