# hibp-downloader

[![pypi](https://img.shields.io/pypi/v/hibp-downloader.svg)](https://pypi.python.org/pypi/hibp-downloader/)
[![python](https://img.shields.io/pypi/pyversions/hibp-downloader.svg)](https://github.com/threatpatrols/hibp-downloader/)
[![build tests](https://github.com/threatpatrols/hibp-downloader/actions/workflows/build-tests.yml/badge.svg)](https://github.com/threatpatrols/hibp-downloader/actions/workflows/build-tests.yml)
[![docs](https://img.shields.io/readthedocs/hibp-downloader)](https://hibp-downloader.readthedocs.io)
[![license](https://img.shields.io/github/license/threatpatrols/hibp-downloader.svg)](https://github.com/threatpatrols/hibp-downloader)

This is a CLI tool to efficiently download a local copy of the pwned password hash data from the very awesome
[HIBP](https://haveibeenpwned.com/Passwords) pwned passwords [api-endpoint](https://api.pwnedpasswords.com) using 
multiprocessing, async-processes, local-caching, content-etags and http2-connection pooling to make things as fast 
as (seems) Pythonly possible.

## Features

 - Only download hash-prefix content blocks when the hash-prefix block content has changed (via content ETAG values).
 - Start, stop and re-start the data-collection process without loss of data already collected.
 - Ability to query clear text values and return results from the pwned password data set.
 - Generate a single text file with pwned password hash values in-order, similar to [PwnedPasswordsDownloader](https://github.com/HaveIBeenPwned/PwnedPasswordsDownloader) from the HIBP team.
 - Per prefix file metadata in JSON format for easy data reuse.

## Install
```commandline
pip install --upgrade hibp-downloader
```

## Usage
![screenshot-help.png](https://raw.githubusercontent.com/threatpatrols/hibp-downloader/main/docs/content/assets/screenshot-help.png)

## Performance
Sample download activity log; host with 12 cores on 45Mbit/s DSL connection. 
```text
2023-07-31T03:22:45+1000 | INFO | hibp-downloader | prefix=e585f source=[lc:265201 et:0 rc:722148 ro:3 xx:0] runtime_rate=[11.2MBit/s 86req/s ~71005H/s] runtime=2.33hr download=11748.0MB
2023-07-31T03:22:48+1000 | INFO | hibp-downloader | prefix=e5877 source=[lc:265201 et:0 rc:722268 ro:3 xx:0] runtime_rate=[11.2MBit/s 86req/s ~70998H/s] runtime=2.33hr download=11750.0MB
2023-07-31T03:22:50+1000 | INFO | hibp-downloader | prefix=f5837 source=[lc:265201 et:0 rc:722388 ro:3 xx:0] runtime_rate=[11.2MBit/s 86req/s ~70992H/s] runtime=2.33hr download=11751.9MB
```

 - 86 requests per second to `api.pwnedpasswords.com`
 - 265,201 prefix files from (`lc`) local-cache; 722,388 from (`rc`) remote-cache; 3 from (`ro`) remote-origin; 0 failed (`xx`) download
 - estimated ~70k hash values downloaded per second
 - 11.5GB (11,751MB) downloaded in 2.3 hours (full dataset is ~3.5 hours)

## Project

 - Github - [github.com/threatpatrols/hibp-downloader](https://github.com/threatpatrols/hibp-downloader)
 - PyPI - [pypi.org/project/hibp-downloader/](https://pypi.org/project/hibp-downloader/)
 - ReadTheDocs - [hibp-downloader.readthedocs.io](https://hibp-downloader.readthedocs.io)

## Copyright
 - Copyright &copy; 2023 [Threat Patrols Pty Ltd](https://www.threatpatrols.com)
 - Copyright &copy; 2023 [Nicholas de Jong](https://www.nicholasdejong.com)

All rights reserved.

## License
 * BSD-3-Clause - see LICENSE file for details.
