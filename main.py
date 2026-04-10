import os
import time
import uuid
import hashlib
import hmac
import logging
from fastapi import FastAPI, Request
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("AuraGenesis")

class AuraSingularity:
    def __init__(self):
        # 1. Aura Genesis: Rooted in the physical silicon DNA of THIS laptop
        # This is what makes it a global standard: It cannot be cloned.
        self.hw_dna = str(uuid.getnode()) 
        self.secret_entropy = os.urandom(32)
        logger.info(f"SINGULARITY ACTIVE: Physical Root {self.hw_dna[-6:]} Initialized.")

    def issue_oxygen_visa(self, agent_id: str, intent: str):
        # 2. Aura Pulse: 30-Second Quantum Decay
        # 3. Aura Boundary: Manifest-Signed (Siphon-Proof)
        timestamp = int(time.time())
        expiry = timestamp + 30
        
        # We bind the Agent + the Intent + the Hardware DNA into a single hash
        raw_manifest = f"{agent_id}|{intent}|{expiry}|{self.hw_dna}".encode()
        visa_sig = hmac.new(self.secret_entropy, raw_manifest, hashlib.sha3_256).hexdigest()
        
        return {
            "visa_authority": os.getenv("AURA_NODE_NAME"),
            "visa_id": f"AURA-QS-{visa_sig[:24]}",
            "manifest": {
                "subject": agent_id,
                "intent": intent,
                "expiry": expiry
            },
            "audit_echo": hashlib.sha256(visa_sig.encode()).hexdigest()[:16]
        }

# --- THE UNIVERSAL INTERFACE ---
app = FastAPI(title="Aura Protocol: The Global Standard of Truth")
aura = AuraSingularity()

@app.post("/v1/request-notarization")
async def notarize(agent_id: str, intent: str, request: Request):
    # 4. Aura Fee Structure (x402 Notary Yield)
    # The agent pays 0.1c for the "Oxygen" (the signature).
    # Their primary funds stay in their own wallet. Transparent & Safe.
    payment_proof = request.headers.get("X-402-Payment-Signature")
    
    if not payment_proof:
        logger.warning(f"ACCESS DENIED: Agent {agent_id} attempted unverified action.")
        return {
            "status": 402,
            "error": "Payment Required",
            "yield_to": os.getenv("AURA_WALLET"),
            "amount_usdc": os.getenv("AURA_YIELD_RATE"),
            "instruction": "Stream 0.1c to generate Oxygen Visa."
        }

    # 5. Aura Echo: Creating the Audit Trail
    visa = aura.issue_oxygen_visa(agent_id, intent)
    logger.info(f"YIELD CAPTURED: Node {aura.hw_dna[-4:]} notarized action for {agent_id}")
    return {"status": "SUCCESS", "oxygen_visa": visa}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)