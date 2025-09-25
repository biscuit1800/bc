import hashlib
import json
from time import time

class Blockchain():
    def __init__(self):
        self.current_transactions = []
        self.chain = []

        # creating a genesis block
        self.new_block(previous_hash=1, proof=100)


    def new_block(self, proof, previous_hash=None):
        """
        creation of new block in blockchain
        :param proof: <int> PoW
        :param previous_hash: hash of the previous block
        :return: <dict> new block
        """
        block = {
            'index': len(self.chain) + 1,
            'timestamp': time(),
            'transactions': self.current_transactions,
            'proof': proof,
            'previous_hash': previous_hash or self.hash(self.chain[-1]),
            }
        
        # reload the current transaction list
        self.current_transactions = []
        self.chain.append(block)
        return block

    def new_transaction(self, sender: str, recipient: str, amount: str) -> int:
        """
        sends a new transaction to the next block
        :param sender: <str> sender address
        :param recipient: <str> recipient address
        :param amount: <str> amount
        :return: <int> block index with this transaction
        """
        self.current_transactions.append({
            'sender' : sender,
            'recipient' : recipient,
            'amount' : amount,
        })

        return self.last_block['index'] + 1

    @staticmethod
    def hash(block):
        """
        creates a SHA-256 hash of the block
        :param block: <dict> block
        :return: <str>
        """
        # you need to make sure that the dictionary is ordered, otherwise there will be inconsistent hashes
        block_string = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()


    @property
    def last_block(self):
        # returns last block in chain
        return self.chain[-1]