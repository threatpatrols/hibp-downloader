# hibp-downloader

[![PyPi](https://img.shields.io/pypi/v/hibp-downloader.svg)](https://pypi.python.org/pypi/hibp-downloader/)
[![Python Versions](https://img.shields.io/pypi/pyversions/hibp-downloader.svg)](https://github.com/threatpatrols/hibp-downloader/)
[![build tests](https://github.com/threatpatrols/hibp-downloader/actions/workflows/build-tests.yml/badge.svg)](https://github.com/threatpatrols/hibp-downloader/actions/workflows/build-tests.yml)
[![License](https://img.shields.io/github/license/threatpatrols/hibp-downloader.svg)](https://github.com/threatpatrols/hibp-downloader)

This is a Python implementation of the original [PwnedPasswordsDownloader](https://github.com/HaveIBeenPwned/PwnedPasswordsDownloader)
that provides some additional useful functionality 
 - Automatically only download prefix-chunks that have changed since the last download
 - Ability to start, stop and re-start without loss of data already collected
 - Ability to name the `--first-hash` and `--last-hash` positions
 - Metadata file per prefix file in JSON format for easy data reuse

## Install
```commandline
pip install --upgrade hibp-downloader
```

## Usage
![screenshot-help.png](https://raw.githubusercontent.com/threatpatrols/hibp-downloader/main/docs/assets/screenshot-help.png)

## Runtime Logs
Sample download activity logs 
```text
2023-07-30T21:42:06+1000 | INFO | hibp-downloader | prefix=65747 source=[lc:207328 et:0 rc:56672 ro:0 xx:0] runtime_rate=[10.3MBit/s 79req/s ~65602H/s] runtime=0.2hr download=922.5MB
2023-07-30T21:42:07+1000 | INFO | hibp-downloader | prefix=29da7 source=[lc:207328 et:0 rc:56792 ro:0 xx:0] runtime_rate=[10.4MBit/s 79req/s ~65646H/s] runtime=0.2hr download=924.5MB
2023-07-30T21:42:09+1000 | INFO | hibp-downloader | prefix=43c7f source=[lc:207328 et:0 rc:56912 ro:0 xx:0] runtime_rate=[10.3MBit/s 79req/s ~65617H/s] runtime=0.2hr download=926.5MB
```
 - 79 requests per second to api.pwnedpasswords.com
 - 207,328 prefix files from (`lc`) local-cache
 - 56,912 prefix files from (`rc`) remote-cache
 - 0 files from (`ro`) remote-origin, 0 files failed (`xx`) download
 - estimated 65,617 hash values downloaded per second
 - 926MB downloaded in ~12 minutes (0.20 hour)


## Issues
 - https://github.com/threatpatrols/hibp-downloader/issues

## Source
 - https://github.com/threatpatrols/hibp-downloader

## Copyright
 - Copyright &copy; 2023 Threat Patrols Pty Ltd &lt;contact@threatpatrols.com&gt;
 - Copyright &copy; 2023 Nicholas de Jong &lt;contact@nicholasdejong.com&gt;

All rights reserved.

## License
 * BSD-3-Clause - see LICENSE file for details.
