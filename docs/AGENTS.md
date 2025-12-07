# Caelum SuperSystem - Agent Guidelines

## Build & Test Commands
- **PIM (TypeScript)**: `cd PassiveIncomeMaximizer && yarn dev` | `yarn test` | `yarn test tests/unit/specific.test.ts`
- **FinVec (Python)**: `cd finvec && uv run python train_production.py` | `uv run pytest tests/`
- **Single test**: `yarn test tests/unit/my-test.test.ts` or `uv run pytest tests/test_specific.py -v`

## Code Style
- **Python**: Use `uv` exclusively (never pip/venv). Type hints required. snake_case naming.
- **TypeScript**: Strict mode. Prefer `const`. Use explicit return types on public functions.
- **Imports**: Group stdlib → third-party → local. Absolute imports preferred.
- **Error handling**: Always wrap API calls in try/catch. Log errors with context.

## Critical Rules
1. **GPU Training**: Never train on CPU. Use 10.32.3.44 or 10.32.3.62 for training.
2. **FinVec Branch**: ALWAYS check `git branch` before training - wrong branch = wasted GPU time.
3. **Secrets**: Never commit .env files or credentials. Check `.gitignore` before commits.
4. **Testing**: Required before commit. No `skip` in tests. Run `yarn test` or `uv run pytest`.
5. **Submodules**: Read the relevant `CLAUDE.md` in each submodule before making changes.

## Infrastructure
- Training: 10.32.3.27 (RTX 5060 Ti) | Inference: 10.32.3.44 (GTX 1660 Ti)
- FinColl API: `http://10.32.3.44:8002` | SenVec: `http://10.32.3.27:18000`
