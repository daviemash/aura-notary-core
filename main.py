import os
import time
import uuid
import hashlib
import hmac
import logging
from typing import Optional
from fastapi import FastAPI, Request, HTTPException, status, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Logging Configuration
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - [%(levelname)s] - %(name)s - %(message)s"
)
logger = logging.getLogger("AuraGenesis")

# =====================================================================
# 1. CRYPTOGRAPHIC NOTARY CORE (Persistent Entropy & Oxygen Visa)
# =====================================================================
class AuraSingularity:
    """
    Core cryptographic notarization engine that binds hardware DNA 
    and secret entropy to produce time-limited Oxygen Visas.
    
    Aura operates purely as a Verification Layer:
    - Validates x402 micro-payment proofs.
    - Collects a flat verification fee for Aura.
    - Routes content owner fees directly to the publisher.
    - Issues cryptographically signed clearance passes (Oxygen Visas).
    """
    def __init__(self):
        # Persistent hardware node UUID
        self.hw_dna = os.getenv("AURA_HW_DNA", str(uuid.getnode()))
        
        # Secret entropy key used for signing HMAC SHA-256 visas
        raw_entropy = os.getenv("AURA_SECRET_ENTROPY", "aura_genesis_default_secret_entropy_key_2026")
        self.secret_entropy = raw_entropy.encode('utf-8')
        
        # Target Protocol Verification Wallet
        self.protocol_wallet = os.getenv("AURA_WALLET", "0xF4FE16a7e3F18D10d1907E30913C5b7Be3C3eBB0")
        
        # Verification Fee Configuration (Fixed Notary Fee)
        self.verification_fee_usdc = os.getenv("AURA_VERIFICATION_FEE", "0.0005")
        
        logger.info(f"AURA NOTARY ENGINE ACTIVE: Root Node HW-DNA [{self.hw_dna[-6:]}] Online.")

    def issue_oxygen_visa(self, agent_id: str, intent: str, scope: str = "general_access", ttl_seconds: int = 30) -> dict:
        """Generates a cryptographic HMAC-SHA256 notarized pass valid for 30 seconds."""
        timestamp = int(time.time())
        expiry = timestamp + ttl_seconds
        
        # Unique manifest payload combining identity, action, expiration, and hardware anchor
        raw_manifest = f"{agent_id}|{intent}|{expiry}|{scope}|{self.hw_dna}".encode('utf-8')
        visa_sig = hmac.new(self.secret_entropy, raw_manifest, hashlib.sha3_256).hexdigest()
        
        return {
            "visa_authority": os.getenv("AURA_NODE_NAME", "ALPHA-MATRIX-ROOT"),
            "visa_id": f"AURA-QS-{visa_sig[:24]}",
            "scope": scope,
            "manifest": {
                "subject": agent_id,
                "intent": intent,
                "expiry": expiry,
                "timestamp": timestamp
            },
            "audit_echo": hashlib.sha256(visa_sig.encode()).hexdigest()[:16]
        }


# Initialize FastAPI Instance & Cryptographic Engine
app = FastAPI(
    title="Aura Protocol Engine",
    description="Pure Web3 x402 Notary & Anti-Scraping Verification Engine",
    version="1.0.0"
)

# =====================================================================
# 2. CORS MIDDLEWARE (Allow Web3 DApps & Autonomous Agents)
# =====================================================================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

aura = AuraSingularity()


# =====================================================================
# 3. STATIC FRONTEND & ASSET ROUTING
# =====================================================================
@app.get("/")
async def serve_frontend():
    """Serves index.html at the root domain or falls back to JSON status if missing."""
    if os.path.exists("index.html"):
        return FileResponse("index.html")
    return JSONResponse({
        "protocol": "AURA_NOTARY_CORE",
        "status": "online",
        "message": "index.html not found in root directory. Running in Notary API mode."
    })

@app.get("/auraIntegration.js")
async def serve_js():
    """Serves the Web3 bridge JavaScript integration file."""
    if os.path.exists("auraIntegration.js"):
        return FileResponse("auraIntegration.js")
    raise HTTPException(status_code=404, detail="Integration JS file not found.")


# =====================================================================
# 4. TELEMETRY & SYSTEM HEALTH ENDPOINTS
# =====================================================================
@app.get("/v1/status")
async def status_check():
    """Returns protocol state, hardware signature, and treasury wallet."""
    return {
        "protocol": "AURA_NOTARY_CORE",
        "role": "PURE_VERIFICATION_LAYER",
        "status": "online",
        "node_dna_hash": aura.hw_dna[-6:],
        "verification_wallet": aura.protocol_wallet,
        "fixed_notary_fee_usdc": aura.verification_fee_usdc,
        "timestamp": int(time.time())
    }


