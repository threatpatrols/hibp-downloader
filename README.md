# hibp-downloader

[![pypi](https://img.shields.io/pypi/v/hibp-downloader.svg)](https://pypi.python.org/pypi/hibp-downloader/)
[![python](https://img.shields.io/pypi/pyversions/hibp-downloader.svg)](https://github.com/threatpatrols/hibp-downloader/)
[![build tests](https://github.com/threatpatrols/hibp-downloader/actions/workflows/build-tests.yml/badge.svg)](https://github.com/threatpatrols/hibp-downloader/actions/workflows/build-tests.yml)
[![docs](https://img.shields.io/readthedocs/hibp-downloader)](https://hibp-downloader.readthedocs.io)
[![license](https://img.shields.io/github/license/threatpatrols/hibp-downloader.svg)](https://github.com/threatpatrols/hibp-downloader)

This is a CLI tool to efficiently download a local copy of the pwned password hash data from the very awesome
[HIBP](https://haveibeenpwned.com/Passwords) pwned passwords [api-endpoint](https://api.pwnedpasswords.com) using all the good bits;
multiprocessing, async-processes, local-caching, content-etags and http2-connection pooling to make things as fast 
as is Pythonly possible.

## Features

 - Easily resume interrupted `download` operations into a `--data-path` without re-clobbering api-source.
 - Only download hash-prefix content blocks when the source content has changed (via content ETAG values); thus making 
   it easy to periodically re-sync when needed.
 - Ability to directly `query` for compromised password values from the data in-place; efficient enough to attach a 
   service with reasonable loads.
 - Ability to generate a single text file with in-order pwned password hash values, similar to [PwnedPasswordsDownloader](https://github.com/HaveIBeenPwned/PwnedPasswordsDownloader) from the HIBP team.
 - Per prefix file metadata in JSON format for easy data reuse by other tooling if required.

## Install
```commandline
pip install --upgrade hibp-downloader
```

## Usage
![screenshot-help.png](https://raw.githubusercontent.com/threatpatrols/hibp-downloader/main/docs/content/assets/screenshot-help.png)

## Performance
Sample download activity log; host with 12 cores on 45Mbit/s DSL connection. 
```text
2023-11-12T21:25:08+1000 | INFO | hibp-downloader | prefix=00ec3 source=[lc:10 et:2 rc:3800 ro:0 xx:0] processed=[62.0MB ~43589H/s] api=[105req/s 60.0MB] runtime=1.2min
2023-11-12T21:25:09+1000 | INFO | hibp-downloader | prefix=00eff source=[lc:10 et:2 rc:3850 ro:0 xx:0] processed=[62.8MB ~43547H/s] api=[105req/s 60.8MB] runtime=1.2min
2023-11-12T21:25:10+1000 | INFO | hibp-downloader | prefix=00f3b source=[lc:10 et:2 rc:3900 ro:0 xx:0] processed=[63.7MB ~43528H/s] api=[105req/s 61.7MB] runtime=1.2min
2023-11-12T21:25:11+1000 | INFO | hibp-downloader | prefix=00f6d source=[lc:10 et:2 rc:3950 ro:0 xx:0] processed=[64.5MB ~43541H/s] api=[105req/s 62.5MB] runtime=1.3min
```

 - 105x requests per second to `api.pwnedpasswords.com`
 - Log sources are shorthand:
     - `lc`: 10x prefix files from local-cache
     - `et`: 2x etag-match responses
     - `rc`: 3950x from remote-cache
     - `ro`: 0x from remote-origin
     - `xx`: 0x failed download
 - 62MB downloaded in ~75 seconds
 - Approx ~43k hash values per second

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
