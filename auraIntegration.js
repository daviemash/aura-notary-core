// auraIntegration.js
const AURA_BACKEND_URL = "https://aura-protocol.onrender.com";

/**
 * 1. Connect Web3 Wallet (DID Authentication)
 */
async function connectAuraWallet() {
    if (typeof window.ethereum !== 'undefined') {
        try {
            const accounts = await window.ethereum.request({ method: 'eth_requestAccounts' });
            const walletAddress = accounts[0];
            console.log("Aura DID Connected:", walletAddress);
            return walletAddress;
        } catch (error) {
            console.error("Wallet Connection Declined:", error);
            return null;
        }
    } else {
        alert("Web3 Wallet not detected. Please install MetaMask or a compatible browser wallet.");
        return null;
    }
}

/**
 * 2. Execute AI Model Query with x402 Handshake
 */
async function queryAuraModel(agentId, promptIntent, modelId = "gpt-4o", paymentSignature = null) {
    const headers = { "Content-Type": "application/json" };
    if (paymentSignature) {
        headers["X-402-Payment-Signature"] = paymentSignature;
    }

    try {
        const url = `${AURA_BACKEND_URL}/v1/request-notarization?agent_id=${encodeURIComponent(agentId)}&intent=${encodeURIComponent(promptIntent)}&model_id=${encodeURIComponent(modelId)}`;
        const response = await fetch(url, { method: "POST", headers: headers });

        // HTTP 402 Handshake Interception
        if (response.status === 402) {
            const payDetails = await response.json();
            console.warn("HTTP 402 Payment Required Triggered:", payDetails.detail);
            
            alert(`Aura Toll Gate: $${payDetails.detail.amount_usdc} USDC required to route query to ${modelId}.\nStreaming to: ${payDetails.detail.yield_to}`);
            return null;
        }

        if (response.ok) {
            const data = await response.json();
            console.log("Oxygen Visa Issued:", data.oxygen_visa);
            return data.oxygen_visa;
        }
    } catch (error) {
        console.error("Aura Network Error:", error);
    }
}

/**
 * 3. Execute Scraper Query with Publisher Yield Sharing
 */
async function queryAuraScraper(agentId, targetUrl, paymentSignature = null) {
    const headers = { "Content-Type": "application/json" };
    if (paymentSignature) {
        headers["X-402-Payment-Signature"] = paymentSignature;
    }

    try {
        const url = `${AURA_BACKEND_URL}/v1/request-scrape?agent_id=${encodeURIComponent(agentId)}&target_url=${encodeURIComponent(targetUrl)}`;
        const response = await fetch(url, { method: "POST", headers: headers });

        if (response.status === 402) {
            const payDetails = await response.json();
            console.warn("Publisher Yield Share 402 Triggered:", payDetails.detail);
            
            alert(`Ethical Scraper Gate: $${payDetails.detail.amount_usdc} USDC required.\n50% paid to website owner at ${payDetails.detail.publisher_yield_to}`);
            return null;
        }

        if (response.ok) {
            const data = await response.json();
            console.log("Scrape Visa Granted:", data.oxygen_visa);
            return data.oxygen_visa;
        }
    } catch (error) {
        console.error("Scraper Network Error:", error);
    }
}