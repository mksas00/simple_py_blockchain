import hashlib
import json
from time import time

class Block:
    def __init__(self, index, previous_hash, timestamp, transactions, hash_value, nonce):
        self.index = index
        self.previous_hash = previous_hash
        self.timestamp = timestamp
        self.transactions = transactions
        self.hash = hash_value
        self.nonce = nonce

    @staticmethod
    def calculate_hash(index, previous_hash, timestamp, transactions, nonce):
        block_string = f"{index}{previous_hash}{timestamp}{json.dumps(transactions)}{nonce}"
        return hashlib.sha256(block_string.encode('utf-8')).hexdigest()

    @classmethod
    def create_block(cls, index, previous_hash, transactions):
        timestamp = time()
        nonce = 0
        hash_value = cls.calculate_hash(index, previous_hash, timestamp, transactions, nonce)
        return cls(index, previous_hash, timestamp, transactions, hash_value, nonce)

    @staticmethod
    def is_valid_hash(hash_value, difficulty):
        return hash_value[:difficulty] == "0" * difficulty

    @staticmethod
    def proof_of_work(block, difficulty):
        while not Block.is_valid_hash(block.hash, difficulty):
            block.nonce += 1
            block.hash = Block.calculate_hash(
                block.index, block.previous_hash, block.timestamp, block.transactions, block.nonce)
        return block

class Blockchain:
    def __init__(self, difficulty=2):
        self.chain = []
        self.transactions = []
        self.difficulty = difficulty
        self.create_genesis_block()

    def create_genesis_block(self):
        # Dodajemy transakcję genezy
        genesis_transaction = {
            'sender': "SYSTEM",
            'recipient': "Alice",
            'amount': 100,
            'signature': None
        }
        self.transactions.append(genesis_transaction)

        genesis_block = Block.create_block(0, "0", self.transactions)
        genesis_block = Block.proof_of_work(genesis_block, self.difficulty)
        self.chain.append(genesis_block)

        self.transactions = []

    def add_transaction(self, sender, recipient, amount):
        if sender != "SYSTEM":
            balance = self.get_balance(sender)
            if balance < amount:
                print(f"Failed to add transaction: Sender '{sender}' has insufficient balance!")
                return False

        transaction = {
            'sender': sender,
            'recipient': recipient,
            'amount': amount
        }
        self.transactions.append(transaction)
        return True

    def add_block(self):
        previous_block = self.chain[-1]
        new_index = previous_block.index + 1

        new_block = Block.create_block(new_index, previous_block.hash, self.transactions)
        new_block = Block.proof_of_work(new_block, self.difficulty)

        self.chain.append(new_block)
        self.transactions = []

    def get_balance(self, public_key):
        balance = 0
        for block in self.chain:
            for transaction in block.transactions:
                if transaction['recipient'] == public_key:
                    balance += transaction['amount']
                if transaction['sender'] == public_key:
                    balance -= transaction['amount']

        for transaction in self.transactions:
            if transaction['recipient'] == public_key:
                balance += transaction['amount']
            if transaction['sender'] == public_key:
                balance -= transaction['amount']

        return balance


    def display_chain(self):
        for block in self.chain:
            print(f"Index: {block.index}, Hash: {block.hash}, Nonce: {block.nonce}, Transactions: {block.transactions}")

    def is_chain_valid(self):
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i - 1]
            # Sprawdzenie hasha poprzedniego bloku
            if current_block.previous_hash != previous_block.hash:
                return False
            # Sprawdzanie, czy hash bloku ma odpowiedna trudnosc
            if not Block.is_valid_hash(current_block.hash, self.difficulty):
                return False
            # Sprawdz czy hash bloku odpowiada jego zawartości
            expected_hash = Block.calculate_hash(
                current_block.index,
                current_block.previous_hash,
                current_block.timestamp,
                current_block.transactions,
                current_block.nonce
            )
            if current_block.hash != expected_hash:
                return False
        return True



def main():
    # Tworzymy nowy blockchain z trudnością 2 (wymaga 2 zer na początku hash)
    blockchain = Blockchain(difficulty=2)

    # Transakcja 1: Alice wysyła 50 jednostek Bobowi
    blockchain.add_transaction("Alice", "Bob", 50)
    blockchain.add_block()  # Dodajemy blok, aby transakcja została zapisana

    # Transakcja 2: Bob wysyła 30 jednostek Charliemu i 10 jednostek Johny'emu
    blockchain.add_transaction("Bob", "Charlie", 30)
    blockchain.add_transaction("Bob", "Johny", 10)
    blockchain.add_block()  # Dodajemy blok, aby te transakcje zostały zapisane

    # Transakcja 3: Charlie wysyła 50 jednostek Alice
    blockchain.add_transaction("Charlie", "Alice", 50)
    blockchain.add_block()  # Dodaj trzeci blok z tą transakcją

    # Wyświetlanie calego blockchaina
    print("\nBlockchain po dodaniu transakcji:")
    blockchain.display_chain()

    # Sprawdzanie, czy blockchain jest poprawny
    print("\nSprawdzamy, czy blockchain jest poprawny...")
    print(f"Is blockchain valid? {blockchain.is_chain_valid()}")

    # Sprawdzanie sald użytkowników
    print("\nSaldo użytkowników:")
    print(f"Alice's balance: {blockchain.get_balance('Alice')}")
    print(f"Bob's balance: {blockchain.get_balance('Bob')}")
    print(f"Charlie's balance: {blockchain.get_balance('Charlie')}")
    print(f"Johny's balance: {blockchain.get_balance('Johny')}")

if __name__ == "__main__":
    main()
