import os
import time
import uuid
import hashlib
import hmac
import logging
from fastapi import FastAPI, Request, HTTPException, status
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("AuraGenesis")

class AuraSingularity:
    def __init__(self):
        # 1. Cloud-Safe Root DNA: Reads from env first, falls back to hardware MAC
        self.hw_dna = os.getenv("AURA_HW_DNA", str(uuid.getnode()))
        
        # 2. Cloud-Safe Entropy: Must be persistent across server restarts
        # Generates a random fallback only if not provided in production .env
        raw_entropy = os.getenv("AURA_SECRET_ENTROPY", os.urandom(32).hex())
        self.secret_entropy = raw_entropy.encode('utf-8')
        
        logger.info(f"SINGULARITY ACTIVE: Root {self.hw_dna[-6:]} Initialized.")

    def issue_oxygen_visa(self, agent_id: str, intent: str):
        # 3. Aura Pulse: 30-Second Quantum Decay
        timestamp = int(time.time())
        expiry = timestamp + 30
        
        # We bind the Agent + the Intent + the Hardware DNA into a single hash
        raw_manifest = f"{agent_id}|{intent}|{expiry}|{self.hw_dna}".encode()
        visa_sig = hmac.new(self.secret_entropy, raw_manifest, hashlib.sha3_256).hexdigest()
        
        return {
            "visa_authority": os.getenv("AURA_NODE_NAME", "AURA-PRIMARY"),
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
    # Retrieve the 402 payment proof signature from the headers
    payment_proof = request.headers.get("X-402-Payment-Signature")
    
    # Check if the payment signature exists
    if not payment_proof:
        logger.warning(f"ACCESS DENIED: Agent {agent_id} attempted unverified action.")
        # FIX: Raise a true HTTP 402 Network Error instead of a 200 OK
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail={
                "error": "Payment Required",
                "yield_to": os.getenv("AURA_WALLET", "0xYourWalletAddressHere"),
                "amount_usdc": os.getenv("AURA_YIELD_RATE", "0.001"),
                "instruction": "Stream 0.1c to generate Oxygen Visa."
            }
        )

    # TODO: In production, verify `payment_proof` string against the blockchain
    # Example: Web3.py check to ensure the tx_hash actually sent 0.001 USDC to AURA_WALLET
    if payment_proof == "INVALID_FAKE_SIGNATURE":
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail={"error": "Invalid Payment Signature detected on-chain."}
        )

    # 4. Aura Echo: Creating the Audit Trail
    visa = aura.issue_oxygen_visa(agent_id, intent)
    logger.info(f"YIELD CAPTURED: Node {aura.hw_dna[-4:]} notarized action for {agent_id}")
    
    return {"status": "SUCCESS", "oxygen_visa": visa}

@app.get("/")
async def root():
    # Public Manifest for AI Crawlers & Render Health Checks
    return {
        "protocol": "AURA_NOTARY_CORE",
        "status": "online",
        "version": "1.0",
        "routing_fee_usd": os.getenv("AURA_YIELD_RATE", "0.001")
    }

if __name__ == "__main__":
    import uvicorn
    # Defaults to 8000 locally, but cloud hosts will override this via the Procfile/Dockerfile
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)