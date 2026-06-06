# Validate

The `validate` command allows you to inspect and repair your local pwned password dataset. It checks each hash-prefix file in the dataset for integrity, corrupted archives, and orphaned metadata records.

If a file fails validation:
- Corrupted data and metadata files are automatically deleted so they can be clean-fetched on the next `download` run.
- Orphaned metadata files (where the actual data file is missing) are cleaned up automatically.

## Usage

```commandline
hibp-downloader validate [OPTIONS]
```

### Options

* `--hash-type` (sha1 or ntlm): The hash algorithm dataset to validate. [default: `sha1`]
* `--first-hash`: Start the validator from a specific prefix (trimmed to the first 5 characters). [default: `00000`]
* `--last-hash`: Stop the validator at a specific prefix (trimmed to the first 5 characters). [default: `fffff`]

## Logs and Progress Updates

During validation, the tool outputs real-time status and rates (prefixes per second). The progress line features three two-letter status counters:

* **`vd` (valid)**: Count of prefixes that successfully passed integrity checks.
* **`ms` (missing)**: Count of prefixes where no data file exists (expected if you haven't downloaded the full range).
* **`cr` (corrupted)**: Count of prefixes that failed decompression or encoding verification and were purged.

## Example

```commandline
$ hibp-downloader --data-path /opt/storage/hibp-datastore validate --first-hash "00000" --last-hash "00fff"
2026-06-06T22:15:32+1000 | INFO | hibp-downloader | HIBP Downloader: v0.4.2
2026-06-06T22:15:32+1000 | INFO | hibp-downloader | data-path '/opt/storage/hibp-datastore'
2026-06-06T22:15:32+1000 | INFO | hibp-downloader | Legend: vd = valid, ms = missing, cr = corrupted
2026-06-06T22:15:33+1000 | INFO | hibp-downloader | prefix=00100 status=[vd:256 ms:0 cr:0] rate=256.0/s
2026-06-06T22:15:34+1000 | INFO | hibp-downloader | prefix=00200 status=[vd:512 ms:0 cr:0] rate=256.0/s
...
```
