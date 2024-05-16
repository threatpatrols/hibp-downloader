# hibp-downloader

[![pypi](https://img.shields.io/pypi/v/hibp-downloader.svg)](https://pypi.python.org/pypi/hibp-downloader/)
[![python](https://img.shields.io/pypi/pyversions/hibp-downloader.svg)](https://github.com/threatpatrols/hibp-downloader/)
[![build tests](https://github.com/threatpatrols/hibp-downloader/actions/workflows/build-tests.yml/badge.svg)](https://github.com/threatpatrols/hibp-downloader/actions/workflows/build-tests.yml)
[![docs](https://img.shields.io/readthedocs/hibp-downloader)](https://hibp-downloader.readthedocs.io)
[![license](https://img.shields.io/github/license/threatpatrols/hibp-downloader.svg)](https://github.com/threatpatrols/hibp-downloader)

This is a CLI tool to efficiently download a local copy of the pwned password hash data from the very awesome
[HIBP](https://haveibeenpwned.com/Passwords) pwned passwords [api-endpoint](https://api.pwnedpasswords.com) using all the good bits;
multiprocessing, async-processes, local-caching, content-etags and http2-connection pooling to probably make things 
as fast as is Pythonly possible.

## Features
 - Interface to directly `query` for compromised password values from the *compressed* file data-store!
 - Download and store acquired data in gzip'd compressed to save on storage and speed up queries. 
 - Download the full dataset in under 45 mins (generally CPU bound)
 - Easily resume interrupted `download` operations into a `--data-path` without re-clobbering api-source.
 - Only download hash-prefix content blocks when the source content has changed (via content ETAG values); making it 
   easy to periodically sync-up when needed.
 - Query interface performance is efficient enough to attach a user web-service with reasonable loads (ie don't waste 
   your own resources decompressing the dataset and storing in a database!)
 - Ability to generate a single text file with in-order pwned password hash values, similar to [PwnedPasswordsDownloader](https://github.com/HaveIBeenPwned/PwnedPasswordsDownloader) from 
   the awesome HIBP team.
 - Per prefix file metadata in JSON format for easy data reuse by other tooling if required.

## Install
```commandline
pipx install hibp-downloader
```

## Usage (download)
![screenshot-help.png](https://raw.githubusercontent.com/threatpatrols/hibp-downloader/main/docs/content/assets/screenshot-help.png)

## Performance
Sample download activity log; host with 32 cores on 500Mbit/s connection. 
```text
...
2024-05-16T10:18:01-0400 | INFO | hibp-downloader | prefix=f80c7 source=[lc:13616 et:3 rc:1002358 ro:25 xx:1] processed=[17836.6MB ~414462H/s] api=[918req/s 17597.4MB] runtime=36.4min
2024-05-16T10:18:02-0400 | INFO | hibp-downloader | prefix=f81af source=[lc:13616 et:3 rc:1002558 ro:25 xx:1] processed=[17840.1MB ~414454H/s] api=[918req/s 17600.9MB] runtime=36.4min
2024-05-16T10:18:02-0400 | INFO | hibp-downloader | prefix=f826f source=[lc:13616 et:3 rc:1002758 ro:25 xx:1] processed=[17843.6MB ~414454H/s] api=[918req/s 17604.4MB] runtime=36.4min
2024-05-16T10:18:03-0400 | INFO | hibp-downloader | prefix=f833f source=[lc:13616 et:3 rc:1002958 ro:25 xx:1] processed=[17847.1MB ~414450H/s] api=[918req/s 17607.9MB] runtime=36.4min
```

 - 918x requests per second to `api.pwnedpasswords.com`
 - Log sources are shorthand:
     - `lc`: 13616 from local-cache (lc) - request-responses handled locally without hitting the network. 
     - `et`: 3 etag-matched (et) - request-responses that confirmed our local data was up-to-date and did not require a new download.
     - `rc`: 1002958 from remote-cache (rc) - request-responses that were downloaded to local, but came from the remote-server cache.
     - `ro`: 25 from remote-origin (ro) - request-responses that were downloaded to local, and the download needed to be fetched from remote origin source.
     - `xx`: 1 failed responses - request-responses that failed (and successfully retried).
 - ~17GB downloaded in ~36 minutes (full dataset)
 - Approx ~414k hash values received per second
 - Processing in this example appears to be CPU bound, measured traffic around ~160 Mbit/s.

## Usage (query)
![screenshot-help.png](https://raw.githubusercontent.com/threatpatrols/hibp-downloader/main/docs/content/assets/screenshot-query-help.png)

## Project

 - Github - [github.com/threatpatrols/hibp-downloader](https://github.com/threatpatrols/hibp-downloader)
 - PyPI - [pypi.org/project/hibp-downloader/](https://pypi.org/project/hibp-downloader/)
 - ReadTheDocs - [hibp-downloader.readthedocs.io](https://hibp-downloader.readthedocs.io)

## Copyright
 - Copyright &copy; 2023-2024 [Threat Patrols Pty Ltd](https://www.threatpatrols.com)
 - Copyright &copy; 2023-2024 [Nicholas de Jong](https://www.nicholasdejong.com)

All rights reserved.

## License
 * BSD-3-Clause - see LICENSE file for details.
