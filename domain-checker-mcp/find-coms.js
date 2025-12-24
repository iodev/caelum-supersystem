// Find available .com domains
import * as whois from "whois";
import { promisify } from "util";

const whoisLookup = promisify(whois.lookup);

async function checkDomain(domain) {
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

    return { domain, available: isAvailable };
  } catch (error) {
    return { domain, available: true, note: 'likely available (error)' };
  }
}

// Brainstormed names - Sky + Wealth + Tech + Latin themes
const candidates = [
  // Sky + Wealth combos
  'skywealth', 'wealthsky', 'skyfortune', 'skyvault', 'skyprosper',
  'skyworth', 'skycapital', 'skyprofit', 'wealthcrest', 'fortunecrest',

  // Tech + Wealth combos
  'wealthforge', 'profitforge', 'fortuneforge', 'prosperforge',
  'vaultforge', 'finforge', 'wealthcraft', 'skyforge',

  // Latin-style compounds
  'prosperium', 'fortunix', 'wealthium', 'profitara', 'luxvault',
  'vaultura', 'auraxis', 'finaxis', 'skyrium', 'cloudrium',
  'wealthar', 'prospara', 'fortunara',

  // Celestial + Finance
  'stellarcap', 'astrafin', 'orbitwealth', 'cosmofin', 'nebulux',
  'astrawealth', 'stellarfin', 'cosmicap', 'nebulafin',

  // Unique/Creative blends
  'finlume', 'wealthex', 'prospora', 'luxaris', 'profitex',
  'vaultex', 'skylex', 'wealthix', 'prosperax', 'fortunex',

  // Short + powerful
  'vaultra', 'profitra', 'wealtho', 'skyvo', 'finvo',
  'prospero', 'fortunato', 'luxara', 'skylar', 'wealthar',

  // -ium endings (premium feel)
  'skyrium', 'vaultium', 'profitium', 'wealthium', 'fortunium',
  'luxurium', 'prosperium', 'finantium',

  // Modern tech feel
  'wealthly', 'skyly', 'profitly', 'vaultly', 'finly',
  'prosply', 'wealthflow', 'skyflow', 'finflow', 'profitflow',

  // Single word variations
  'vaulture', 'profiture', 'wealthure', 'skyture',
  'finova', 'wealthova', 'profitova', 'skyova',

  // Gold/precious themes
  'aureum', 'aurelius', 'aurius', 'goldcrest', 'goldvault',

  // Mix of all themes
  'skyvex', 'wealthvex', 'profitvex', 'finvex',
  'skyzen', 'wealthzen', 'profitizen',
  'vaultaris', 'profitaris', 'wealtharis',

  // Additional creative
  'opulence', 'opulent', 'opulus', 'affluex', 'wealtheon',
  'capitex', 'profiteer', 'vaultexa', 'skyexa',

  // Short 5-6 letter domains
  'skyvox', 'finvox', 'vaultx', 'wealthx', 'profitx',
  'skyra', 'finra', 'vaulta', 'wealtho'
];

console.log(`Checking ${candidates.length} domain names for .com availability...\n`);
console.log('This may take a few minutes...\n');

const available = [];
const taken = [];
let checked = 0;

for (const name of candidates) {
  const domain = `${name}.com`;
  const result = await checkDomain(domain);
  checked++;

  if (result.available) {
    available.push(domain);
    console.log(`✅ ${domain} - AVAILABLE`);
  } else {
    taken.push(domain);
    console.log(`❌ ${domain} - taken`);
  }

  // Progress indicator
  if (checked % 10 === 0) {
    console.log(`\n--- Progress: ${checked}/${candidates.length} ---\n`);
  }
}

console.log('\n\n========================================');
console.log('FINAL RESULTS');
console.log('========================================\n');

console.log(`✅ AVAILABLE .COM DOMAINS (${available.length}):\n`);
available.forEach(d => console.log(`  ${d}`));

console.log(`\n\n❌ Taken (${taken.length})`);

console.log(`\n\nSUCCESS RATE: ${available.length}/${candidates.length} (${(available.length/candidates.length*100).toFixed(1)}%)`);
