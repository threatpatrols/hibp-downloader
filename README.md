# hibp-downloader

[![PyPi](https://img.shields.io/pypi/v/hibp-downloader.svg)](https://pypi.python.org/pypi/hibp-downloader/)
[![Python Versions](https://img.shields.io/pypi/pyversions/hibp-downloader.svg)](https://github.com/threatpatrols/hibp-downloader/)
[![build tests](https://github.com/threatpatrols/hibp-downloader/actions/workflows/build-tests.yml/badge.svg)](https://github.com/threatpatrols/hibp-downloader/actions/workflows/build-tests.yml)
[![License](https://img.shields.io/github/license/threatpatrols/hibp-downloader.svg)](https://github.com/threatpatrols/hibp-downloader)

This is a Python implementation of [PwnedPasswordsDownloader](https://github.com/HaveIBeenPwned/PwnedPasswordsDownloader)
that is more download efficient and provides additional useful functionality
 - Automatically **only** download prefix-chunks that have changed since the last download
 - Ability to start, stop and re-start without loss of data already collected
 - Ability to start and stop at named hash positions
 - Per prefix file metadata in JSON format for easy data reuse

## Install
```commandline
pip install --upgrade hibp-downloader
```

## Usage
![screenshot-help.png](https://raw.githubusercontent.com/threatpatrols/hibp-downloader/main/docs/assets/screenshot-help.png)

## Runtime Logs
Sample download activity log
```text
2023-07-31T03:22:45+1000 | INFO | hibp-downloader | prefix=e585f source=[lc:265201 et:0 rc:722148 ro:3 xx:0] runtime_rate=[11.2MBit/s 86req/s ~71005H/s] runtime=2.33hr download=11748.0MB
2023-07-31T03:22:48+1000 | INFO | hibp-downloader | prefix=e5877 source=[lc:265201 et:0 rc:722268 ro:3 xx:0] runtime_rate=[11.2MBit/s 86req/s ~70998H/s] runtime=2.33hr download=11750.0MB
2023-07-31T03:22:50+1000 | INFO | hibp-downloader | prefix=f5837 source=[lc:265201 et:0 rc:722388 ro:3 xx:0] runtime_rate=[11.2MBit/s 86req/s ~70992H/s] runtime=2.33hr download=11751.9MB
```
 - 86 requests per second to api.pwnedpasswords.com
 - 265,201 prefix files from (`lc`) local-cache; 722,388 from (`rc`) remote-cache; 3 from (`ro`) remote-origin; 0 failed (`xx`) download
 - estimated ~70k hash values downloaded per second
 - 11.5GB (11,751MB) downloaded in 2.3 hours

## Source
 - https://github.com/threatpatrols/hibp-downloader

## Issues
 - https://github.com/threatpatrols/hibp-downloader/issues

## Copyright
 - Copyright &copy; 2023 Threat Patrols Pty Ltd &lt;contact@threatpatrols.com&gt;
 - Copyright &copy; 2023 Nicholas de Jong &lt;contact@nicholasdejong.com&gt;

All rights reserved.

## License
 * BSD-3-Clause - see LICENSE file for details.
