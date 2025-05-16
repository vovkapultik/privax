import os
import hashlib
from pydantic import BaseModel
from typing import Optional, Dict, Any

def poseidon_hash_placeholder(inputs):
    """Placeholder for a ZK-friendly hash function like Poseidon.
    Uses SHA256 for demonstration in Python. Inputs are converted to strings.
    In a real scenario, inputs would be field elements and a proper ZK-hash would be used.
    """
    hasher = hashlib.sha256()
    for item in inputs:
        hasher.update(str(item).encode('utf-8'))
    return hasher.hexdigest()

def generate_random_field_element_hex(byte_length=31):
    """Generates a random hex string representing a field element (approx)."""
    return os.urandom(byte_length).hex()

class Note:
    def __init__(self, amount, secret=None, nullifier_secret=None):
        self.amount = int(amount)
        self.secret = secret if secret is not None else generate_random_field_element_hex()
        self.nullifier_secret = nullifier_secret if nullifier_secret is not None else generate_random_field_element_hex()
        
        self.commitment = self._calculate_commitment()
        self.nullifier_hash = self._calculate_nullifier_hash()

    def _calculate_commitment(self):
        """Calculates the commitment for the note.
        commitment = H(amount, secret, nullifier_secret)
        """
        # In a real ZK system, these would be field elements.
        # Using a placeholder hash for Python demonstration.
        return poseidon_hash_placeholder([
            self.amount,
            self.secret,
            self.nullifier_secret
        ])

    def _calculate_nullifier_hash(self):
        """Calculates the nullifier hash for the note.
        nullifier_hash = H(nullifier_secret, domain_separator)
        A domain separator (e.g., 1) is used to distinguish nullifier hashes.
        """
        domain_separator_nullifier = 1 
        return poseidon_hash_placeholder([
            self.nullifier_secret,
            domain_separator_nullifier
        ])

    def to_dict(self) -> Dict[str, Any]:
        """Convert note to dictionary for API responses"""
        return {
            "amount": self.amount,
            "secret": self.secret,
            "nullifier_secret": self.nullifier_secret,
            "commitment": self.commitment,
            "nullifier_hash": self.nullifier_hash
        }

    def __repr__(self):
        return (
            f"Note(\n"
            f"  Amount: {self.amount}\n"
            f"  Secret: {self.secret}\n"
            f"  Nullifier Secret: {self.nullifier_secret}\n"
            f"  Commitment: {self.commitment}\n"
            f"  Nullifier Hash: {self.nullifier_hash}\n"
            f")"
        ) 