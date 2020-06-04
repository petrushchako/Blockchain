from blockchain import Blockchain
from uuid import uuid4           #Uniform Unique ID
from verification import Verification

class Node:
    def __init__(self):
        #self.id = str(uuid4())
        self.id = "Alex"
        self.blockchain = Blockchain(self.id)


    def get_input(self):
        """Prompts the yser for its choice and returns it.
        """
        return input('Enter your choice: ')


    def get_transaction_value(self):
        """Get input for transaction
        return: tuple with recipient and amount
        """
        tx_recipient = input('Enter the recipient of the transaction: ')
        tx_amount =float(input('Your transaction amount please:  '))
        return (tx_recipient, tx_amount)    #return tuple!!!


    def output_blockchain(self):
        """Output all blocks of the blockchain.
        """
        for item in self.blockchain.chain:
            print('Outputting blockchain: ')
            print(item)
        else: 
            print('-'*20)


    def listen_for_input(self):
        waiting_for_input = True

        while waiting_for_input:
            print('Please choose:')
            print('1: Add new transaction.')
            print('2: Mine a new block.')
            print('3: Output the blockchain blocks.')
            print('4: Check transaction validity.')
            print('q: Exit')

            user_choice = self.get_input()
            if user_choice == '1':
                tx_data = self.get_transaction_value()
                recipient, amount = tx_data
                if self.blockchain.add_transaction(recipient, self.id, amount= amount):
                    print('Added transaction!')
                else: 
                    print('Transaction failed!!!')
                print(self.blockchain.get_open_transactions())
            elif user_choice=='2':
                self.blockchain.mine_block()
            elif user_choice=='3':
                self.output_blockchain()
            elif user_choice=='4':
                if Verification.verify_transactions(self.blockchain.get_open_transactions(), self.blockchain.get_balance):
                    print('All transactions are valid.')
                else:
                    print('There are invalid transactions.')
            elif user_choice=='q':
                waiting_for_input=False
            else:
                print('Invalid option. \n')
            if not Verification.verify_chain(self.blockchain.get_chain()):
                self.output_blockchain()
                print('Invalid blockchain!')
                waiting_for_input=False
            print("{}'s balance: {:6.2f} \n".format(self.id, self.blockchain.get_balance()))        
        print('Done!')

node = Node()
node.listen_for_input()