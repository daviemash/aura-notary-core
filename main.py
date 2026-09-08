import os
import time
import uuid
import hashlib
import hmac
import logging
from fastapi import FastAPI, Request, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("AuraGenesis")

class AuraSingularity:
    def __init__(self):
        self.hw_dna = os.getenv("AURA_HW_DNA", str(uuid.getnode()))
        raw_entropy = os.getenv("AURA_SECRET_ENTROPY", os.urandom(32).hex())
        self.secret_entropy = raw_entropy.encode('utf-8')
        logger.info(f"SINGULARITY ACTIVE: Root {self.hw_dna[-6:]} Initialized.")

    def issue_oxygen_visa(self, agent_id: str, intent: str):
        timestamp = int(time.time())
        expiry = timestamp + 30
        
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

# --- NEW: CORS MIDDLEWARE ---
# This allows your frontend (Render domain) to talk to this backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, restrict this to ["https://aura-protocol.onrender.com"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

aura = AuraSingularity()

@app.post("/v1/request-notarization")
async def notarize(agent_id: str, intent: str, request: Request):
    payment_proof = request.headers.get("X-402-Payment-Signature")
    
    if not payment_proof:
        logger.warning(f"ACCESS DENIED: Agent {agent_id} attempted unverified action.")
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail={
                "error": "Payment Required",
                "yield_to": os.getenv("AURA_WALLET", "0xYourWalletAddressHere"),
                "amount_usdc": os.getenv("AURA_YIELD_RATE", "0.001"),
                "instruction": "Stream 0.1c to generate Oxygen Visa."
            }
        )

    visa = aura.issue_oxygen_visa(agent_id, intent)
    logger.info(f"YIELD CAPTURED: Node {aura.hw_dna[-4:]} notarized action for {agent_id}")
    
    return {"status": "SUCCESS", "oxygen_visa": visa}

@app.get("/")
async def root():
    return {
        "protocol": "AURA_NOTARY_CORE",
        "status": "online",
        "version": "1.0",
        "routing_fee_usd": os.getenv("AURA_YIELD_RATE", "0.001")
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)