const { expect } = require("chai");
const { ethers } = require("hardhat");

describe("PrivaxProtocol", function () {
  let privacyContract;
  let mockToken;
  let mockVerifier;
  let owner;
  let user1;
  let user2;
  let relayer;

  // Sample proof data (mocked for testing)
  const mockProof = {
    a: [ethers.toBigInt("1"), ethers.toBigInt("2")],
    b: [
      [ethers.toBigInt("3"), ethers.toBigInt("4")],
      [ethers.toBigInt("5"), ethers.toBigInt("6")]
    ],
    c: [ethers.toBigInt("7"), ethers.toBigInt("8")]
  };

  beforeEach(async function () {
    [owner, user1, user2, relayer] = await ethers.getSigners();

    // Deploy mock ERC20 token
    const MockToken = await ethers.getContractFactory("MockERC20");
    mockToken = await MockToken.deploy("Privax Token", "PRIVAX");
    
    // Deploy mock verifier
    const MockVerifier = await ethers.getContractFactory("MockVerifier");
    mockVerifier = await MockVerifier.deploy();
    
    // Deploy the privacy contract
    const PrivacyContract = await ethers.getContractFactory("PrivaxProtocol");
    privacyContract = await PrivacyContract.deploy(
      await mockToken.getAddress(),
      await mockVerifier.getAddress()
    );
    
    // Mint some tokens to user1 for testing
    await mockToken.mint(user1.address, ethers.parseEther("1000"));
    
    // Approve the privacy contract to spend user1's tokens
    await mockToken.connect(user1).approve(
      await privacyContract.getAddress(),
      ethers.parseEther("1000")
    );
  });

  describe("Deployment", function () {
    it("Should set the right admin", async function () {
      expect(await privacyContract.admin()).to.equal(owner.address);
    });

    it("Should set the right token", async function () {
      expect(await privacyContract.token()).to.equal(await mockToken.getAddress());
    });

    it("Should set the right verifier", async function () {
      expect(await privacyContract.verifier()).to.equal(await mockVerifier.getAddress());
    });
  });

  describe("Admin functions", function () {
    it("Should add a relayer successfully", async function () {
      await privacyContract.addRelayer(relayer.address);
      expect(await privacyContract.isRelayer(relayer.address)).to.be.true;
    });

    it("Should remove a relayer successfully", async function () {
      await privacyContract.addRelayer(relayer.address);
      await privacyContract.removeRelayer(relayer.address);
      expect(await privacyContract.isRelayer(relayer.address)).to.be.false;
    });

    it("Should transfer ownership successfully", async function () {
      await privacyContract.transferOwnership(user1.address);
      expect(await privacyContract.admin()).to.equal(user1.address);
    });

    it("Should revert when non-admin calls admin functions", async function () {
      await expect(
        privacyContract.connect(user1).addRelayer(relayer.address)
      ).to.be.revertedWith("Privax: Caller is not the admin");
    });
  });

  describe("Deposit", function () {
    it("Should deposit tokens successfully", async function () {
      const depositAmount = ethers.parseEther("10");
      const commitment = ethers.randomBytes(32);
      
      await expect(privacyContract.connect(user1).deposit(depositAmount, commitment))
        .to.emit(privacyContract, "DepositOccurred")
        .withArgs(user1.address, await mockToken.getAddress(), depositAmount, commitment);
      
      // Check contract balance
      expect(await mockToken.balanceOf(await privacyContract.getAddress())).to.equal(depositAmount);
    });

    it("Should revert when deposit amount is zero", async function () {
      const commitment = ethers.randomBytes(32);
      await expect(
        privacyContract.connect(user1).deposit(0, commitment)
      ).to.be.revertedWith("Privax: Deposit amount must be greater than zero");
    });
  });

  // More tests would be needed for the withdrawal function, but those would require
  // mocking the verifier to return specific proof validation results
}); 