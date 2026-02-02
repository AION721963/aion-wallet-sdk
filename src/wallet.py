"""
AION Wallet SDK - Python
Solana wallet utilities for AI agents on Moltbook

Usage:
    from aion_wallet import generate_wallet, import_from_mnemonic, validate_address

    # Generate new wallet
    wallet = generate_wallet()
    print(f"Address: {wallet['public_key']}")
    print(f"Mnemonic: {wallet['mnemonic']}")  # Save this securely!

    # Import existing wallet
    imported = import_from_mnemonic("your twelve word mnemonic phrase here")

Requirements:
    pip install solana mnemonic base58
"""

from typing import TypedDict, Optional
import base58
from mnemonic import Mnemonic
from solders.keypair import Keypair
import hashlib
import hmac


class Wallet(TypedDict):
    public_key: str
    secret_key: bytes
    mnemonic: str


class ImportedWallet(TypedDict):
    public_key: str
    secret_key: bytes


def generate_wallet() -> Wallet:
    """
    Generate a new Solana wallet with a BIP39 mnemonic.

    Returns:
        Wallet dict with public_key, secret_key, and mnemonic

    Example:
        wallet = generate_wallet()
        print(f"Address: {wallet['public_key']}")
        print(f"Mnemonic: {wallet['mnemonic']}")
        # IMPORTANT: Save the mnemonic securely!
    """
    # Generate 12-word mnemonic
    mnemo = Mnemonic("english")
    mnemonic = mnemo.generate(strength=128)  # 12 words

    # Derive keypair from mnemonic
    seed = mnemo.to_seed(mnemonic)
    derived_key = _derive_path(seed, "m/44'/501'/0'/0'")

    keypair = Keypair.from_seed(derived_key[:32])

    return {
        "public_key": str(keypair.pubkey()),
        "secret_key": bytes(keypair),
        "mnemonic": mnemonic
    }


def import_from_mnemonic(mnemonic: str) -> ImportedWallet:
    """
    Import a wallet from an existing BIP39 mnemonic phrase.

    Args:
        mnemonic: 12 or 24 word mnemonic phrase

    Returns:
        ImportedWallet dict with public_key and secret_key

    Raises:
        ValueError: If mnemonic is invalid

    Example:
        wallet = import_from_mnemonic("your twelve word mnemonic phrase here")
        print(f"Address: {wallet['public_key']}")
    """
    mnemo = Mnemonic("english")

    if not mnemo.check(mnemonic):
        raise ValueError("Invalid mnemonic phrase")

    seed = mnemo.to_seed(mnemonic)
    derived_key = _derive_path(seed, "m/44'/501'/0'/0'")

    keypair = Keypair.from_seed(derived_key[:32])

    return {
        "public_key": str(keypair.pubkey()),
        "secret_key": bytes(keypair)
    }


def import_from_secret_key(secret_key: bytes) -> ImportedWallet:
    """
    Import a wallet from a raw secret key.

    Args:
        secret_key: 64-byte secret key

    Returns:
        ImportedWallet dict with public_key and secret_key
    """
    keypair = Keypair.from_bytes(secret_key)

    return {
        "public_key": str(keypair.pubkey()),
        "secret_key": bytes(keypair)
    }


def validate_address(address: str) -> bool:
    """
    Validate a Solana address format.

    Args:
        address: Solana address string to validate

    Returns:
        True if valid base58 Solana address format

    Example:
        if validate_address(user_input):
            # Safe to use as wallet address
            pass
    """
    try:
        # Check length
        if len(address) < 32 or len(address) > 44:
            return False

        # Try to decode base58
        decoded = base58.b58decode(address)

        # Solana addresses are 32 bytes
        return len(decoded) == 32
    except Exception:
        return False


def get_public_key(secret_key: bytes) -> str:
    """
    Get the public key from a secret key.

    Args:
        secret_key: 64-byte secret key

    Returns:
        Public key as base58 string
    """
    keypair = Keypair.from_bytes(secret_key)
    return str(keypair.pubkey())


def _derive_path(seed: bytes, path: str) -> bytes:
    """
    Derive a key from seed using BIP32/ED25519 derivation.

    Args:
        seed: BIP39 seed bytes
        path: Derivation path (e.g., "m/44'/501'/0'/0'")

    Returns:
        Derived key bytes
    """
    # ED25519 seed derivation
    key = hmac.new(b"ed25519 seed", seed, hashlib.sha512).digest()
    chain_code = key[32:]
    key = key[:32]

    # Parse path
    segments = path.replace("m/", "").split("/")

    for segment in segments:
        hardened = segment.endswith("'")
        index = int(segment.rstrip("'"))

        if hardened:
            index += 0x80000000

        # Derive child key
        data = b"\x00" + key + index.to_bytes(4, "big")
        derived = hmac.new(chain_code, data, hashlib.sha512).digest()
        key = derived[:32]
        chain_code = derived[32:]

    return key


# Convenience aliases
create_wallet = generate_wallet
from_mnemonic = import_from_mnemonic
from_secret = import_from_secret_key
is_valid_address = validate_address
