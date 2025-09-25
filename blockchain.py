import hashlib
import json
from time import time
from uuid import uuid4


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

    def proof_of_work(self, last_proof):
        """
        a simple algorithm check:
        - find the number p`, as hash(pp`) contains 4 leading zeros,
        where p is the previous proof, 
        and p` is the new one

        :param last_proof: <int> last proof
        :return: <int> current proof
        """
        proof = 0
        while self.valid_proof(last_proof, proof) is False:
            proof += 1

        return proof

    @staticmethod
    def valid_proof(last_proof, proof):
        """
        proof verification: does hash(last_proof, proof) contain 4 leading zeros?
        :param last_proof: <int> last proof
        :param proof: <int> current proof
        :return: <bool>
        """
        guess = f'{last_proof}{proof}'.encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[:5] == "00000"

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