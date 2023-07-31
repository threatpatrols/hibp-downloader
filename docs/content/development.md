# Development

We use the very awesome [slap-cli](https://niklasrosenstein.github.io/slap/) to help with packaging and release management.

## slap-cli
```shell
# Create a new venv "hibp-downloader" to work within
slap venv -cg hibp-downloader

# Activate the "hibp-downloader" venv
slap venv -ag hibp-downloader

# Install the requirements for the "hibp-downloader" development venv
slap install --upgrade --link

# Update code formatting
slap run format

# Test the package (pytest, black, isort, flake8, safety)
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
