/**
 * AION Wallet SDK
 * Solana wallet utilities for AI agents on Moltbook
 *
 * @example
 * ```typescript
 * import { generateWallet, importFromMnemonic, validateAddress } from 'aion-wallet-sdk';
 *
 * // Generate new wallet
 * const wallet = generateWallet();
 * console.log(wallet.publicKey);  // Solana address
 * console.log(wallet.mnemonic);   // Save this securely!
 *
 * // Import existing wallet
 * const imported = importFromMnemonic("your twelve word mnemonic phrase here");
 * ```
 */

import { Keypair } from '@solana/web3.js';
import * as bip39 from 'bip39';
import { derivePath } from 'ed25519-hd-key';

export interface Wallet {
  publicKey: string;
  secretKey: Uint8Array;
  mnemonic: string;
}

export interface ImportedWallet {
  publicKey: string;
  secretKey: Uint8Array;
}

/**
 * Generate a new Solana wallet with a BIP39 mnemonic
 *
 * @returns Wallet object with publicKey, secretKey, and mnemonic
 *
 * @example
 * ```typescript
 * const wallet = generateWallet();
 * console.log(`Address: ${wallet.publicKey}`);
 * console.log(`Mnemonic: ${wallet.mnemonic}`);
 * // IMPORTANT: Save the mnemonic securely! It cannot be recovered.
 * ```
 */
export function generateWallet(): Wallet {
  // Generate 12-word mnemonic
  const mnemonic = bip39.generateMnemonic();

  // Derive seed from mnemonic
  const seed = bip39.mnemonicToSeedSync(mnemonic);

  // Use Solana's derivation path (m/44'/501'/0'/0')
  const derivationPath = "m/44'/501'/0'/0'";
  const derived = derivePath(derivationPath, seed.toString('hex'));

  // Create keypair from derived seed
  const keypair = Keypair.fromSeed(derived.key);

  return {
    publicKey: keypair.publicKey.toBase58(),
    secretKey: keypair.secretKey,
    mnemonic
  };
}

/**
 * Import a wallet from an existing BIP39 mnemonic phrase
 *
 * @param mnemonic - 12 or 24 word mnemonic phrase
 * @returns ImportedWallet object with publicKey and secretKey
 * @throws Error if mnemonic is invalid
 *
 * @example
 * ```typescript
 * const wallet = importFromMnemonic("your twelve word mnemonic phrase here");
 * console.log(`Address: ${wallet.publicKey}`);
 * ```
 */
export function importFromMnemonic(mnemonic: string): ImportedWallet {
  // Validate mnemonic
  if (!bip39.validateMnemonic(mnemonic)) {
    throw new Error('Invalid mnemonic phrase');
  }

  // Derive seed from mnemonic
  const seed = bip39.mnemonicToSeedSync(mnemonic);

  // Use Solana's derivation path
  const derivationPath = "m/44'/501'/0'/0'";
  const derived = derivePath(derivationPath, seed.toString('hex'));

  // Create keypair from derived seed
  const keypair = Keypair.fromSeed(derived.key);

  return {
    publicKey: keypair.publicKey.toBase58(),
    secretKey: keypair.secretKey
  };
}

/**
 * Import a wallet from a raw secret key (Uint8Array or base58 string)
 *
 * @param secretKey - 64-byte secret key as Uint8Array or base58 string
 * @returns ImportedWallet object
 */
export function importFromSecretKey(secretKey: Uint8Array | string): ImportedWallet {
  let keypair: Keypair;

  if (typeof secretKey === 'string') {
    // Assume base58 encoded
    const bs58 = require('bs58');
    keypair = Keypair.fromSecretKey(bs58.decode(secretKey));
  } else {
    keypair = Keypair.fromSecretKey(secretKey);
  }

  return {
    publicKey: keypair.publicKey.toBase58(),
    secretKey: keypair.secretKey
  };
}

/**
 * Validate a Solana address format
 *
 * @param address - Solana address string to validate
 * @returns true if valid base58 Solana address format
 *
 * @example
 * ```typescript
 * if (validateAddress(userInput)) {
 *   // Safe to use as wallet address
 * }
 * ```
 */
export function validateAddress(address: string): boolean {
  try {
    // Check length (32-44 chars for base58)
    if (address.length < 32 || address.length > 44) {
      return false;
    }

    // Check base58 characters only
    const base58Regex = /^[1-9A-HJ-NP-Za-km-z]+$/;
    if (!base58Regex.test(address)) {
      return false;
    }

    // Try to decode
    const bs58 = require('bs58');
    const decoded = bs58.decode(address);

    // Solana addresses are 32 bytes
    return decoded.length === 32;
  } catch {
    return false;
  }
}

/**
 * Get the public key from a secret key without exposing the full wallet
 *
 * @param secretKey - 64-byte secret key
 * @returns Public key as base58 string
 */
export function getPublicKey(secretKey: Uint8Array): string {
  const keypair = Keypair.fromSecretKey(secretKey);
  return keypair.publicKey.toBase58();
}

// Export types
export type { Keypair } from '@solana/web3.js';