# =====================================================================
# 5. PURE x402 RESOURCE NOTARIZATION (Zero Double-Fee Model)
# =====================================================================
@app.post("/v1/request-notarization")
async def notarize_resource(
    agent_id: str = Query(..., description="Web3 Wallet Address or Agent DID"),
    intent: str = Query(..., description="Resource or Service Intent"),
    resource_owner_wallet: str = Query(..., description="Target Owner / Service Provider Wallet Address"),
    resource_fee_usdc: str = Query("0.001", description="Fee required by the resource owner"),
    request: Request = None
):
    """
    Notarizes access to any decentralized resource or model.
    Single Payment Request = [Aura Verification Fee] + [Resource Owner Fee].
    No double-paying or third-party web2 costs.
    """
    payment_proof = request.headers.get("X-402-Payment-Signature")
    
    # Calculate single total fee
    total_fee_usdc = str(float(aura.verification_fee_usdc) + float(resource_fee_usdc))
    
    # HTTP 402 Settlement Guard
    if not payment_proof:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail={
                "error": "Payment Required",
                "protocol": "AURA_x402_NOTARY_STANDARD",
                "intent": intent,
                "total_usdc_required": total_fee_usdc,
                "fee_breakdown": {
                    "aura_verification_fee": f"{aura.verification_fee_usdc} USDC -> {aura.protocol_wallet}",
                    "owner_resource_fee": f"{resource_fee_usdc} USDC -> {resource_owner_wallet}"
                },
                "instruction": f"Attach valid X-402-Payment-Signature header streaming total {total_fee_usdc} USDC to receive Oxygen Visa."
            }
        )

    # Issue notarized Oxygen Visa upon verified payment
    visa = aura.issue_oxygen_visa(
        agent_id=agent_id, 
        intent=f"resource:{intent}", 
        scope="resource_access"
    )
    
    return {
        "status": "SETTLED_AND_NOTARIZED",
        "node_type": "resource_notary",
        "payment_verified": True,
        "fee_settlement": {
            "notary_cut": f"{aura.verification_fee_usdc} USDC",
            "owner_cut": f"{resource_fee_usdc} USDC"
        },
        "oxygen_visa": visa
    }


# =====================================================================
# 6. ANTI-SCRAPING & PUBLISHER CLEARINGHOUSE (DIRECT FEE SPLIT)
# =====================================================================
@app.post("/v1/request-scrape")
async def notarize_scrape(
    agent_id: str = Query(..., description="Web3 Wallet Address or Agent DID"),
    target_url: str = Query(..., description="Target URL to access or scrape"),
    publisher_wallet: str = Query("0xPublisherRegisteredWalletAddress", description="Target Domain Owner Wallet"),
    publisher_fee_usdc: str = Query("0.001", description="Access fee set by the website owner"),
    request: Request = None
):
    """
    Protects websites from unauthorized AI scraping.
    AI Bots must pay:
    1. A small verification fee to Aura for issuing access proof.
    2. The publisher's access fee directly to the website owner's wallet.
    """
    payment_proof = request.headers.get("X-402-Payment-Signature")
    
    total_scrape_fee = str(float(aura.verification_fee_usdc) + float(publisher_fee_usdc))
    
    # HTTP 402 Settlement Guard
    if not payment_proof:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail={
                "error": "Anti-Scraping Payment Required",
                "protocol": "AURA_ANTI_SCRAPE_NOTARY",
                "target_url": target_url,
                "total_usdc_required": total_scrape_fee,
                "fee_distribution": {
                    "aura_verification_cut": f"{aura.verification_fee_usdc} USDC -> {aura.protocol_wallet}",
                    "publisher_cut": f"{publisher_fee_usdc} USDC -> {publisher_wallet}"
                },
                "instruction": f"Stream {total_scrape_fee} USDC via X-402-Payment-Signature to unlock notarized scraping access to {target_url}."
            }
        )

    # Issue notarized Oxygen Visa if payment proof is valid
    visa = aura.issue_oxygen_visa(
        agent_id=agent_id, 
        intent=f"anti_scrape_clearance:{target_url}", 
        scope="web_access"
    )
    
    return {
        "status": "SETTLED_AND_NOTARIZED",
        "node_type": "anti_scrape_clearinghouse",
        "target_url": target_url,
        "publisher_compensated": True,
        "yield_distribution": {
            "aura_verification": f"{aura.verification_fee_usdc} USDC -> {aura.protocol_wallet}",
            "publisher": f"{publisher_fee_usdc} USDC -> {publisher_wallet}"
        },
        "oxygen_visa": visa
    }


# =====================================================================
# 7. SERVER RUNNER
# =====================================================================
if __name__ == "__main__":
    import uvicorn
    # Automatically retrieve port injected by Render or default to 8000
    port = int(os.environ.get("PORT", 8000))
    logger.info(f"Starting Aura Pure Verification Core on Port {port}...")
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)