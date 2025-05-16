const { ethers } = require("hardhat");

async function main() {
  console.log("Deploying Privax Protocol...");
  
  // Replace these addresses with actual deployed contract addresses for production
  // For demo or testnet, you can deploy a mock ERC20 token and verifier first
  let tokenAddress, verifierAddress;
  
  // For local testing, deploy mock contracts
  if (network.name === "localhost" || network.name === "hardhat") {
    // Deploy mock token
    const MockToken = await ethers.getContractFactory("MockERC20");
    const mockToken = await MockToken.deploy("Privax Token", "PRIVAX");
    await mockToken.waitForDeployment();
    tokenAddress = await mockToken.getAddress();
    console.log(`Privax Token deployed to: ${tokenAddress}`);
    
    // Deploy mock verifier
    const MockVerifier = await ethers.getContractFactory("MockVerifier");
    const mockVerifier = await MockVerifier.deploy();
    await mockVerifier.waitForDeployment();
    verifierAddress = await mockVerifier.getAddress();
    console.log(`Privacy Verifier deployed to: ${verifierAddress}`);
  } else {
    // For testnet/mainnet, use actual addresses
    // These should be replaced with actual deployed contract addresses
    tokenAddress = process.env.TOKEN_ADDRESS;
    verifierAddress = process.env.VERIFIER_ADDRESS;
    
    if (!tokenAddress || !verifierAddress) {
      throw new Error("TOKEN_ADDRESS and VERIFIER_ADDRESS environment variables must be set for non-local deployments");
    }
  }
  
  // Deploy PrivaxProtocol
  const PrivacyContract = await ethers.getContractFactory("PrivaxProtocol");
  const privacyContract = await PrivacyContract.deploy(tokenAddress, verifierAddress);
  await privacyContract.waitForDeployment();
  
  const privacyContractAddress = await privacyContract.getAddress();
  console.log(`PrivaxProtocol deployed to: ${privacyContractAddress}`);
  
  // For easier verification on Etherscan
  console.log("Contract deployment completed. For verification on Etherscan, run:");
  console.log(`npx hardhat verify --network ${network.name} ${privacyContractAddress} ${tokenAddress} ${verifierAddress}`);
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error(error);
    process.exit(1);
  }); 