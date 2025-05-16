const { buildPoseidon } = require('circomlibjs');
const crypto = require('crypto');

let poseidon;

// Initialize Poseidon hash function
async function initializePoseidon() {
  if (!poseidon) {
    poseidon = await buildPoseidon();
  }
  return poseidon;
}

// Convert a number to a field element (bigint)
function toField(num) {
  if (typeof num === 'string') {
    return BigInt(num);
  }
  return BigInt(num);
}

// Poseidon hash of arbitrary inputs
async function poseidonHash(inputs) {
  const poseidon = await initializePoseidon();
  const hash = poseidon(inputs.map(x => toField(x)));
  return poseidon.F.toString(hash);
}

// Generate a random field element
function randomField() {
  return '0x' + crypto.randomBytes(31).toString('hex');
}

// MerkleTree implementation for commitments
class MerkleTree {
  constructor(levels = 20) {
    this.levels = levels;
    this.capacity = 2 ** levels;
    this.leaves = new Array(this.capacity).fill(0n);
    this.zeros = this._calculateZeros();
    this.filled = 0;
  }

  // Generate zero values for empty leaves
  async _calculateZeros() {
    const zeros = new Array(this.levels + 1);
    zeros[0] = 0n;
    
    for (let i = 1; i <= this.levels; i++) {
      zeros[i] = BigInt(await poseidonHash([zeros[i-1], zeros[i-1]]));
    }
    
    return zeros;
  }

  // Insert a leaf (commitment) into the tree
  async insert(commitment) {
    if (this.filled >= this.capacity) {
      throw new Error('Tree is full');
    }
    
    let pos = this.filled;
    this.leaves[pos] = BigInt(commitment);
    this.filled++;
    
    return pos;
  }

  // Generate a Merkle proof for a leaf at a specific index
  async generateProof(index) {
    if (index >= this.filled) {
      throw new Error('Leaf does not exist');
    }
    
    const pathElements = [];
    const pathIndices = [];
    
    let currentIndex = index;
    
    for (let i = 0; i < this.levels; i++) {
      const isRight = currentIndex % 2;
      const siblingIndex = isRight ? currentIndex - 1 : currentIndex + 1;
      
      pathIndices.push(isRight ? 0 : 1);
      
      const sibling = siblingIndex < this.filled 
        ? this.leaves[siblingIndex] 
        : this.zeros[i];
      
      pathElements.push(sibling.toString());
      
      currentIndex = Math.floor(currentIndex / 2);
    }
    
    return { pathElements, pathIndices };
  }

  // Calculate the current root of the tree
  async getRoot() {
    if (this.filled === 0) {
      return this.zeros[this.levels];
    }
    
    const layerSize = this.capacity;
    const hashes = [...this.leaves];
    
    for (let level = 0; level < this.levels; level++) {
      const levelSize = layerSize / (2 ** level);
      const nextLevelSize = levelSize / 2;
      
      for (let i = 0; i < nextLevelSize; i++) {
        const left = i * 2 < this.filled 
          ? hashes[i * 2] 
          : this.zeros[level];
        
        const right = i * 2 + 1 < this.filled 
          ? hashes[i * 2 + 1] 
          : this.zeros[level];
        
        hashes[i] = BigInt(await poseidonHash([left.toString(), right.toString()]));
      }
    }
    
    return hashes[0].toString();
  }
}

// Generate commitment from amount, secret, and nullifierSecret
async function generateCommitment(amount, secret, nullifierSecret) {
  return await poseidonHash([amount, secret, nullifierSecret]);
}

// Generate nullifier hash from nullifierSecret
async function generateNullifierHash(nullifierSecret) {
  return await poseidonHash([nullifierSecret, '1']);
}

module.exports = {
  MerkleTree,
  generateCommitment,
  generateNullifierHash,
  poseidonHash,
  randomField,
  initializePoseidon
}; 