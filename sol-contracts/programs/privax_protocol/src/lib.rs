use anchor_lang::prelude::*;
use anchor_spl::token::{self, Mint, Token, TokenAccount, Transfer};

// Declare the program ID. Replace with your actual program ID when deploying.
declare_id!("Fg6PaFpoGXkYsidMpWTK6W2BeZ7FEfcYkg476zPFsLnS");

// --- Errors ---
#[error_code]
pub enum PrivaxError {
    #[msg("Amount must be greater than zero.")]
    AmountTooSmall,
    #[msg("Invalid public input count for ZK proof.")]
    InvalidPublicInputCount,
    #[msg("Recipient mismatch in proof inputs.")]
    RecipientMismatch,
    #[msg("Amount mismatch in proof inputs.")]
    AmountMismatch,
    #[msg("Invalid ZK proof (placeholder check).")]
    InvalidZkProof,
    #[msg("Relayer already whitelisted.")]
    RelayerAlreadyWhitelisted,
    #[msg("Relayer not whitelisted.")]
    RelayerNotWhitelisted,
    #[msg("Invalid relayer address.")]
    InvalidRelayerAddress,
    #[msg("New admin cannot be the zero address (system program).")]
    NewAdminIsZero,
    #[msg("Overflow during arithmetic operation.")]
    Overflow,
}

// --- Program State Account ---
#[account]
#[derive(Default)]
pub struct ProgramState {
    pub admin: Pubkey,          // The administrator of the contract
    pub token_mint: Pubkey,     // The SPL token mint this contract manages
    pub verifier_program_id: Pubkey, // Placeholder for a ZK verifier program ID
    pub bump: u8,
    // Whitelisted relayers - using a Vec for simplicity in showcase, consider BTreeMap for production
    pub whitelisted_relayers: Vec<Pubkey>,
}

impl ProgramState {
    // Calculate space for ProgramState account
    // Pubkey (admin) = 32
    // Pubkey (token_mint) = 32
    // Pubkey (verifier_program_id) = 32
    // u8 (bump) = 1
    // Vec<Pubkey> for whitelisted_relayers: 4 (for Vec prefix) + N * 32. Let's assume max 10 relayers for showcase.
    pub const MAX_RELAYERS: usize = 10;
    pub const SPACE: usize = 8 + 32 + 32 + 32 + 1 + (4 + Self::MAX_RELAYERS * 32);
}

// --- Events (emitted via `emit!`) ---
#[event]
pub struct AdminChanged {
    old_admin: Pubkey,
    new_admin: Pubkey,
}

#[event]
pub struct RelayerAdded {
    relayer_address: Pubkey,
}

#[event]
pub struct RelayerRemoved {
    relayer_address: Pubkey,
}

#[event]
pub struct DepositOccurred {
    user: Pubkey,
    token_address: Pubkey, // Mint address of the token
    amount: u64,
    commitment: [u8; 32], // bytes32 commitment
}

#[event]
pub struct WithdrawalOccurred {
    nullifier_hash: [u8; 32], // bytes32 nullifierHash
    recipient: Pubkey,
    token_address: Pubkey, // Mint address of the token
    amount: u64,
}

// --- Program Entry Point and Instructions ---
#[program]
pub mod privax_protocol {
    use super::*; // Import items from parent module

    pub const REQUIRED_PUBLIC_INPUTS_COUNT: usize = 5;

    pub fn initialize(
        ctx: Context<Initialize>,
        token_mint_address: Pubkey,
        verifier_program_id: Pubkey, // Placeholder
    ) -> Result<()> {
        let state = &mut ctx.accounts.program_state;
        state.admin = *ctx.accounts.admin.key;
        state.token_mint = token_mint_address;
        state.verifier_program_id = verifier_program_id; // Store for potential future use
        state.whitelisted_relayers = Vec::new();
        state.bump = *ctx.bumps.get("program_state").unwrap();

        emit!(AdminChanged {
            old_admin: Pubkey::default(), // System program as placeholder for "address(0)"
            new_admin: state.admin,
        });
        Ok(())
    }

    pub fn add_relayer(ctx: Context<ManageRelayers>, relayer_address: Pubkey) -> Result<()> {
        let state = &mut ctx.accounts.program_state;
        require!(relayer_address != Pubkey::default(), PrivaxError::InvalidRelayerAddress);
        require!(!state.whitelisted_relayers.contains(&relayer_address), PrivaxError::RelayerAlreadyWhitelisted);
        
        // Ensure we don't exceed max relayers if using a fixed-size Vec or check capacity
        if state.whitelisted_relayers.len() >= ProgramState::MAX_RELAYERS {
            // For showcase, we might just error out or handle it differently
            return err!(ProgramError::AccountDataTooSmall); // Or a custom error
        }
        state.whitelisted_relayers.push(relayer_address);

        emit!(RelayerAdded { relayer_address });
        Ok(())
    }

