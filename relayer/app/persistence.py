import os
import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class RelayerPersistence:
    """Handles persistence of relayer state to disk"""
    
    def __init__(self, data_dir="./data"):
        """
        Initialize persistence with the data directory
        
        Args:
            data_dir: Path to the data directory
        """
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True, parents=True)
        
        self.nullifiers_file = self.data_dir / "nullifiers.json"
        self.leaves_file = self.data_dir / "leaves.json"
        self.deposits_file = self.data_dir / "deposits.json"
        self.withdrawals_file = self.data_dir / "withdrawals.json"
        
        logger.info(f"Persistence initialized with data directory: {self.data_dir}")

    def save_nullifiers(self, nullifiers):
        """
        Save the used nullifiers set to disk
        
        Args:
            nullifiers: Set of used nullifier hashes
        """
        try:
            with open(self.nullifiers_file, "w") as f:
                json.dump(list(nullifiers), f)
            logger.debug(f"Saved {len(nullifiers)} nullifiers to {self.nullifiers_file}")
        except Exception as e:
            logger.error(f"Error saving nullifiers: {str(e)}")

    def load_nullifiers(self):
        """
        Load the used nullifiers set from disk
        
        Returns:
            Set of used nullifier hashes
        """
        if not self.nullifiers_file.exists():
            logger.debug(f"Nullifiers file {self.nullifiers_file} does not exist, returning empty set")
            return set()
        
        try:
            with open(self.nullifiers_file, "r") as f:
                nullifiers = set(json.load(f))
            logger.debug(f"Loaded {len(nullifiers)} nullifiers from {self.nullifiers_file}")
            return nullifiers
        except Exception as e:
            logger.error(f"Error loading nullifiers: {str(e)}")
            return set()

    def save_leaves(self, leaves):
        """
        Save the Merkle tree leaves to disk
        
        Args:
            leaves: List of leaf values
        """
        try:
            with open(self.leaves_file, "w") as f:
                json.dump(leaves, f)
            logger.debug(f"Saved {len(leaves)} leaves to {self.leaves_file}")
        except Exception as e:
            logger.error(f"Error saving leaves: {str(e)}")

    def load_leaves(self):
        """
        Load the Merkle tree leaves from disk
        
        Returns:
            List of leaf values
        """
        if not self.leaves_file.exists():
            logger.debug(f"Leaves file {self.leaves_file} does not exist, returning empty list")
            return []
        
        try:
            with open(self.leaves_file, "r") as f:
                leaves = json.load(f)
            logger.debug(f"Loaded {len(leaves)} leaves from {self.leaves_file}")
            return leaves
        except Exception as e:
            logger.error(f"Error loading leaves: {str(e)}")
            return []

    def save_deposits(self, deposits):
        """
        Save deposits to disk
        
        Args:
            deposits: Dict mapping commitment to deposit info
        """
        try:
            with open(self.deposits_file, "w") as f:
                json.dump(deposits, f)
            logger.debug(f"Saved {len(deposits)} deposits to {self.deposits_file}")
        except Exception as e:
            logger.error(f"Error saving deposits: {str(e)}")

    def load_deposits(self):
        """
        Load deposits from disk
        
        Returns:
            Dict mapping commitment to deposit info
        """
        if not self.deposits_file.exists():
            logger.debug(f"Deposits file {self.deposits_file} does not exist, returning empty dict")
            return {}
        
        try:
            with open(self.deposits_file, "r") as f:
                deposits = json.load(f)
            logger.debug(f"Loaded {len(deposits)} deposits from {self.deposits_file}")
            return deposits
        except Exception as e:
            logger.error(f"Error loading deposits: {str(e)}")
            return {}

    def save_withdrawals(self, withdrawals):
        """
        Save withdrawals to disk
        
        Args:
            withdrawals: Dict mapping nullifier hash to withdrawal info
        """
        try:
            with open(self.withdrawals_file, "w") as f:
                json.dump(withdrawals, f)
            logger.debug(f"Saved {len(withdrawals)} withdrawals to {self.withdrawals_file}")
        except Exception as e:
            logger.error(f"Error saving withdrawals: {str(e)}")

    def load_withdrawals(self):
        """
        Load withdrawals from disk
        
        Returns:
            Dict mapping nullifier hash to withdrawal info
        """
        if not self.withdrawals_file.exists():
            logger.debug(f"Withdrawals file {self.withdrawals_file} does not exist, returning empty dict")
            return {}
        
        try:
            with open(self.withdrawals_file, "r") as f:
                withdrawals = json.load(f)
            logger.debug(f"Loaded {len(withdrawals)} withdrawals from {self.withdrawals_file}")
            return withdrawals
        except Exception as e:
            logger.error(f"Error loading withdrawals: {str(e)}")
            return {} 