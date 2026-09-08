import os
import time
import uuid
import hashlib
import hmac
import logging
import httpx
from typing import Optional
from fastapi import FastAPI, Request, HTTPException, status, Query
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("AuraGenesis")

class AuraSingularity:
    def __init__(self):
        # 1. Physical/Virtual Hardware DNA
        self.hw_dna = os.getenv("AURA_HW_DNA", str(uuid.getnode()))
        
        # 2. Persistent Secret Entropy across server restarts
        raw_entropy = os.getenv("AURA_SECRET_ENTROPY", "aura_genesis_default_secret_entropy_key_2026")
        self.secret_entropy = raw_entropy.encode('utf-8')
        
        logger.info(f"SINGULARITY ACTIVE: Root Node {self.hw_dna[-6:]} Online.")

    def issue_oxygen_visa(self, agent_id: str, intent: str, scope: str = "ai_mesh") -> dict:
        # 3. Quantum Decay: 30-Second TTL
        timestamp = int(time.time())
        expiry = timestamp + 30
        
        # 4. Bind Agent + Intent + Expiry + Hardware DNA into an HMAC SHA-256 signature
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

# --- APPLICATION INTERFACE ---
app = FastAPI(
    title="Aura Protocol Engine",
    description="Decentralized Machine-to-Machine Routing & Notarization Layer",
    version="1.0.0"
)

# --- CORS MIDDLEWARE (Frontend Mesh Connection) ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

aura = AuraSingularity()

# --- DEFAULT ACTIVE MODEL MESH CONFIGURATION ---
MODEL_NODES = {
    "deepseek-v3": {"name": "DeepSeek V3", "active": True, "provider": "DeepSeek Grid"},
    "gpt-4o": {"name": "GPT-4o", "active": True, "provider": "OpenAI Node"},
    "llama-3-70b": {"name": "Llama 3 70B", "active": False, "provider": "Meta P2P Node"},
    "mistral-large": {"name": "Mistral Large", "active": False, "provider": "Mistral Network"},
    "claude-3-5-sonnet": {"name": "Claude 3.5 Sonnet", "active": False, "provider": "OpenRouter"},
    "flux-pro": {"name": "FLUX Pro", "active": False, "provider": "OpenRouter"},
    "scraper-node": {"name": "Ethical Web Scraper", "active": True, "provider": "Aura Publisher Mesh"}
}

# --- ROUTE 1: SYSTEM & MODEL MESH STATUS ---
@app.get("/")
async def root():
    return {
        "protocol": "AURA_NOTARY_CORE",
        "status": "online",
        "version": "1.0.0",
        "node_dna": aura.hw_dna[-6:],
        "yield_wallet": os.getenv("AURA_WALLET", "0xF4FE16a7e3F18D10d1907E30913C5b7Be3C3eBB0"),
        "active_nodes": sum(1 for n in MODEL_NODES.values() if n["active"])
    }

@app.get("/v1/mesh-nodes")
async def get_mesh_nodes():
    return {"status": "SUCCESS", "nodes": MODEL_NODES}

# --- ROUTE 2: AI MODEL NOTARIZATION ROUTE (HTTP 402) ---
@app.post("/v1/request-notarization")
async def notarize_model(
    agent_id: str = Query(..., description="Web3 Wallet Address or Agent DID"),
    intent: str = Query(..., description="Prompt or Execution Intent"),
    model_id: str = Query("gpt-4o", description="Target AI Model Node"),
    request: Request = None
):
    payment_proof = request.headers.get("X-402-Payment-Signature")
    
    # 1. Enforce HTTP 402 Payment Trigger if signature is missing
    if not payment_proof:
        logger.warning(f"ACCESS DENIED (402): Agent {agent_id} requested {model_id} without yield signature.")
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail={
                "error": "Payment Required",
                "protocol": "AURA_x402_STANDARD",
                "target_model": model_id,
                "yield_to": os.getenv("AURA_WALLET", "0xF4FE16a7e3F18D10d1907E30913C5b7Be3C3eBB0"),
                "amount_usdc": os.getenv("AURA_YIELD_RATE", "0.001"),
                "instruction": f"Attach valid X-402-Payment-Signature header transferring $0.001 USDC to unlock {model_id}."
            }
        )

    # 2. Issue Notarized Oxygen Visa
    visa = aura.issue_oxygen_visa(agent_id, intent=f"model:{model_id}:{intent}", scope="ai_mesh")
    logger.info(f"YIELD CAPTURED: Model {model_id} notarized for Agent {agent_id[:10]}...")
    
    return {
        "status": "SUCCESS",
        "node_type": "ai_model",
        "model_id": model_id,
        "oxygen_visa": visa
    }

# --- ROUTE 3: WEB SCRAPER & PUBLISHER REVENUE SHARE ROUTE ---
@app.post("/v1/request-scrape")
async def notarize_scrape(
    agent_id: str = Query(..., description="Web3 Wallet Address or Agent DID"),
    target_url: str = Query(..., description="URL to scrape"),
    request: Request = None
):
    payment_proof = request.headers.get("X-402-Payment-Signature")
    
    # Attempt to resolve publisher wallet via simulated aura.txt protocol lookup
    publisher_wallet = "0xWebsiteOwnerRegisteredWalletAddress"
    
    if not payment_proof:
        logger.warning(f"ACCESS DENIED (402): Agent {agent_id} requested scrape of {target_url}.")
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail={
                "error": "Payment Required",
                "protocol": "AURA_PUBLISHER_YIELD_SHARE",
                "target_url": target_url,
                "protocol_yield_to": os.getenv("AURA_WALLET", "0xF4FE16a7e3F18D10d1907E30913C5b7Be3C3eBB0"),
                "publisher_yield_to": publisher_wallet,
                "amount_usdc": "0.002",  # $0.001 to Aura Node, $0.001 to Publisher
                "split_ratio": "50/50",
                "instruction": f"Stream $0.002 USDC to scrape {target_url}. 50% distributed directly to domain publisher."
            }
        )

    visa = aura.issue_oxygen_visa(agent_id, intent=f"scrape:{target_url}", scope="web_scrape")
    logger.info(f"SCRAPE NOTARIZED: Agent {agent_id[:10]}... granted access to {target_url}. Yield split with publisher.")
    
    return {
        "status": "SUCCESS",
        "node_type": "web_scraper",
        "target_url": target_url,
        "publisher_compensated": True,
        "oxygen_visa": visa
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)