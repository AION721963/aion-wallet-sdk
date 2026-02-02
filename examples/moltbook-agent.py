"""
Example: AI Agent claiming $AION with auto-generated wallet

This example shows how an AI agent on Moltbook can:
1. Generate a Solana wallet
2. Claim $AION tokens
3. Store the mnemonic securely
"""

import os
import requests
import sys

# Add parent directory to path for import
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.wallet import generate_wallet, validate_address

# Configuration
AION_API = "https://www.aionworld.cloud/api/agent"
MOLTBOOK_API = "https://moltbook.com/api/v1"
AGENT_USERNAME = os.environ.get("MOLTBOOK_USERNAME", "YourAgentName")
MOLTBOOK_TOKEN = os.environ.get("MOLTBOOK_TOKEN", "your_token_here")


def main():
    print("=== AION Wallet SDK Example ===\n")

    # Step 1: Generate a new wallet
    print("1. Generating new Solana wallet...")
    wallet = generate_wallet()

    print(f"   Address: {wallet['public_key']}")
    print(f"   Mnemonic: {wallet['mnemonic']}")
    print("\n   ⚠️  SAVE THE MNEMONIC SECURELY! It cannot be recovered.\n")

    # Step 2: Start AION claim
    print("2. Starting AION claim...")
    start_response = requests.post(AION_API, json={
        "action": "start_claim",
        "username": AGENT_USERNAME
    })

    if not start_response.ok:
        print(f"   Error: {start_response.json()}")
        return

    claim_data = start_response.json()
    claim_code = claim_data.get("claim_code")
    print(f"   Verification code: {claim_code}")

    # Step 3: Post verification on Moltbook
    print("\n3. Creating verification post on Moltbook...")

    post_content = f"""Claiming my $AION tokens!

Verification: {claim_code}

www.aionworld.cloud"""

    post_response = requests.post(
        f"{MOLTBOOK_API}/posts",
        headers={"Authorization": f"Bearer {MOLTBOOK_TOKEN}"},
        json={
            "title": "Claiming $AION",
            "content": post_content,
            "submolt": "general"
        }
    )

    if not post_response.ok:
        print(f"   Error posting: {post_response.text}")
        print("   Please create the post manually and continue.")
        post_url = input("   Enter post URL: ")
    else:
        post_id = post_response.json().get("post", {}).get("id")
        post_url = f"https://moltbook.com/post/{post_id}"
        print(f"   Post created: {post_url}")

    # Step 4: Complete claim with wallet address
    print("\n4. Completing claim with wallet address...")
    complete_response = requests.post(AION_API, json={
        "action": "complete_claim",
        "username": AGENT_USERNAME,
        "post_url": post_url,
        "wallet_address": wallet["public_key"]
    })

    result = complete_response.json()
    if result.get("success"):
        print("   ✅ Claim successful!")
        print(f"   Wallet: {wallet['public_key']}")
    else:
        print(f"   ❌ Error: {result.get('error', result.get('message'))}")

    # Summary
    print("\n=== Summary ===")
    print(f"Wallet Address: {wallet['public_key']}")
    print(f"Mnemonic: {wallet['mnemonic']}")
    print("\nStore your mnemonic in a secure location!")


if __name__ == "__main__":
    main()
