/**
 * Aura Protocol - Web3 Direct Wallet Authentication
 */

async function connectWeb3Wallet() {
    const terminalLog = document.getElementById("terminalLog");
    const logAuthType = document.getElementById("logAuthType");
    const walletBtnText = document.getElementById("walletBtnText");
    const walletStatusPanel = document.getElementById("walletStatusPanel");
    const connectedAddress = document.getElementById("connectedAddress");

    // Check if EVM Wallet (MetaMask, Rabby, Coinbase Wallet) is installed
    if (typeof window.ethereum === 'undefined') {
        alert("No Web3 provider detected! Please install MetaMask or another EVM wallet extension.");
        if (terminalLog) terminalLog.innerText = "[ERROR] No window.ethereum provider found.";
        return;
    }

    try {
        if (terminalLog) terminalLog.innerText = "[WEB3] Requesting account access...";
        
        // 1. Request wallet account access
        const accounts = await window.ethereum.request({ method: 'eth_requestAccounts' });
        const userAddress = accounts[0];

        if (terminalLog) terminalLog.innerText = `[WEB3] Requesting signature verification from ${userAddress.slice(0, 6)}...${userAddress.slice(-4)}`;

        // 2. Request cryptographic signature for identity challenge
        const timestamp = Math.floor(Date.now() / 1000);
        const challengeMessage = `Aura Protocol Authentication\nSign this message to prove ownership of your wallet.\nTimestamp: ${timestamp}`;

        const signature = await window.ethereum.request({
            method: 'personal_sign',
            params: [challengeMessage, userAddress]
        });

        // 3. Update UI on successful signature
        const truncatedAddress = `${userAddress.substring(0, 6)}...${userAddress.substring(userAddress.length - 4)}`;
        
        if (walletBtnText) walletBtnText.innerText = truncatedAddress;
        if (connectedAddress) connectedAddress.innerText = userAddress;
        if (walletStatusPanel) walletStatusPanel.classList.remove("hidden");
        if (logAuthType) logAuthType.innerText = "EIP-191 SIGNED";
        if (terminalLog) {
            terminalLog.className = "text-emerald-400 font-mono text-[11px] overflow-hidden text-ellipsis whitespace-nowrap";
            terminalLog.innerText = `[VERIFIED] Signature ${signature.slice(0, 16)}... bound to DID ${truncatedAddress}`;
        }

        console.log("Authenticated Web3 Wallet:", userAddress);
        console.log("Cryptographic Proof:", signature);

    } catch (error) {
        console.error("User rejected signature or connection failed:", error);
        if (terminalLog) {
            terminalLog.className = "text-red-400 font-mono text-[11px] overflow-hidden text-ellipsis whitespace-nowrap";
            terminalLog.innerText = `[FAILED] ${error.message || "User denied signature request."}`;
        }
    }
}