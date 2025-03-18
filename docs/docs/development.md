# Development

<img src="https://github.com/NiklasRosenstein/slap/raw/develop/.github/assets/logo.svg" style="height: 120px; float: right; margin-left: 24px; margin-bottom: 24px">

This project uses the very awesome **[slap-cli](https://niklasrosenstein.github.io/slap/)** utility to help with 
development, testing, packaging and release management.  Slap-cli works well with the fancy-and-fast UV tooling too. 

## slap-cli
```shell
# Create a new venv "env-alias" to work within
slap venv -cg env-alias

# Activate the "env-alias" venv
slap venv -ag env-alias

# Install the requirements for the "env-alias" development venv
slap install --upgrade --link

# Update code formatting
slap run format

# Test the package (pytest, uv)
slap test

# Write a "feature" changelog entry
slap changelog add -t "feature" -d "<changelog message>" [--issue <issue_url>]

# Bump the package version at the "patch" semver level
slap release patch --dry
slap release patch --tag [--push]

# Build a package
slap publish --build-directory build --dry

# Publish a package
slap publish
```
