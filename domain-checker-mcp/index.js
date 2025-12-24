#!/usr/bin/env node

import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
} from "@modelcontextprotocol/sdk/types.js";
import * as whois from "whois";
import fetch from "node-fetch";
import { promisify } from "util";

const whoisLookup = promisify(whois.lookup);

// Popular TLDs to check
const DEFAULT_TLDS = [
  "com", "io", "ai", "cloud", "dev", "app",
  "tech", "co", "net", "org", "xyz"
];

// Create MCP server
const server = new Server(
  {
    name: "domain-checker",
    version: "1.0.0",
  },
  {
    capabilities: {
      tools: {},
    },
  }
);

// Helper: Check domain availability via WHOIS
async function checkDomainWhois(domain) {
  try {
    const result = await whoisLookup(domain);

    // Parse the WHOIS response (it's a plain text string)
    const lowerResult = result.toLowerCase();

    // Check for common "not found" indicators
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

    // Try to parse basic info if registered
    const registrarMatch = result.match(/registrar:\s*(.+)/i);
    const createdMatch = result.match(/creation date:\s*(.+)/i);
    const expiryMatch = result.match(/expir(?:y|ation) date:\s*(.+)/i);

    return {
      domain,
      available: isAvailable,
      registered: !isAvailable,
      registrar: registrarMatch ? registrarMatch[1].trim() : null,
      createdDate: createdMatch ? createdMatch[1].trim() : null,
      expiryDate: expiryMatch ? expiryMatch[1].trim() : null,
      rawSnippet: result.split('\n').slice(0, 10).join('\n') + '...'
    };
  } catch (error) {
    // WHOIS errors often mean domain is available or timeout
    if (error.message?.includes('timeout') || error.message?.includes('ENOTFOUND')) {
      return {
        domain,
        available: null,
        error: 'WHOIS lookup failed - domain may be available or service unavailable',
        errorDetails: error.message
      };
    }

    // Many WHOIS errors actually indicate availability
    return {
      domain,
      available: true,
      note: 'WHOIS query failed - likely available or new TLD',
      error: error.message
    };
  }
}

// Helper: Check multiple TLDs for a base name
async function checkMultipleTLDs(baseName, tlds = DEFAULT_TLDS) {
  const results = await Promise.all(
    tlds.map(async (tld) => {
      const domain = `${baseName}.${tld}`;
      return checkDomainWhois(domain);
    })
  );

  return {
    baseName,
    tlds: results,
    availableCount: results.filter(r => r.available === true).length,
    summary: results
      .filter(r => r.available === true)
      .map(r => r.domain)
      .join(', ') || 'None available'
  };
}

// Helper: Get pricing estimate from Namecheap (web scraping fallback)
async function getPricingEstimate(domain) {
  // This is a simplified version - in production you'd use Namecheap API
  // For now, return generic pricing
  const tld = domain.split('.').pop();

  const pricing = {
    com: { registration: 8.88, renewal: 13.98 },
    io: { registration: 39.98, renewal: 49.98 },
    ai: { registration: 89.98, renewal: 99.98 },
    cloud: { registration: 4.88, renewal: 14.98 },
    dev: { registration: 12.98, renewal: 17.98 },
    app: { registration: 14.98, renewal: 19.98 },
    tech: { registration: 5.88, renewal: 54.98 },
    co: { registration: 9.98, renewal: 32.98 },
    net: { registration: 12.98, renewal: 16.98 },
    org: { registration: 12.98, renewal: 16.98 },
    xyz: { registration: 1.00, renewal: 13.98 }
  };

  return pricing[tld] || { registration: 'unknown', renewal: 'unknown' };
}

// List available tools
server.setRequestHandler(ListToolsRequestSchema, async () => {
  return {
    tools: [
      {
        name: "check_domain",
        description: "Check if a specific domain name is available for registration",
        inputSchema: {
          type: "object",
          properties: {
            domain: {
              type: "string",
              description: "Domain name to check (e.g., 'culmina.com' or 'welkin.io')"
            }
          },
          required: ["domain"]
        }
      },
      {
        name: "check_multiple_tlds",
        description: "Check availability of a base name across multiple TLDs (.com, .io, .ai, etc.)",
        inputSchema: {
          type: "object",
          properties: {
            baseName: {
              type: "string",
              description: "Base name without TLD (e.g., 'culmina' or 'welkin')"
            },
            tlds: {
              type: "array",
              items: { type: "string" },
              description: "Optional: specific TLDs to check (defaults to popular TLDs)"
            }
          },
          required: ["baseName"]
        }
      },
      {
        name: "check_with_pricing",
        description: "Check domain availability and get pricing estimates",
        inputSchema: {
          type: "object",
          properties: {
            domain: {
              type: "string",
              description: "Domain name to check with pricing"
            }
          },
          required: ["domain"]
        }
      },
      {
        name: "bulk_check",
        description: "Check multiple domain names at once",
        inputSchema: {
          type: "object",
          properties: {
            domains: {
              type: "array",
              items: { type: "string" },
              description: "Array of domain names to check"
            }
          },
          required: ["domains"]
        }
      }
    ]
  };
});

// Handle tool calls
server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const { name, arguments: args } = request.params;

  try {
    switch (name) {
      case "check_domain": {
        const result = await checkDomainWhois(args.domain);
        const pricing = await getPricingEstimate(args.domain);

        return {
          content: [
            {
              type: "text",
              text: JSON.stringify({ ...result, pricing }, null, 2)
            }
          ]
        };
      }

      case "check_multiple_tlds": {
        const tlds = args.tlds || DEFAULT_TLDS;
        const results = await checkMultipleTLDs(args.baseName, tlds);

        // Add pricing for available domains
        for (const result of results.tlds) {
          if (result.available) {
            result.pricing = await getPricingEstimate(result.domain);
          }
        }

        return {
          content: [
            {
              type: "text",
              text: JSON.stringify(results, null, 2)
            }
          ]
        };
      }

      case "check_with_pricing": {
        const result = await checkDomainWhois(args.domain);
        const pricing = await getPricingEstimate(args.domain);

        return {
          content: [
            {
              type: "text",
              text: JSON.stringify({ ...result, pricing }, null, 2)
            }
          ]
        };
      }

      case "bulk_check": {
        const results = await Promise.all(
          args.domains.map(async (domain) => {
            const result = await checkDomainWhois(domain);
            if (result.available) {
              result.pricing = await getPricingEstimate(domain);
            }
            return result;
          })
        );

        return {
          content: [
            {
              type: "text",
              text: JSON.stringify({
                total: results.length,
                available: results.filter(r => r.available === true).length,
                results
              }, null, 2)
            }
          ]
        };
      }

      default:
        throw new Error(`Unknown tool: ${name}`);
    }
  } catch (error) {
    return {
      content: [
        {
          type: "text",
          text: JSON.stringify({ error: error.message }, null, 2)
        }
      ],
      isError: true
    };
  }
});

// Start server
async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
  console.error("Domain Checker MCP Server running on stdio");
}

main().catch((error) => {
  console.error("Fatal error:", error);
  process.exit(1);
});
