pragma circom 2.1.5;

// Import Poseidon hash function from circomlib
// Ensure circomlib is installed and accessible in your include path (e.g., node_modules)
include "circomlib/circuits/poseidon.circom";

// Template for the withdrawal circuit
// 'levels' is the depth of the Merkle tree
template Withdraw(levels) {

    // --- Private Inputs --- 
    // These are known only to the prover

    // Secret random value used in generating the commitment
    signal input secret;
    // Secret random value used for generating the commitment and the nullifierHash
    signal input nullifierSecret;
    
    // Merkle proof components for the commitment
    // pathElements: The sibling nodes along the path from the leaf (commitment) to the root
    signal input pathElements[levels];
    // pathIndices: Binary values (0 or 1) indicating the position (left/right) of the current hash at each level
    // 0 means current hash is on the left, 1 means current hash is on the right
    signal input pathIndices[levels];

    // --- Public Inputs --- 
    // These are known to both prover and verifier, and are part of the public statement being proven

    // The Merkle root of the tree of commitments
    signal input merkleRoot;
    // The nullifier hash, H(nullifierSecret, 1), to prevent double-spending
    signal input nullifierHash;
    // The recipient's address (as a field element)
    signal input recipient; 
    // The amount of tokens to be withdrawn
    signal input amount; 
    // An external nullifier, e.g., address of the contract or a domain-specific value, 
    // to prevent replay attacks across different contexts.
    signal input externalNullifier;

    // --- 1. Reconstruct the Commitment --- 
    // The commitment is calculated as H(amount, secret, nullifierSecret)
    // We use Poseidon hash with 3 inputs.
    component commitmentHasher = Poseidon(3);
    commitmentHasher.inputs[0] <== amount;
    commitmentHasher.inputs[1] <== secret;
    commitmentHasher.inputs[2] <== nullifierSecret;
    signal calculatedCommitment <== commitmentHasher.out;

    // --- 2. Verify Nullifier Hash --- 
    // The nullifierHash is calculated as H(nullifierSecret, domain_separator_for_nullifier)
    // We use a domain separator (e.g., 1) to differentiate it from other hashes.
    // We use Poseidon hash with 2 inputs.
    component nullifierHasher = Poseidon(2);
    nullifierHasher.inputs[0] <== nullifierSecret;
    nullifierHasher.inputs[1] <== 1; // Domain separator for nullifier (must match generation)
    signal calculatedNullifierHash <== nullifierHasher.out;

    // Constraint: The provided public nullifierHash must match the one calculated from private inputs.
    nullifierHash === calculatedNullifierHash;

    // --- 3. Verify Merkle Proof --- 
    // This section verifies that the 'calculatedCommitment' is a leaf in a Merkle tree
    // whose root is 'merkleRoot', using the provided 'pathElements' and 'pathIndices'.

    // Array to store intermediate hashes during Merkle root calculation
    signal currentHashes[levels + 1];
    // The first hash is the leaf itself (the calculated commitment)
    currentHashes[0] <== calculatedCommitment;

    // Iteratively compute hashes up the Merkle tree
    for (var i = 0; i < levels; i++) {
        // Ensure pathIndices[i] is binary (0 or 1)
        pathIndices[i] * (pathIndices[i] - 1) === 0;

        // Instantiate Poseidon hasher for this level (2 inputs)
        component merkleLevelHasher = Poseidon(2);
        
        // Based on pathIndices[i], determine if the current hash is the left or right child
        // If pathIndices[i] is 0, currentHashes[i] is left, pathElements[i] is right.
        // If pathIndices[i] is 1, pathElements[i] is left, currentHashes[i] is right.
        var leftInput = (1 - pathIndices[i]) * currentHashes[i] + pathIndices[i] * pathElements[i];
        var rightInput = pathIndices[i] * currentHashes[i] + (1 - pathIndices[i]) * pathElements[i];
        
        merkleLevelHasher.inputs[0] <== leftInput;
        merkleLevelHasher.inputs[1] <== rightInput;
        
        currentHashes[i+1] <== merkleLevelHasher.out;
    }

    // Constraint: The final computed hash must match the public merkleRoot.
    merkleRoot === currentHashes[levels];

    // --- 4. Public Input Usage (Implicit Constraints) --- 
    // The public inputs `recipient`, `amount`, and `externalNullifier` are part of the statement being proven.
    // `amount` is used in commitment calculation.
    // `recipient` defines the withdrawal destination.
    // `externalNullifier` scopes the proof (e.g., to a specific contract or action type).
    // While not explicitly constrained further in this simple circuit, their inclusion as public inputs
    // means the generated proof is only valid for these specific public values.
    // More complex circuits might include them in a final hash or other checks.
}

// Main component declaration with a Merkle tree of depth 20
// Public inputs are declared here - these are the values that will be known to both prover and verifier
component main {public [merkleRoot, nullifierHash, recipient, amount, externalNullifier]} = Withdraw(20); 