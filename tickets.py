import streamlit as st
import hashlib
import json
from time import time

from io import BytesIO

# Simple Blockchain class
class Blockchain:
    def __init__(self):
        self.chain = []
        self.current_tickets = []
        self.create_block(previous_hash='1', proof=100)  # Genesis block

    def create_block(self, proof, previous_hash):
        block = {
            'index': len(self.chain) + 1,
            'timestamp': time(),
            'tickets': self.current_tickets,
            'proof': proof,
            'previous_hash': previous_hash
        }
        self.current_tickets = []
        self.chain.append(block)
        return block

    def get_last_block(self):
        return self.chain[-1]

    def proof_of_work(self, last_proof):
        proof = 0
        while not self.valid_proof(last_proof, proof):
            proof += 1
        return proof

    @staticmethod
    def valid_proof(last_proof, proof):
        guess = f'{last_proof}{proof}'.encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[:4] == "0000"

    @staticmethod
    def hash(block):
        block_string = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    def add_ticket(self, ticket_id, buyer_name):
        # Check if ticket ID already exists in chain or pending
        for block in self.chain:
            for ticket in block['tickets']:
                if ticket['ticket_id'] == ticket_id:
                    return False  # Duplicate

        for ticket in self.current_tickets:
            if ticket['ticket_id'] == ticket_id:
                return False

        # Add ticket to pending tickets
        self.current_tickets.append({'ticket_id': ticket_id, 'buyer_name': buyer_name})
        return True

    def verify_ticket(self, ticket_id):
        for block in self.chain:
            for ticket in block['tickets']:
                if ticket['ticket_id'] == ticket_id:
                    return True, ticket['buyer_name']
        for ticket in self.current_tickets:
            if ticket['ticket_id'] == ticket_id:
                return True, ticket['buyer_name']
        return False, None

# Generate QR code image
def generate_qr_code(data):
    qr = qrcode.QRCode(version=1, box_size=5, border=2)
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    return img

# Initialize blockchain
blockchain = Blockchain()

# Streamlit UI
st.title("🎫 Blockchain-Based Event Ticketing System")

menu = st.sidebar.selectbox("Menu", ["Buy Ticket", "Verify Ticket", "View Blockchain"])

if menu == "Buy Ticket":
    st.header("Buy Your Ticket")
    ticket_id = st.text_input("Enter Unique Ticket ID (e.g. TICKET123)")
    buyer_name = st.text_input("Your Name")

    if st.button("Buy Ticket"):
        if not ticket_id or not buyer_name:
            st.warning("Please fill in both Ticket ID and your Name.")
        else:
            success = blockchain.add_ticket(ticket_id.strip(), buyer_name.strip())
            if success:
                st.success(f"Ticket '{ticket_id}' successfully bought by {buyer_name}!")
                # Generate and display QR code
                qr_img = generate_qr_code(ticket_id)
                buf = BytesIO()
                qr_img.save(buf)
                st.image(buf)
            else:
                st.error("Ticket ID already exists! Please choose a unique Ticket ID.")

elif menu == "Verify Ticket":
    st.header("Verify Your Ticket")
    ticket_id = st.text_input("Enter Ticket ID to Verify")

    if st.button("Verify Ticket"):
        if not ticket_id:
            st.warning("Please enter a Ticket ID to verify.")
        else:
            valid, owner = blockchain.verify_ticket(ticket_id.strip())
            if valid:
                st.success(f"Ticket ID '{ticket_id}' is VALID and owned by {owner}.")
            else:
                st.error(f"Ticket ID '{ticket_id}' is INVALID or does not exist.")

elif menu == "View Blockchain":
    st.header("Blockchain Ledger")
    for block in blockchain.chain:
        st.write(f"### Block {block['index']}")
        st.write(f"Timestamp: {block['timestamp']}")
        st.write(f"Previous Hash: {block['previous_hash']}")
        st.write(f"Proof: {block['proof']}")
        st.write("Tickets in this block:")
        if block['tickets']:
            for t in block['tickets']:
                st.write(f"- Ticket ID: {t['ticket_id']} | Owner: {t['buyer_name']}")
        else:
            st.write("- No tickets in this block.")
        st.markdown("---")

    if st.button("Mine New Block (Confirm Tickets)"):
        last_block = blockchain.get_last_block()
        proof = blockchain.proof_of_work(last_block['proof'])
        previous_hash = blockchain.hash(last_block)
        block = blockchain.create_block(proof, previous_hash)
        st.success(f"New block mined! Block index: {block['index']} confirming {len(block['tickets'])} tickets.")

