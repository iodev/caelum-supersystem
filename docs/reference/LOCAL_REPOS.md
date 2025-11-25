# Local-Only Repositories

These repositories in `/home/rford/caelum/ss/` are **not included as submodules** because they don't have remote Git repositories:

## caelum-cli

**Location**: `/home/rford/caelum/ss/caelum-cli/`
**Status**: Local development only, no remote configured
**Purpose**: Command-line tools for Caelum ecosystem

### Why Not Included?

Git submodules require each component to have a remote repository URL. The `caelum-cli` directory is currently a local-only repository without a configured `origin` remote.

### To Include Later

If you want to add `caelum-cli` as a submodule in the future:

1. Create a GitHub repository:
   ```bash
   cd /home/rford/caelum/ss/caelum-cli
   gh repo create caelum-cli --public --source=. --remote=origin
   git push -u origin main  # or master
   ```

2. Add as submodule to caelum-supersystem:
   ```bash
   cd /home/rford/caelum/caelum-supersystem
   git submodule add https://github.com/iodev/caelum-cli.git caelum-cli
   git commit -m "chore: add caelum-cli submodule"
   git push
   ```

### Current Workaround

For now, `caelum-cli` remains in `/home/rford/caelum/ss/caelum-cli/` and must be managed separately from the meta-repository.

---

**Note**: This is not an issue if `caelum-cli` is experimental, temporary, or truly intended to be local-only. The meta-repository successfully tracks the 9 production components with remotes.
