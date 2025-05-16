const fs = require('fs');
const snarkjs = require('snarkjs');
const util = require('util');
const readFile = util.promisify(fs.readFile);
const writeFile = util.promisify(fs.writeFile);

async function generateWitness(wasmFile, inputFile, witnessFile) {
  try {
    // Read input JSON file
    const inputData = JSON.parse(await readFile(inputFile, 'utf8'));
    
    // Generate the witness
    const { witness } = await snarkjs.wtns.calculate(
      inputData, 
      wasmFile
    );
    
    // Write witness to binary file
    await snarkjs.wtns.export(witness, witnessFile);
    
    console.log(`Witness generated successfully at ${witnessFile}`);
    return true;
  } catch (err) {
    console.error('Error generating witness:', err);
    return false;
  }
}

// If this script is executed directly, run with command line arguments
if (require.main === module) {
  if (process.argv.length !== 5) {
    console.log('Usage: node generate_witness.js <circuit.wasm> <input.json> <witness.wtns>');
    process.exit(1);
  }
  
  const wasmFile = process.argv[2];
  const inputFile = process.argv[3];
  const witnessFile = process.argv[4];
  
  generateWitness(wasmFile, inputFile, witnessFile)
    .then(success => {
      process.exit(success ? 0 : 1);
    })
    .catch(err => {
      console.error(err);
      process.exit(1);
    });
}

module.exports = generateWitness; 