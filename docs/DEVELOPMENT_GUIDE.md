# PassiveIncomeMaximizer - Development Guide

**Last Updated**: 2025-11-14
**For Developers**: Setup, workflow, testing, deployment

---

## Development Setup

### Prerequisites

- Node.js 20+
- Python 3.11+
- Docker & Docker Compose
- Git

### Initial Setup

```bash
# Clone repository
git clone https://github.com/yourusername/passive-income-maximizer.git
cd passive-income-maximizer

# Install Node dependencies
npm install

# Setup Python engine
cd engine
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cd ..

# Copy environment template
cp .env.example .env
# Edit .env with your API keys

# Initialize database
npm run db:push

# Start services
npm run dev  # Terminal 1: Express + React
npm run vue  # Terminal 2: Vue3 frontend
```

---

## Project Structure

```
PassiveIncomeMaximizer/
├── server/              # Express backend
│   ├── index.ts         # Entry point
│   ├── routes/          # API routes
│   ├── services/        # Business logic
│   │   ├── agents/      # 9 PIM agents
│   │   └── ...
│   └── storage.ts       # Database layer
│
├── client/              # React frontend (legacy)
├── src/                 # Vue3 frontend (modern)
├── engine/              # Python PIM Engine
├── api/                 # Flask API (alternative)
├── shared/              # Shared TypeScript types
├── tests/               # Test suites
└── docs/                # Documentation
```

---

## Development Workflow

### Branch Strategy

```
main              # Production-ready code
├── develop       # Integration branch
│   ├── feature/agent-swarm
│   ├── feature/vue3-dashboard
│   └── fix/backtest-validation
```

### Making Changes

```bash
# 1. Create feature branch
git checkout -b feature/my-feature

# 2. Make changes
# Edit code...

# 3. Test locally
npm run test
npm run type-check

# 4. Commit with conventional commits
git commit -m "feat: add new agent for sector analysis"

# 5. Push and create PR
git push origin feature/my-feature
```

### Conventional Commits

```
feat: New feature
fix: Bug fix
docs: Documentation changes
style: Code style (formatting, no logic changes)
refactor: Code restructuring
test: Adding tests
chore: Build process, dependencies
```

---

## Testing

### Unit Tests

```bash
# Run all tests
npm run test

# Run specific test file
npm run test src/components/SwarmGraph.spec.ts

# Run with coverage
npm run test:coverage
```

### Integration Tests

```bash
# Run integration tests
npm run test:integration

# Test agent communication
npm run test tests/integration/agent-bus.test.ts
```

### End-to-End Tests (Playwright)

```bash
# Install Playwright
npx playwright install

# Run E2E tests
npm run test:e2e

# Run specific test
npx playwright test tests/e2e/trading-flow.spec.ts

# Debug mode
npx playwright test --debug
```

### Testing Strategy

1. **Unit Tests** - Individual functions, components
2. **Integration Tests** - Agent collaboration, API calls
3. **Feature Tests** - Complete workflows (e.g., trade execution)
4. **E2E Tests** - Full user journeys

**Target Coverage**: >80% for critical paths

---

## Code Quality

### TypeScript

```bash
# Type checking
npm run type-check

# Fix type errors
npm run type-check --watch
```

### Linting

```bash
# Run ESLint
npm run lint

# Auto-fix
npm run lint:fix
```

### Formatting

```bash
# Check formatting
npm run format:check

# Auto-format
npm run format
```

### Pre-commit Hooks

```bash
# Setup Husky
npm install --save-dev husky lint-staged

# .husky/pre-commit
#!/bin/sh
npm run lint
npm run type-check
npm run test
```

---

## Database Operations

### Migrations

```bash
# Generate migration
npm run db:generate

# Apply migrations
npm run db:push

# Reset database
npm run db:reset
```

### Schema Changes

1. Edit `server/db/schema.ts`
2. Run `npm run db:generate`
3. Review migration in `migrations/`
4. Apply with `npm run db:push`

### Seed Data

```bash
# Seed development data
npm run db:seed

# Seed production data
npm run db:seed:prod
```

---

## Debugging

### VS Code Configuration

`.vscode/launch.json`:
```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "type": "node",
      "request": "launch",
      "name": "Debug Express Server",
      "program": "${workspaceFolder}/server/index.ts",
      "preLaunchTask": "tsc: build",
      "outFiles": ["${workspaceFolder}/dist/**/*.js"]
    },
    {
      "type": "python",
      "request": "launch",
      "name": "Debug PIM Engine",
      "program": "${workspaceFolder}/engine/pim_service.py",
      "console": "integratedTerminal"
    }
  ]
}
```

### Logging

