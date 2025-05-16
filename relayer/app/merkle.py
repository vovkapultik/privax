#!/usr/bin/env python3
import hashlib
import logging

logger = logging.getLogger(__name__)

# --- Hash Function (SHA256 for Python simplicity) ---
def hash_func(input_string):
    """Computes SHA256 hash of a string and returns hex digest."""
    return hashlib.sha256(input_string.encode("utf-8")).hexdigest()

def hash_pair(left_hex, right_hex):
    """Hashes a pair of hex strings. Order matters.
    Concatenates them before hashing.
    """
    # Ensure consistent ordering or a separator if order doesn't inherently matter
    # For Merkle trees, order of concatenation is usually fixed (e.g., left + right)
    return hash_func(left_hex + right_hex)

# Default zero commitment - used as the first leaf of the tree
ZERO_COMMITMENT = hash_func("zero_commitment")

class MerkleTree:
    def __init__(self, initialize_with_zero=True):
        """
        Initialize a new Merkle tree
        
        Args:
            initialize_with_zero: If True, initializes the tree with a zero commitment
        """
        self.leaves = []  # Store the actual leaf values (commitments)
        self.tree_levels = [] # Stores all levels of the tree, tree_levels[0] are leaves (hashed), tree_levels[-1] is the root
        self.merkle_root = None
        
        # Initialize with a zero commitment if requested
        if initialize_with_zero:
            self.add_leaf(ZERO_COMMITMENT)
            logger.info(f"Initialized Merkle tree with zero commitment: {ZERO_COMMITMENT[:10]}...")

    def _calculate_next_level(self, current_level_nodes):
        """Calculates the next level of the Merkle tree from the current level."""
        next_level = []
        num_nodes = len(current_level_nodes)
        for i in range(0, num_nodes, 2):
            left_child = current_level_nodes[i]
            if i + 1 < num_nodes:
                right_child = current_level_nodes[i+1]
            else:
                # Handle odd number of nodes by duplicating the last one
                right_child = left_child 
            parent = hash_pair(left_child, right_child)
            next_level.append(parent)
        return next_level

    def add_leaf(self, leaf_value_hex):
        """Adds a new leaf (commitment) to the tree and rebuilds it."""
        if not isinstance(leaf_value_hex, str):
            raise ValueError("Leaf value must be a hex string.")
        
        self.leaves.append(leaf_value_hex)
        
        # Rebuild the tree
        if not self.leaves:
            self.tree_levels = []
            self.merkle_root = None
            return

        # For this simple Merkle tree, we'll hash the leaf values themselves if they aren't already hashes.
        # Assuming leaf_value_hex is the commitment itself, which is already a hash.
        current_level_nodes = list(self.leaves) 
        self.tree_levels = [current_level_nodes]

        while len(current_level_nodes) > 1:
            current_level_nodes = self._calculate_next_level(current_level_nodes)
            self.tree_levels.append(current_level_nodes)
        
        if current_level_nodes:
            self.merkle_root = current_level_nodes[0]
        else:
            self.merkle_root = None # Should not happen if leaves is not empty

    def get_merkle_root(self):
        """Returns the current Merkle root of the tree."""
        return self.merkle_root

    def get_merkle_path(self, leaf_value_hex):
        """Returns the Merkle path (siblings) and path indices for a given leaf value."""
        if leaf_value_hex not in self.leaves:
            raise ValueError("Leaf value not found in the tree.")

        leaf_index = self.leaves.index(leaf_value_hex)
        
        path_elements = []
        path_indices = [] # 0 for left, 1 for right (relative to the path element)

        current_index_in_level = leaf_index
        
        # Iterate from the leaf level up to the level just below the root
        for i in range(len(self.tree_levels) - 1):
            current_level_nodes = self.tree_levels[i]
            level_node_count = len(current_level_nodes)
            
            is_right_node = current_index_in_level % 2 != 0
            
            if is_right_node:
                # Current node is a right child, sibling is to the left
                sibling_index = current_index_in_level - 1
                path_indices.append(1) # The leaf/current_hash is on the right of its sibling
            else:
                # Current node is a left child, sibling is to the right
                sibling_index = current_index_in_level + 1
                # If the sibling index is out of bounds (odd number of nodes, last one duplicated for hashing)
                # the sibling is the node itself (as it was duplicated for hashing with itself)
                if sibling_index >= level_node_count:
                    sibling_index = current_index_in_level # its own hash was used as sibling
                path_indices.append(0) # The leaf/current_hash is on the left of its sibling
            
            path_elements.append(current_level_nodes[sibling_index])
            current_index_in_level //= 2 # Move to the parent's index in the next level
            
        return {
            "leaf_index": leaf_index,
            "path_elements": path_elements, # These are the siblings
            "path_indices": path_indices    # These indicate if the current path node was left (0) or right (1)
        } 