/**
 * Simple example: Generate and validate Solana wallets
 */

import { generateWallet, importFromMnemonic, validateAddress } from '../src';

// Generate a new wallet
console.log('=== Generate New Wallet ===');
const wallet = generateWallet();
console.log(`Address: ${wallet.publicKey}`);
console.log(`Mnemonic: ${wallet.mnemonic}`);
console.log('');

// Validate addresses
console.log('=== Validate Addresses ===');
const testAddresses = [
  wallet.publicKey,
  'InvalidAddress123',
  '11111111111111111111111111111111', // System program
];

for (const addr of testAddresses) {
  const valid = validateAddress(addr);
  console.log(`${addr.slice(0, 20)}... : ${valid ? '✅ Valid' : '❌ Invalid'}`);
}
console.log('');

// Import from mnemonic
console.log('=== Import from Mnemonic ===');
const imported = importFromMnemonic(wallet.mnemonic);
console.log(`Original: ${wallet.publicKey}`);
console.log(`Imported: ${imported.publicKey}`);
console.log(`Match: ${wallet.publicKey === imported.publicKey ? '✅ Yes' : '❌ No'}`);
