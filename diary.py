import streamlit as st
import hashlib
import json
from time import time, ctime

# Blockchain class for diary entries
class Blockchain:
    def __init__(self):
        self.chain = []
        self.current_entries = []
        self.create_block(proof=100, previous_hash='1')  # Genesis block

    def create_block(self, proof, previous_hash):
        block = {
            'index': len(self.chain) + 1,
            'timestamp': time(),
            'entries': self.current_entries,
            'proof': proof,
            'previous_hash': previous_hash
        }
        self.current_entries = []
        self.chain.append(block)
        return block

    def get_last_block(self):
        return self.chain[-1]

    def proof_of_work(self, last_proof):
        proof = 0
        while not self.valid_proof(last_proof, proof):
            proof += 1
        return proof

    def valid_proof(self, last_proof, proof):
        guess = f'{last_proof}{proof}'.encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[:4] == "0000"

    def hash(self, block):
        return hashlib.sha256(json.dumps(block, sort_keys=True).encode()).hexdigest()

    def add_entry(self, entry):
        self.current_entries.append(entry)

# Streamlit UI & app logic
st.set_page_config(page_title="Blockchain Digital Diary", layout="centered")
st.title("📔 Blockchain-based Digital Diary (Tamper-Proof Notes)")

blockchain = Blockchain()

# Input new diary entry
st.header("📝 Write Your Daily Note")

note = st.text_area("Enter today's note")

if st.button("Add Note"):
    if note.strip() == "":
        st.warning("Please write something before adding your note.")
    else:
        entry = {
            "note": note.strip(),
            "timestamp": time()
        }
        blockchain.add_entry(entry)
        st.success("🖊️ Note added to pending entries! Remember to mine a block to save permanently.")

# Mine a block with current pending entries
st.header("⛓️ Mine a Block to Save Your Notes Permanently")

if st.button("Mine Block"):
    if len(blockchain.current_entries) == 0:
        st.warning("No new notes to mine. Add some notes first!")
    else:
        last_block = blockchain.get_last_block()
        last_proof = last_block['proof']
        proof = blockchain.proof_of_work(last_proof)
        previous_hash = blockchain.hash(last_block)
        block = blockchain.create_block(proof, previous_hash)
        st.success(f"⛏️ Block #{block['index']} mined successfully! Your notes are now permanent and tamper-proof.")

# Display the blockchain diary timeline
st.header("📜 Diary Timeline (Blockchain Ledger)")

if len(blockchain.chain) == 0:
    st.info("No diary entries yet. Start by adding notes and mining blocks!")
else:
    for block in blockchain.chain:
        st.subheader(f"Block #{block['index']} (Timestamp: {ctime(block['timestamp'])})")
        st.write(f"Proof: {block['proof']}")
        st.write(f"Previous Hash: {block['previous_hash']}")
        if block['entries']:
            for idx, entry in enumerate(block['entries'], start=1):
                note_time = ctime(entry['timestamp'])
                st.markdown(f"**Note {idx}** ({note_time}): {entry['note']}")
        else:
            st.write("No entries in this block.")
        st.markdown("---")

# Explanation
st.sidebar.header("About this App")
st.sidebar.info("""
This digital diary uses blockchain technology to ensure your daily notes are permanent and tamper-proof.

- Notes are added as entries (transactions).
- Mining a block saves all pending notes permanently.
- Once saved in a block, notes cannot be edited or deleted.
- This simulates real-world scenarios where data integrity is critical (e.g., medical logs, research notes).

Try adding some notes, then mine a block to secure them!
""")
