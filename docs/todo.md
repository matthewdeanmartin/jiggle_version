# Security features
- Stop running setup.py or any shell commands

# Workflow features
- some sort of git tag awareness/sync features

# New places to put version numbers
- support pyproject.toml

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