```typescript
// Use structured logging
import { logger } from './utils/logger';

logger.info('Trade executed', {
  symbol: 'AAPL',
  quantity: 50,
  price: 175.50
});

logger.error('Order failed', {
  error: err.message,
  symbol: 'AAPL'
});
```

### Debug Endpoints

```bash
# Agent status
curl http://10.32.3.27:5000/api/agents/status | jq

# Agent Bus stats
curl http://10.32.3.27:5000/api/agents/bus/stats | jq

# Performance metrics
curl http://10.32.3.27:5000/api/performance | jq
```

---

## Building

### Development Build

```bash
# Build TypeScript
npm run build

# Build Vue3 frontend
npm run build:vue

# Build Python wheel
cd engine
python setup.py bdist_wheel
```

### Production Build

```bash
# Full production build
npm run build:prod

# Optimize assets
npm run build:optimize
```

---

## Deployment

### Docker

```bash
# Build Docker image
docker build -t pim-server .

# Run container
docker run -p 5000:5000 --env-file .env pim-server

# Docker Compose
docker-compose up -d
```

### Dockerfile

```dockerfile
FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM node:20-alpine
WORKDIR /app
COPY --from=builder /app/dist ./dist
COPY --from=builder /app/node_modules ./node_modules
COPY package*.json ./
EXPOSE 5000
CMD ["node", "dist/server/index.js"]
```

### Environment Variables

Production `.env`:
```bash
NODE_ENV=production
DATABASE_URL=postgresql://...
ALPACA_PAPER_TRADING=false
LOG_LEVEL=info
```

---

## CI/CD Pipeline

### GitHub Actions

`.github/workflows/ci.yml`:
```yaml
name: CI

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: 20
      - run: npm ci
      - run: npm run lint
      - run: npm run type-check
      - run: npm run test
      - run: npm run build

  deploy:
    needs: test
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - run: docker build -t pim-server .
      - run: docker push ghcr.io/username/pim-server:latest
```

---

## Performance Optimization

### Frontend

```bash
# Analyze bundle size
npm run build:analyze

# Optimize images
npm run optimize:images

# Lazy load routes
# Use dynamic imports in router.ts
```

### Backend

```typescript
// Use connection pooling
const pool = new Pool({ max: 20 });

// Cache frequently accessed data
const cache = new NodeCache({ stdTTL: 300 });

// Use indexes on database queries
// CREATE INDEX idx_symbol ON positions(symbol);
```

### Database

```sql
-- Add indexes
CREATE INDEX idx_positions_symbol ON positions(symbol);
CREATE INDEX idx_trades_exit_date ON trades(exit_date);

-- Analyze query performance
EXPLAIN ANALYZE SELECT * FROM positions WHERE symbol = 'AAPL';
```

---

## Monitoring

### Health Checks

```bash
# Server health
curl http://10.32.3.27:5000/api/health

# Database health
curl http://10.32.3.27:5000/api/health/db

# External services
curl http://10.32.3.27:5000/api/health/services
```

### Metrics

```typescript
// Prometheus metrics
import { register, Counter, Histogram } from 'prom-client';

const httpRequestDuration = new Histogram({
  name: 'http_request_duration_seconds',
  help: 'Duration of HTTP requests in seconds',
  labelNames: ['method', 'route', 'status_code']
});

// Expose metrics
app.get('/metrics', async (req, res) => {
  res.set('Content-Type', register.contentType);
  res.end(await register.metrics());
});
```

---

## Troubleshooting

### Common Issues

**Build Errors**:
```bash
# Clear cache
rm -rf node_modules dist .next
npm install
npm run build
```

**Database Errors**:
```bash
# Reset database
npm run db:reset
npm run db:seed
```

**Port Conflicts**:
```bash
# Kill process on port 5000
lsof -ti:5000 | xargs kill -9
```

---

## Best Practices

### Code Style

- Use TypeScript strict mode
- Prefer `const` over `let`
- Use async/await over callbacks
- Document complex functions with JSDoc
- Keep functions < 50 lines

### Security

- Never commit API keys
- Use environment variables
- Validate all inputs
- Sanitize database queries
- Use HTTPS in production

### Performance

- Use lazy loading
- Implement caching
- Optimize database queries
- Monitor memory usage
- Profile slow operations

---

## Resources

- **TypeScript Docs**: https://www.typescriptlang.org/docs
- **Vue3 Docs**: https://vuejs.org/guide/introduction.html
- **Playwright Docs**: https://playwright.dev
- **Docker Docs**: https://docs.docker.com

---

## Related Documentation

- **GETTING_STARTED.md** - Initial setup
- **ARCHITECTURE.md** - System design
- **TESTING-README.md** - Detailed testing guide

---

**For initial setup, see GETTING_STARTED.md**
**For system architecture, see ARCHITECTURE.md**
