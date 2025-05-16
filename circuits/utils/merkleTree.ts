import { buildPoseidon } from 'circomlibjs';
import crypto from 'crypto';

let poseidon: any;

// Initialize Poseidon hash function
async function initializePoseidon() {
  if (!poseidon) {
    poseidon = await buildPoseidon();
  }
  return poseidon;
}

// Convert a number to a field element (bigint)
function toField(num: string | number | bigint): bigint {
  if (typeof num === 'string') {
    return BigInt(num);
  }
  return BigInt(num);
}

// Poseidon hash of arbitrary inputs
async function poseidonHash(inputs: (string | number | bigint)[]): Promise<string> {
  const poseidon = await initializePoseidon();
  const hash = poseidon(inputs.map(x => toField(x)));
  return poseidon.F.toString(hash);
}

// Generate a random field element
function randomField(): string {
  return '0x' + crypto.randomBytes(31).toString('hex');
}

// MerkleTree implementation for commitments
class MerkleTree {
  levels: number;
  capacity: number;
  leaves: bigint[];
  zeros: Promise<bigint[]>;
  filled: number;

  constructor(levels = 20) {
    this.levels = levels;
    this.capacity = 2 ** levels;
    this.leaves = new Array(this.capacity).fill(BigInt(0));
    this.zeros = this._calculateZeros();
    this.filled = 0;
  }

  // Generate zero values for empty leaves
  async _calculateZeros(): Promise<bigint[]> {
    const zeros: bigint[] = new Array(this.levels + 1);
    zeros[0] = BigInt(0);
    
    for (let i = 1; i <= this.levels; i++) {
      zeros[i] = BigInt(await poseidonHash([zeros[i-1].toString(), zeros[i-1].toString()]));
    }
    
    return zeros;
  }

  // Insert a leaf (commitment) into the tree
  async insert(commitment: string | bigint): Promise<number> {
    if (this.filled >= this.capacity) {
      throw new Error('Tree is full');
    }
    
    let pos = this.filled;
    this.leaves[pos] = BigInt(commitment);
    this.filled++;
    
    return pos;
  }

  // Generate a Merkle proof for a leaf at a specific index
  async generateProof(index: number): Promise<{ pathElements: string[], pathIndices: number[] }> {
    if (index >= this.filled) {
      throw new Error('Leaf does not exist');
    }
    
    const pathElements: string[] = [];
    const pathIndices: number[] = [];
    
    let currentIndex = index;
    const zeros = await this.zeros;
    
    for (let i = 0; i < this.levels; i++) {
      const isRight = currentIndex % 2;
      const siblingIndex = isRight ? currentIndex - 1 : currentIndex + 1;
      
      pathIndices.push(isRight ? 0 : 1);
      
      const sibling = siblingIndex < this.filled 
        ? this.leaves[siblingIndex] 
        : zeros[i];
      
      pathElements.push(sibling.toString());
      
      currentIndex = Math.floor(currentIndex / 2);
    }
    
    return { pathElements, pathIndices };
  }

  // Calculate the current root of the tree
  async getRoot(): Promise<string> {
    if (this.filled === 0) {
      const zeros = await this.zeros;
      return zeros[this.levels].toString();
    }
    
    const layerSize = this.capacity;
    const hashes = [...this.leaves];
    const zeros = await this.zeros;
    
    for (let level = 0; level < this.levels; level++) {
      const levelSize = layerSize / (2 ** level);
      const nextLevelSize = levelSize / 2;
      
      for (let i = 0; i < nextLevelSize; i++) {
        const left = i * 2 < this.filled 
          ? hashes[i * 2] 
          : zeros[level];
        
        const right = i * 2 + 1 < this.filled 
          ? hashes[i * 2 + 1] 
          : zeros[level];
        
        hashes[i] = BigInt(await poseidonHash([left.toString(), right.toString()]));
      }
    }
    
    return hashes[0].toString();
  }
}

// Generate commitment from amount, secret, and nullifierSecret
async function generateCommitment(
  amount: string | number | bigint, 
  secret: string | number | bigint, 
  nullifierSecret: string | number | bigint
): Promise<string> {
  return await poseidonHash([amount, secret, nullifierSecret]);
}

// Generate nullifier hash from nullifierSecret
async function generateNullifierHash(
  nullifierSecret: string | number | bigint
): Promise<string> {
  return await poseidonHash([nullifierSecret, '1']);
}

export {
  MerkleTree,
  generateCommitment,
  generateNullifierHash,
  poseidonHash,
  randomField,
  initializePoseidon
}; 