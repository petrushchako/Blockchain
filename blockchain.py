import functools
import hashlib

import json
import pickle

from hash_util import hash_block, hash_string_256
from block import Block
from transaction import Transaction
from verification import Verification

#The reward given to miners for creating new block
MINING_REWARD =10

class Blockchain:
    def __init__(self, hosting_node_id):
        genesis_block = Block(0,'', [], 100, 0)
        #Initializing blockchain
        self.__chain = [genesis_block]
        #Unhandled transactions
        self.__open_transactions = []
        self.load_data()
        self.hosting_node = hosting_node_id


    @property
    def chain(self):
        return self.__chain[:]

    @chain.setter
    def chain(self, val):
        self.__chain = val

    def get_chain(self):
        return self.__chain[:]

    
    def get_open_transactions(self):
        return self.__open_transactions[:]


    def save_data(self):
        """ Save blockchain + open transactions snapshot to a file """
        try:
            with open('blockchain.txt', mode = 'w') as f:
                saveable_chain = [block.__dict__ for block in [Block(block_el.index, block_el.previous_hash, [tx.__dict__ for tx in block_el.transactions],block_el.proof, block_el.timestamp) for block_el in self.__chain]]

                f.write(json.dumps(saveable_chain))
                f.write("\n")
                saveable_tx = [tx.__dict__ for tx in self.__open_transactions]
                f.write(json.dumps(saveable_tx))
                #Pickle format saving
                # save_data = {
                #     'chain': blockchain,
                #     'ot': open_transactions
                # }
                # f.write(pickle.dumps(save_data))
        except IOError:
            print('Saving failed!')



    def load_data(self):
        """ Initialize blockchain + open transactions data from a file """
        try:
            with open('blockchain.txt', mode = 'r') as f:
                #file_content = pickle.loads(f.read())
                file_content = f.readlines() #list of strings
                #Pickle format loading
                # blockchain = file_content['chain']
                # open_transactions = file_content['ot']
                blockchain = json.loads(file_content[0][:-1])
                updated_blockchain = []
                for block in blockchain:
                    converted_tx = [Transaction(tx['sender'], tx['recipient'], tx['amount']) for tx in block['transactions']]
                    updated_block = Block(block['index'], block['previous_hash'], converted_tx, block['proof'], block['timestamp'])
                    updated_blockchain.append(updated_block)
                self.chain = updated_blockchain
                open_transactions = json.loads(file_content[1])
                #We need to convert the loaded data because Transactions should use OrderedDict
                updated_transactions = []
                for tx in open_transactions:
                    updated_transaction = Transaction(tx['sender'], tx['recipient'], tx['amount'])
                    updated_transactions.append(updated_transaction)
                self.__open_transactions = updated_transactions
        except (IOError, IndexError):
            print("Handled Exception.")
        finally:
            print('Cleanup!')


    def proof_of_work(self):
        """Generate a proof of work for open transactions """
        last_block = self.__chain[-1]
        last_hash = hash_block(last_block)
        proof = 0
        #Try different PoW numbers and return the first valid one
        while not Verification.valid_proof(self.__open_transactions, last_hash, proof):
            proof +=1
        return proof


    def get_balance(self):
        """Calculate and return the balanace for a participant
        """

        participant = self.hosting_node
        tx_sender = [[tx.amount for tx in block.transactions 
                        if tx.sender == participant] for block in self.__chain]
        open_tx_sender = [tx.amount 
                        for tx in self.__open_transactions if tx.sender==participant]
        tx_sender.append(open_tx_sender)
        print(tx_sender)
        #Reduce list of amount sent
        amount_sent = functools.reduce(lambda tx_sum, tx_amt: tx_sum + sum(tx_amt) if len(tx_amt)>0 else tx_sum + 0, tx_sender, 0) #tx_amt[0] as we access list of lists
        #Reduce list of amount received
        tx_recipient = [[tx.amount for tx in block.transactions 
                            if tx.recipient == participant] for block in self.__chain]
        amount_received = functools.reduce(lambda tx_sum, tx_amt: tx_sum + sum(tx_amt) if len(tx_amt)>0 else tx_sum + 0, tx_recipient, 0)
        #return the difference between amount received and sent
        return amount_received-amount_sent


    def get_last_blockchain_value(self):
        if len(self.__chain) < 1:
            return None
        return self.__chain[-1]


    def add_transaction(self, recipient, sender, amount = 1.0):
        """Append a new value as well as the last blockchain value to the blockchain

        Arguments:
            :sender: The sender of the coins
            :recipient: The recipient of the coins
            :amount: The amount of coins sent with the transaction (default = 1.0)
        """
        transaction = Transaction(sender, recipient, amount)
        if Verification.verify_transaction(transaction, self.get_balance):
            self.__open_transactions.append(transaction)
            self.save_data()
            return True
        return False

 
    def mine_block(self):
        last_block = self.__chain[-1]
        hashed_block = hash_block(last_block)
        proof = self.proof_of_work()
        reward_transaction = Transaction("MINING", self.hosting_node, MINING_REWARD)
        copied_transactions = self.__open_transactions[:]
        copied_transactions.append(reward_transaction)
        block = Block(len(self.__chain), hashed_block, copied_transactions, proof)
        self.__chain.append(block)
        self.__open_transactions = []
        self.save_data()
        return True


