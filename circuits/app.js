const fs = require('fs');
const path = require('path');
const { promisify } = require('util');
const readFile = promisify(fs.readFile);
const writeFile = promisify(fs.writeFile);
const snarkjs = require('snarkjs');

const { 
  MerkleTree, 
  generateCommitment, 
  generateNullifierHash, 
  randomField 
} = require('./utils/merkleTree');

// In-memory database of deposits
const deposits = {};
// In-memory set of spent nullifiers
const spentNullifiers = new Set();
// Merkle tree for commitments
let merkleTree;

async function initialize() {
  console.log('Initializing ZK Deposit/Withdrawal system...');
  
  // Initialize the Merkle tree with depth 20
  merkleTree = new MerkleTree(20);
  await merkleTree._calculateZeros();
  
  console.log('System initialized successfully');
  console.log('Merkle root:', await merkleTree.getRoot());
}

// Deposit function - creates a commitment and adds it to the Merkle tree
async function deposit(amount, userAddress) {
  // Generate random secrets
  const secret = randomField();
  const nullifierSecret = randomField();
  
  // Generate the commitment
  const commitment = await generateCommitment(amount, secret, nullifierSecret);
  
  // Insert commitment into the Merkle tree
  const index = await merkleTree.insert(commitment);
  
  // Calculate nullifier hash
  const nullifierHash = await generateNullifierHash(nullifierSecret);
  
  // Store deposit information
  deposits[commitment] = {
    index,
    amount,
    secret,
    nullifierSecret,
    nullifierHash,
    recipient: userAddress,
    timestamp: Date.now()
  };
  
  console.log(`\nDeposit successful!`);
  console.log(`Commitment: ${commitment}`);
  console.log(`Index in tree: ${index}`);
  console.log(`Amount: ${amount}`);
  console.log(`Recipient: ${userAddress}`);
  console.log(`Nullifier hash: ${nullifierHash}`);
  console.log(`Secret: ${secret} (keep this private)`);
  console.log(`Nullifier secret: ${nullifierSecret} (keep this private)`);
  
  // Return data needed for withdrawal
  return {
    commitment,
    nullifierHash,
    secret,
    nullifierSecret,
    index
  };
}

// Generate a proof for withdrawal
async function generateWithdrawalProof(
  amount, 
  secret, 
  nullifierSecret, 
  recipient, 
  externalNullifier = '1', 
  index
) {
  // Generate the commitment
  const commitment = await generateCommitment(amount, secret, nullifierSecret);
  const deposit = deposits[commitment];
  
  if (!deposit) {
    throw new Error('Deposit not found');
  }
  
  // Generate the nullifier hash
  const nullifierHash = await generateNullifierHash(nullifierSecret);
  
  // Check if nullifier has been spent
  if (spentNullifiers.has(nullifierHash)) {
    throw new Error('Deposit already withdrawn');
  }
  
  // Generate Merkle proof
  const { pathElements, pathIndices } = await merkleTree.generateProof(index);
  
  // Get current Merkle root
  const merkleRoot = await merkleTree.getRoot();
  
  // Prepare inputs for the circuit
  const circuitInputs = {
    secret: secret,
    nullifierSecret: nullifierSecret,
    pathElements: pathElements,
    pathIndices: pathIndices,
    merkleRoot: merkleRoot,
    nullifierHash: nullifierHash,
    recipient: recipient,
    amount: amount,
    externalNullifier: externalNullifier
  };
  
  // Save inputs to file
  await writeFile('input.json', JSON.stringify(circuitInputs, null, 2));
  
  console.log('\nGenerating proof...');
  console.log('Input saved to input.json');
  
  // For demo purposes, we'll explain how to generate the proof
  console.log('\nTo generate the witness and proof, run:');
  console.log('1. npm run compile');
  console.log('2. npm run setup');
  console.log('3. npm run generate-witness');
  console.log('4. npm run generate-proof');
  console.log('5. npm run verify');
  
  return circuitInputs;
}

// Withdraw function - processes the withdrawal using a valid proof
async function withdraw(nullifierHash, proof, publicSignals) {
  // Check if nullifier has been spent
  if (spentNullifiers.has(nullifierHash)) {
    throw new Error('Deposit already withdrawn');
  }
  
  // Verify the proof
  const verificationKey = JSON.parse(
    await readFile('verification_key.json', 'utf8')
  );
  
  // Use snarkjs to verify the proof
  const isValid = await snarkjs.groth16.verify(
    verificationKey,
    publicSignals,
    proof
  );
  
  if (!isValid) {
    throw new Error('Invalid proof');
  }
  
  // Mark nullifier as spent
  spentNullifiers.add(nullifierHash);
  
  // Extract public inputs
  const amount = publicSignals[3];
  const recipient = publicSignals[2];
  
  console.log(`\nWithdrawal successful!`);
  console.log(`Amount: ${amount}`);
  console.log(`Recipient: ${recipient}`);
  console.log(`Nullifier hash: ${nullifierHash} (now spent)`);
  
  return { amount, recipient };
}

// Demo function to simulate the entire flow
async function runDemo() {
  await initialize();
  
  console.log('\n---- DEPOSIT FLOW ----');
  const amount = '1000000000000000000'; // 1 ETH in Wei
  const userAddress = '123456789'; // User address
  
  const depositData = await deposit(amount, userAddress);
  
  console.log('\n---- WITHDRAWAL PREPARATION ----');
  // In a real application, the user would keep these values secret and use them to withdraw
  const { secret, nullifierSecret, index } = depositData;
  
  const withdrawInputs = await generateWithdrawalProof(
    amount,
    secret,
    nullifierSecret,
    userAddress,
    '1', // External nullifier
    index
  );
  
  console.log('\n---- WITHDRAWAL VERIFICATION (simulated) ----');
  console.log('In a real application, the proof would be verified on-chain');
  console.log('The nullifier would be recorded on-chain to prevent double-spending');
  
  // For demonstration, we'll explain the process rather than executing it
  console.log('\nAfter generating a valid proof, you would submit:');
  console.log('1. The proof');
  console.log('2. The public inputs (merkleRoot, nullifierHash, recipient, amount, externalNullifier)');
  console.log('3. The smart contract would verify the proof and transfer the funds');
}

// Run the demo if this script is executed directly
if (require.main === module) {
  runDemo().catch(console.error);
}

module.exports = {
  initialize,
  deposit,
  generateWithdrawalProof,
  withdraw,
  runDemo
}; 