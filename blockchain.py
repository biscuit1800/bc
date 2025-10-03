import hashlib
import json
from time import time
from uuid import uuid4
from flask import Flask, jsonify, request

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
    



# create an instance of the node
app = Flask(__name__)

# generate a globally unique address for this node
node_identifier = str(uuid4()).replace('-', '')

# create an instance of blockchain
blockchain = Blockchain()


# creation of endpoint /mine, which is a GET request
@app.route('/mine', methods=['GET'])
def mine():
    # run the proof of work algorithm to get the next proof
    last_block = blockchain.last_block
    last_proof = last_block['proof']
    proof = blockchain.proof_of_work(last_proof)

    # must receive a reward for finding the proof
    # the sender "0" means that the node has earned a coin
    blockchain.new_transaction(
        sender="0",
        recipient=node_identifier,
        amount=1,
    )

    # create a new block by adding it to the chain
    previous_hash = blockchain.hash(last_block)
    block = blockchain.new_block(proof, previous_hash)

    response = {
        'message': "New Block Forged",
        'index': block['index'],
        'transactions': block['transactions'],
        'proof': block['proof'],
        'previous_hash': block['previous_hash'],
    }
    return jsonify(response), 200


# creation of endpoint /transactions/new, which is a POST request
@app.route('/transactions/new', methods=['POST'])
def new_transaction():
    values = request.get_json()

    # check that the required fields are in the POST data
    required = ['sender', 'recipient', 'amount']
    if not all(k in values for k in required):
        return 'Missing values', 400

    # create a new transaction
    index = blockchain.new_transaction(values['sender'], values['recipient'], values['amount'])

    response = {'message': f'Transaction will be added to Block {index}'}
    return jsonify(response), 201


# creation of endpoint /chain, which returns the whole blockchain
@app.route('/chain', methods=['GET'])
def full_chain():
    response = {
        'chain': blockchain.chain,
        'length': len(blockchain.chain),
    }
    return jsonify(response), 200


# run the server on port: 5000
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