    pub fn remove_relayer(ctx: Context<ManageRelayers>, relayer_address: Pubkey) -> Result<()> {
        let state = &mut ctx.accounts.program_state;
        require!(state.whitelisted_relayers.contains(&relayer_address), PrivaxError::RelayerNotWhitelisted);
        state.whitelisted_relayers.retain(|&x| x != relayer_address);

        emit!(RelayerRemoved { relayer_address });
        Ok(())
    }

    pub fn transfer_ownership(ctx: Context<TransferOwnership>, new_admin: Pubkey) -> Result<()> {
        let state = &mut ctx.accounts.program_state;
        require!(new_admin != Pubkey::default(), PrivaxError::NewAdminIsZero);
        
        let old_admin = state.admin;
        state.admin = new_admin;

        emit!(AdminChanged { old_admin, new_admin });
        Ok(())
    }

    pub fn deposit(
        ctx: Context<DepositTokens>,
        amount: u64,
        commitment: [u8; 32],
    ) -> Result<()> {
        require!(amount > 0, PrivaxError::AmountTooSmall);

        // Transfer tokens from user to program's vault PDA
        let cpi_accounts = Transfer {
            from: ctx.accounts.user_token_account.to_account_info(),
            to: ctx.accounts.program_token_vault.to_account_info(),
            authority: ctx.accounts.user.to_account_info(),
        };
        let cpi_program = ctx.accounts.token_program.to_account_info();
        let cpi_ctx = CpiContext::new(cpi_program, cpi_accounts);
        token::transfer(cpi_ctx, amount)?;

        emit!(DepositOccurred {
            user: *ctx.accounts.user.key,
            token_address: ctx.accounts.program_state.token_mint,
            amount,
            commitment,
        });
        Ok(())
    }

    #[allow(unused_variables)] // For a_proof, b_proof, c_proof if verifier is placeholder
    pub fn withdraw(
        ctx: Context<WithdrawTokens>,
        a_proof: Vec<u8>, // Placeholder for actual proof structure (e.g., [u64; 2])
        b_proof: Vec<u8>, // Placeholder
        c_proof: Vec<u8>, // Placeholder
        public_inputs: Vec<u64>, // Assuming public inputs are u64 for simplicity
        recipient_address: Pubkey,
        amount_to_withdraw: u64,
    ) -> Result<()> {
        require!(amount_to_withdraw > 0, PrivaxError::AmountTooSmall);
        require!(public_inputs.len() == REQUIRED_PUBLIC_INPUTS_COUNT, PrivaxError::InvalidPublicInputCount);

        // Public inputs expected order (as u64 for this example):
        // public_inputs[0]: merkleRoot (u64 representation)
        // public_inputs[1]: nullifierHash (u64 representation of bytes32)
        // public_inputs[2]: recipient (u64 representation of Pubkey)
        // public_inputs[3]: amountToWithdraw (u64)
        // public_inputs[4]: externalNullifier (u64, e.g., program_id as u64)

        // Validate recipient and amount from public inputs
        // This requires careful conversion if Pubkey/amounts are not directly u64 in ZK circuit
        // For showcase, we assume they are compatible or a conversion function exists.
        // Example: Convert recipient_address to u64 for comparison (highly simplified)
        let recipient_as_u64_bytes = recipient_address.to_bytes();
        let mut recipient_u64_array = [0u8; 8];
        recipient_u64_array.copy_from_slice(&recipient_as_u64_bytes[0..8]); // Highly simplified, not robust
        let recipient_input_check = u64::from_le_bytes(recipient_u64_array);

        require!(recipient_input_check == public_inputs[2], PrivaxError::RecipientMismatch);
        require!(amount_to_withdraw == public_inputs[3], PrivaxError::AmountMismatch);

        // --- ZK Proof Verification Placeholder ---
        // In a real contract, you would make a CPI to a verifier program.
        // let cpi_accounts = VerifyProofAccounts { ... };
        // let cpi_program = ctx.accounts.verifier_program.to_account_info();
        // verify_zk_proof_cpi(CpiContext::new(cpi_program, cpi_accounts), proof_params)?;
        // For showcase, we simulate a valid proof. Replace with actual CPI.
        let is_valid_proof = true; // Placeholder
        require!(is_valid_proof, PrivaxError::InvalidZkProof);
        // --- End ZK Proof Verification Placeholder ---

        // Extract nullifierHash (assuming it's public_inputs[1] and needs conversion to [u8; 32])
        let nullifier_hash_u64 = public_inputs[1];
        let nullifier_hash_bytes: [u8; 32] = unsafe { std::mem::transmute(nullifier_hash_u64.to_le_bytes().try_into().unwrap_or_else(|_| [0u8;32])) }; // Highly unsafe, for demo only

        // Transfer tokens from program's vault to recipient
        let seeds = &[b"program_token_vault".as_ref(), ctx.accounts.program_state.to_account_info().key.as_ref(), &[ctx.accounts.program_state.bump]];
        let signer_seeds = &[&seeds[..]];

        let cpi_accounts = Transfer {
            from: ctx.accounts.program_token_vault.to_account_info(),
            to: ctx.accounts.recipient_token_account.to_account_info(),
            authority: ctx.accounts.program_token_vault_authority.to_account_info(), // The PDA is the authority
        };
        let cpi_program = ctx.accounts.token_program.to_account_info();
        token::transfer(CpiContext::new_with_signer(cpi_program, cpi_accounts, signer_seeds), amount_to_withdraw)?;

        emit!(WithdrawalOccurred {
            nullifier_hash: nullifier_hash_bytes,
            recipient: recipient_address,
            token_address: ctx.accounts.program_state.token_mint,
            amount: amount_to_withdraw,
        });
        Ok(())
    }
}

