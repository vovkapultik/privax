import { expect } from "chai";
import path from "path";
import { wasm as wasm_tester } from "circom_tester";
import { MerkleTree, generateCommitment, generateNullifierHash, randomField } from "../../utils/merkleTree";

describe("Withdraw Circuit", function() {
  this.timeout(100000); // Increase timeout for circuit compilation

  let circuit: any;
  let merkleTree: MerkleTree;

  // Our test deposit data
  const amount = "1000000000000000000"; // 1 ETH in Wei
  const secret = randomField();
  const nullifierSecret = randomField();
  const recipient = "123456789";
  const externalNullifier = "1";
  
  // To store calculated values
  let commitment: string;
  let nullifierHash: string;
  let index: number;
  let merkleRoot: string;
  let proof: any;

  before(async () => {
    // Load the circuit
    circuit = await wasm_tester(path.join(__dirname, "../../circuits/circuit.circom"));
    
    // Initialize Merkle tree
    merkleTree = new MerkleTree(20);
    await merkleTree._calculateZeros();
    
    // Generate commitment and add to tree
    commitment = await generateCommitment(amount, secret, nullifierSecret);
    index = await merkleTree.insert(commitment);
    
    // Generate nullifier hash
    nullifierHash = await generateNullifierHash(nullifierSecret);
    
    // Get Merkle root
    merkleRoot = await merkleTree.getRoot();
    
    // Generate Merkle proof
    proof = await merkleTree.generateProof(index);
  });

  it("should generate a valid witness for correct inputs", async () => {
    const input = {
      // Private inputs
      secret: secret,
      nullifierSecret: nullifierSecret,
      pathElements: proof.pathElements,
      pathIndices: proof.pathIndices,
      
      // Public inputs
      merkleRoot: merkleRoot,
      nullifierHash: nullifierHash,
      recipient: recipient,
      amount: amount,
      externalNullifier: externalNullifier
    };
    
    const witness = await circuit.calculateWitness(input);
    await circuit.checkConstraints(witness);
  });

  it("should fail with invalid merkle proof", async () => {
    // Tamper with the path elements to create invalid proof
    const invalidProof = { ...proof };
    if (invalidProof.pathElements.length > 0) {
      invalidProof.pathElements[0] = randomField();
    }
    
    const input = {
      secret: secret,
      nullifierSecret: nullifierSecret,
      pathElements: invalidProof.pathElements,
      pathIndices: proof.pathIndices,
      merkleRoot: merkleRoot,
      nullifierHash: nullifierHash,
      recipient: recipient,
      amount: amount,
      externalNullifier: externalNullifier
    };
    
    try {
      const witness = await circuit.calculateWitness(input);
      await circuit.checkConstraints(witness);
      expect.fail("Circuit should have rejected invalid merkle proof");
    } catch (err: any) {
      // Expected error
      expect(err.toString()).to.include("Error: Assert Failed");
    }
  });
}); 