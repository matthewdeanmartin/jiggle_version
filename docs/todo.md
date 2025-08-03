2025 TODO
--- 
- Break dependency on setuptools, reimplement find_package
- Use argparse, the bots understand it better
- Fix command structure
  - bump - increment version
  - display - displays version(s)
- Args to
  - Increment (sub)modules (could have `__version__` per file)
  - Increment package (one per collection, could be a "main module")

---
# Security features
- Stop running setup.py or any shell commands

# Workflow features
- some sort of git tag awareness/sync features

# New places to put version numbers
- support pyproject.toml
- related: support projects that don't involve setup.py at all.

# Multifile bumping
- update major & minor with user input (low value scenario, imho)

# Linting
- Just detect if version layout as of now is sane. Why? When version metadata is
laid out in a sane manner, it is easier to bump

# Broad support
- add tox for 3.x-3.9
- run vermin to get min
- Allow running tool in docker
- pre-commit support? 

# CLI
- clean up the clunky options
- provide a zero-options workflow
- some way to specify which branch gets bumps (maybe prompt for input if not known?)