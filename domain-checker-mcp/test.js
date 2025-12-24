// Quick test to verify domain checking works
import * as whois from "whois";
import { promisify } from "util";

const whoisLookup = promisify(whois.lookup);

async function testDomain(domain) {
  console.log(`\nTesting: ${domain}`);
  try {
    const result = await whoisLookup(domain);
    const lowerResult = result.toLowerCase();

    const notFoundIndicators = [
      'no match',
      'not found',
      'no entries found',
      'no data found',
      'status: available',
      'no matching record',
      'not registered'
    ];

    const isAvailable = notFoundIndicators.some(indicator =>
      lowerResult.includes(indicator)
    );

    console.log(`  Available: ${isAvailable}`);
    console.log(`  First line: ${result.split('\n')[0]}`);
  } catch (error) {
    console.log(`  Error (likely available): ${error.message}`);
  }
}

// Test with some of the suggested names
const testDomains = [
  'culmina.com', 'culmina.io', 'culmina.ai', 'culmina.cloud', 'culmina.dev',
  'welkin.com', 'welkin.io', 'welkin.ai', 'welkin.cloud', 'welkin.dev',
  'empyreal.io', 'empyreal.com', 'empyreal.ai',
  'aethereum.com', 'aethereum.io', 'aethereum.ai',
  'stratumis.com', 'stratumis.io',
  'aphelion.io', 'aphelion.ai',
  'pelagus.io', 'pelagus.ai',
  'aurorium.io', 'aurorium.com',
  'nexarium.io', 'nexarium.com',
  'vaultis.io', 'vaultis.com'
];

console.log('Running domain availability tests...\n');

for (const domain of testDomains) {
  await testDomain(domain);
}

console.log('\nTest complete!');