// --- Account Structs for Instructions ---
#[derive(Accounts)]
pub struct Initialize<'info> {
    #[account(init, payer = admin, space = ProgramState::SPACE, seeds = [b"program_state"], bump)]
    pub program_state: Account<'info, ProgramState>,
    #[account(mut)]
    pub admin: Signer<'info>,
    pub system_program: Program<'info, System>,
}

#[derive(Accounts)]
pub struct ManageRelayers<'info> {
    #[account(mut, has_one = admin, seeds = [b"program_state"], bump = program_state.bump)]
    pub program_state: Account<'info, ProgramState>,
    pub admin: Signer<'info>,
}

#[derive(Accounts)]
pub struct TransferOwnership<'info> {
    #[account(mut, has_one = admin, seeds = [b"program_state"], bump = program_state.bump)]
    pub program_state: Account<'info, ProgramState>,
    pub admin: Signer<'info>,
}

#[derive(Accounts)]
pub struct DepositTokens<'info> {
    #[account(seeds = [b"program_state"], bump = program_state.bump)]
    pub program_state: Account<'info, ProgramState>,
    #[account(mut)] // User who is depositing
    pub user: Signer<'info>,
    #[account(mut, constraint = user_token_account.mint == program_state.token_mint)]
    pub user_token_account: Account<'info, TokenAccount>,
    #[account(
        init_if_needed, // Initialize if it doesn't exist
        payer = user,
        token::mint = program_state.token_mint,
        token::authority = program_token_vault_authority, // PDA will be authority
        seeds = [b"program_token_vault", program_state.key().as_ref()], 
        bump
    )]
    pub program_token_vault: Account<'info, TokenAccount>,
    /// CHECK: This is the PDA authority for the program_token_vault, derived from program_state key.
    #[account(seeds = [b"program_token_vault", program_state.key().as_ref()], bump)]
    pub program_token_vault_authority: UncheckedAccount<'info>,
    pub token_program: Program<'info, Token>,
    pub system_program: Program<'info, System>,
    pub rent: Sysvar<'info, Rent>,
}

#[derive(Accounts)]
pub struct WithdrawTokens<'info> {
    #[account(seeds = [b"program_state"], bump = program_state.bump)]
    pub program_state: Account<'info, ProgramState>,
    #[account(mut)] // User initiating the withdrawal (signer of the transaction)
    pub user: Signer<'info>,
    #[account(mut, token::mint = program_state.token_mint, seeds = [b"program_token_vault", program_state.key().as_ref()], bump)] // program_token_vault.bump? No, use state bump for seed consistency
    pub program_token_vault: Account<'info, TokenAccount>,
    /// CHECK: This is the PDA authority for the program_token_vault
    #[account(seeds = [b"program_token_vault", program_state.key().as_ref()], bump)] // This bump should be the one used to create the vault authority PDA
    pub program_token_vault_authority: UncheckedAccount<'info>,
    #[account(mut, token::mint = program_state.token_mint)] // Recipient's token account
    pub recipient_token_account: Account<'info, TokenAccount>,
    // pub verifier_program: UncheckedAccount<'info>, // For CPI to a verifier program
    pub token_program: Program<'info, Token>,
} 