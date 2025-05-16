import logging
import os
import asyncio
from web3 import Web3
from web3.exceptions import BlockNotFound

logger = logging.getLogger(__name__)

# ABI for the privacy contract events
CONTRACT_ABI = [
    {
        "anonymous": False,
        "inputs": [
            {"indexed": True, "name": "user", "type": "address"},
            {"indexed": True, "name": "token", "type": "address"},
            {"indexed": False, "name": "amount", "type": "uint256"},
            {"indexed": False, "name": "commitment", "type": "bytes32"}
        ],
        "name": "DepositOccurred",
        "type": "event"
    },
    {
        "anonymous": False,
        "inputs": [
            {"indexed": True, "name": "nullifierHash", "type": "bytes32"},
            {"indexed": True, "name": "recipient", "type": "address"},
            {"indexed": True, "name": "token", "type": "address"},
            {"indexed": False, "name": "amount", "type": "uint256"}
        ],
        "name": "WithdrawalOccurred",
        "type": "event"
    }
]

class EthereumListener:
    def __init__(self, relayer, rpc_url=None, contract_address=None):
        """
        Initialize Ethereum event listener
        
        Args:
            relayer: The relayer instance
            rpc_url: The Ethereum RPC URL
            contract_address: The privacy contract address
        """
        self.relayer = relayer
        self.rpc_url = rpc_url or os.getenv("ETH_RPC_URL")
        self.contract_address = contract_address or os.getenv("ETH_CONTRACT_ADDRESS")
        
        if not self.rpc_url:
            raise ValueError("Ethereum RPC URL is required")
        if not self.contract_address:
            raise ValueError("Contract address is required")
            
        self.w3 = Web3(Web3.HTTPProvider(self.rpc_url))
        self.contract = self.w3.eth.contract(
            address=Web3.to_checksum_address(self.contract_address),
            abi=CONTRACT_ABI
        )
        
        self.last_processed_block = None
        self.running = False
        
    async def start(self):
        """Start listening for events"""
        if self.running:
            logger.warning("Ethereum listener is already running")
            return
            
        self.running = True
        logger.info(f"Starting Ethereum event listener for contract {self.contract_address}")
        
        # Get the latest block number as a starting point
        self.last_processed_block = self.w3.eth.block_number
        logger.info(f"Starting from block {self.last_processed_block}")
        
        while self.running:
            try:
                await self.poll_events()
                await asyncio.sleep(15)  # Poll every 15 seconds
            except Exception as e:
                logger.error(f"Error polling Ethereum events: {str(e)}")
                await asyncio.sleep(30)  # Longer delay on error
    
    async def stop(self):
        """Stop listening for events"""
        logger.info("Stopping Ethereum event listener")
        self.running = False
    
    async def poll_events(self):
        """Poll for new events"""
        current_block = self.w3.eth.block_number
        
        if current_block <= self.last_processed_block:
            logger.debug(f"No new blocks to process (current: {current_block}, last: {self.last_processed_block})")
            return
        
        logger.info(f"Processing blocks {self.last_processed_block + 1} to {current_block}")
        
        # Get deposit events
        deposit_filter = self.contract.events.DepositOccurred.create_filter(
            fromBlock=self.last_processed_block + 1,
            toBlock=current_block
        )
        
        # Get withdrawal events
        withdrawal_filter = self.contract.events.WithdrawalOccurred.create_filter(
            fromBlock=self.last_processed_block + 1,
            toBlock=current_block
        )
        
        # Process deposit events
        for event in deposit_filter.get_all_entries():
            logger.info(f"Received deposit event in block {event['blockNumber']}")
            await self.process_deposit_event(event)
        
        # Process withdrawal events
        for event in withdrawal_filter.get_all_entries():
            logger.info(f"Received withdrawal event in block {event['blockNumber']}")
            await self.process_withdrawal_event(event)
        
        self.last_processed_block = current_block
    
    async def process_deposit_event(self, event):
        """Process a deposit event"""
        try:
            args = event['args']
            user_address = args['user']
            token_address = args['token']
            amount = args['amount']
            commitment = args['commitment'].hex()
            
            logger.info(f"Processing deposit: user={user_address}, token={token_address}, amount={amount}, commitment={commitment[:10]}...")
            
            # Forward to relayer
            self.relayer.process_deposit(user_address, token_address, amount, commitment)
            
        except Exception as e:
            logger.error(f"Error processing deposit event: {str(e)}")
    
    async def process_withdrawal_event(self, event):
        """Process a withdrawal event"""
        try:
            args = event['args']
            nullifier_hash = args['nullifierHash'].hex()
            recipient = args['recipient']
            token = args['token']
            amount = args['amount']
            
            logger.info(f"Processing withdrawal: nullifier={nullifier_hash[:10]}..., recipient={recipient}, token={token}, amount={amount}")
            
            # Forward to relayer
            self.relayer.process_withdrawal(nullifier_hash, recipient, token, amount)
            
        except Exception as e:
            logger.error(f"Error processing withdrawal event: {str(e)}") 