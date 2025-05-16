import * as anchor from "@coral-xyz/anchor";
import { Program } from "@coral-xyz/anchor";
import { Keypair, PublicKey, SystemProgram, LAMPORTS_PER_SOL } from "@solana/web3.js";
import { 
  TOKEN_PROGRAM_ID, 
  createMint, 
  createAssociatedTokenAccount,
  mintTo,
  getAssociatedTokenAddress
} from "@solana/spl-token";
import { assert } from "chai";

describe("privax_protocol", () => {
  // Configure the client to use the local cluster
  const provider = anchor.AnchorProvider.env();
  anchor.setProvider(provider);

  const program = anchor.workspace.PrivaxProtocol as Program;
  
  // Key participants
  const admin = Keypair.generate();
  const user = Keypair.generate();
  const recipient = Keypair.generate();
  
  // Mock data for testing
  let tokenMint: PublicKey;
  let userTokenAccount: PublicKey;
  let recipientTokenAccount: PublicKey;
  let programStatePDA: PublicKey;
  let vaultPDA: PublicKey;
  let vaultAuthority: PublicKey;
  
  // Constants
  const AMOUNT = 1_000_000_000; // 1 token with 9 decimals
  const MOCK_COMMITMENT = new Uint8Array(32).fill(1); // Dummy commitment
  
  // Mock proof data for testing
  const mockProof = {
    aProof: Buffer.from([1, 2, 3]),
    bProof: Buffer.from([4, 5, 6]),
    cProof: Buffer.from([7, 8, 9]),
    publicInputs: [1, 2, 3, AMOUNT, 5] // Matching the required format in contract
  };

  before(async () => {
    // Airdrop SOL to participants
    await provider.connection.requestAirdrop(admin.publicKey, 10 * LAMPORTS_PER_SOL);
    await provider.connection.requestAirdrop(user.publicKey, 10 * LAMPORTS_PER_SOL);
    await provider.connection.requestAirdrop(recipient.publicKey, 10 * LAMPORTS_PER_SOL);
    
    // Wait for confirmations
    await new Promise(resolve => setTimeout(resolve, 3000));
    
    // Create test token mint
    tokenMint = await createMint(
      provider.connection,
      admin,
      admin.publicKey,
      null,
      9 // 9 decimals
    );
    
    // Create token accounts
    userTokenAccount = await createAssociatedTokenAccount(
      provider.connection,
      user,
      tokenMint,
      user.publicKey
    );
    
    recipientTokenAccount = await createAssociatedTokenAccount(
      provider.connection,
      recipient,
      tokenMint,
      recipient.publicKey
    );
    
    // Mint tokens to user
    await mintTo(
      provider.connection,
      admin,
      tokenMint,
      userTokenAccount,
      admin.publicKey,
      AMOUNT * 10 // Mint 10 tokens
    );
    
    // Derive PDAs
    [programStatePDA] = PublicKey.findProgramAddressSync(
      [Buffer.from("program_state")],
      program.programId
    );
    
    [vaultPDA] = PublicKey.findProgramAddressSync(
      [Buffer.from("program_token_vault"), programStatePDA.toBuffer()],
      program.programId
    );
    
    [vaultAuthority] = PublicKey.findProgramAddressSync(
      [Buffer.from("program_token_vault"), programStatePDA.toBuffer()],
      program.programId
    );
  });

  it("Initializes the program", async () => {
    const mockVerifierProgramId = Keypair.generate().publicKey;
    
    await program.methods
      .initialize(tokenMint, mockVerifierProgramId)
      .accounts({
        programState: programStatePDA,
        admin: admin.publicKey,
        systemProgram: SystemProgram.programId,
      })
      .signers([admin])
      .rpc();
    
    // Verify state was properly initialized
    const programState = await program.account.programState.fetch(programStatePDA);
    assert.isTrue(programState.admin.equals(admin.publicKey));
    assert.isTrue(programState.tokenMint.equals(tokenMint));
    assert.isTrue(programState.verifierProgramId.equals(mockVerifierProgramId));
    assert.equal(programState.whitelistedRelayers.length, 0);
  });

  it("Adds and removes a relayer", async () => {
    const relayer = Keypair.generate().publicKey;
    
    // Add relayer
    await program.methods
      .addRelayer(relayer)
      .accounts({
        programState: programStatePDA,
        admin: admin.publicKey,
      })
      .signers([admin])
      .rpc();
    
    let programState = await program.account.programState.fetch(programStatePDA);
    assert.equal(programState.whitelistedRelayers.length, 1);
    assert.isTrue(programState.whitelistedRelayers[0].equals(relayer));
    
    // Remove relayer
    await program.methods
      .removeRelayer(relayer)
      .accounts({
        programState: programStatePDA,
        admin: admin.publicKey,
      })
      .signers([admin])
      .rpc();
    
    programState = await program.account.programState.fetch(programStatePDA);
    assert.equal(programState.whitelistedRelayers.length, 0);
  });

  it("Deposits tokens", async () => {
    await program.methods
      .deposit(new anchor.BN(AMOUNT), Array.from(MOCK_COMMITMENT))
      .accounts({
        programState: programStatePDA,
        user: user.publicKey,
        userTokenAccount: userTokenAccount,
        programTokenVault: vaultPDA,
        programTokenVaultAuthority: vaultAuthority,
        tokenProgram: TOKEN_PROGRAM_ID,
        systemProgram: SystemProgram.programId,
        rent: anchor.web3.SYSVAR_RENT_PUBKEY,
      })
      .signers([user])
      .rpc();

    // Verify tokens were transferred to vault
    const vaultBalance = await provider.connection.getTokenAccountBalance(vaultPDA);
    assert.equal(vaultBalance.value.uiAmount, AMOUNT / 1_000_000_000); // Convert to UI amount
  });

  // Note: In a real test, you would need to generate a valid ZK proof
  it("Withdraws tokens", async () => {
    await program.methods
      .withdraw(
        Array.from(mockProof.aProof),
        Array.from(mockProof.bProof),
        Array.from(mockProof.cProof),
        mockProof.publicInputs,
        recipient.publicKey,
        new anchor.BN(AMOUNT)
      )
      .accounts({
        programState: programStatePDA,
        user: user.publicKey,
        programTokenVault: vaultPDA,
        programTokenVaultAuthority: vaultAuthority,
        recipientTokenAccount: recipientTokenAccount,
        tokenProgram: TOKEN_PROGRAM_ID,
      })
      .signers([user])
      .rpc();

    // Verify tokens were transferred to recipient
    const recipientBalance = await provider.connection.getTokenAccountBalance(recipientTokenAccount);
    assert.equal(recipientBalance.value.uiAmount, AMOUNT / 1_000_000_000); // Convert to UI amount
  });

  it("Transfers ownership", async () => {
    const newAdmin = Keypair.generate().publicKey;
    
    await program.methods
      .transferOwnership(newAdmin)
      .accounts({
        programState: programStatePDA,
        admin: admin.publicKey,
      })
      .signers([admin])
      .rpc();
    
    const programState = await program.account.programState.fetch(programStatePDA);
    assert.isTrue(programState.admin.equals(newAdmin));
  });
}); 