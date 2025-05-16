import * as anchor from "@coral-xyz/anchor";
import { Program } from "@coral-xyz/anchor";
import { PublicKey, Keypair, SystemProgram } from "@solana/web3.js";
import { TOKEN_PROGRAM_ID, Token } from "@solana/spl-token";
import fs from "fs";
import dotenv from "dotenv";

dotenv.config();

// Load the wallet keypair from file
const walletKeyData = JSON.parse(
  fs.readFileSync(process.env.WALLET_PATH || "~/.config/solana/id.json", "utf-8")
);
const walletKeypair = Keypair.fromSecretKey(new Uint8Array(walletKeyData));

// Anchor configuration
const provider = anchor.AnchorProvider.env();
anchor.setProvider(provider);

// Main deployment function
async function main() {
  try {
    console.log("Deploying Privax Protocol...");
    
    // Get the program from Anchor workspace
    const idl = JSON.parse(
      fs.readFileSync("target/idl/privax_protocol.json", "utf-8")
    );
    const programId = new PublicKey("Fg6PaFpoGXkYsidMpWTK6W2BeZ7FEfcYkg476zPFsLnS");
    const program = new anchor.Program(idl, programId, provider);
    
    // Create a new token for the protocol
    console.log("Creating token mint...");
    const tokenMint = await Token.createMint(
      provider.connection,
      walletKeypair,
      walletKeypair.publicKey,
      null, // No freeze authority
      9, // 9 decimals
      TOKEN_PROGRAM_ID
    );
    console.log(`Token mint created: ${tokenMint.publicKey.toString()}`);
    
    // Create a placeholder for the verifier program
    const verifierProgramId = Keypair.generate().publicKey;
    console.log(`Placeholder verifier program ID: ${verifierProgramId.toString()}`);
    
    // Find the program state PDA
    const [programStatePDA] = PublicKey.findProgramAddressSync(
      [Buffer.from("program_state")],
      program.programId
    );
    console.log(`Program state PDA: ${programStatePDA.toString()}`);
    
    // Initialize the protocol
    console.log("Initializing the Privax Protocol...");
    await program.methods
      .initialize(tokenMint.publicKey, verifierProgramId)
      .accounts({
        programState: programStatePDA,
        admin: walletKeypair.publicKey,
        systemProgram: SystemProgram.programId,
      })
      .signers([walletKeypair])
      .rpc();
    
    console.log("Privax Protocol successfully deployed and initialized!");
    console.log("Configuration summary:");
    console.log(`- Program ID: ${program.programId.toString()}`);
    console.log(`- Token Mint: ${tokenMint.publicKey.toString()}`);
    console.log(`- Program State: ${programStatePDA.toString()}`);
    console.log(`- Admin: ${walletKeypair.publicKey.toString()}`);
    
  } catch (error) {
    console.error("Deployment failed:", error);
    process.exit(1);
  }
}

// Run the main function
main().then(
  () => process.exit(0),
  (error) => {
    console.error(error);
    process.exit(1);
  }
); 