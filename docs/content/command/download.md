# Download

The `hibp-downloader` CLI tool attempts to be as fast and efficient as Pythonly possible (*see note below).

The downloader works by creating multiple threads (based on CPU cores) that each then create collections of 
async-workers that work in chunks of the hash-prefix address-space.

The downloader collects the content for each hash-prefix in gzip format which makes it possible to write this 
content directly to disk without needing to decompress and recompress anything.  This saves us a _LOT_ of 
compute time and means we can store the content locally and compressed.

The downloader stores a `.meta` file (JSON, you can also use) alongside each content file that tracks the content
timestamps, checksums and ETAG value.

Because the downloader tracks content ETAG values we only receive new content from the remote-source (ie 
`api.pwnedpasswords.com`) when the content has actually changed.  The user is able to override this using 
the `--ignore-etag` option that will force all content to be sent by the source without regard for the ETAG.

The downloader also prevents the user from requesting the same hash-prefix content block more than once per 
local-cache-ttl to prevent unnecessary re-requests for the same content in short time periods (default 12 hrs); use 
the `--local-cache-ttl` option to adjust this if needed.

The `--force` option is simply a convenience option that sets both `--ignore-etag` and `--local-cache-ttl=0`  

The options `--hash-type`, `--first-hash`, `--last-hash`, `--processes` and `--chunk-size` are described in 
the application-help and should be self-evident.

## Usage
![screenshot-help.png](../assets/screenshot-download-help.png)

## Logs
The downloader logs emit information about the download progress, not each requested hash-prefix content 
object.  The following attributes are logged -

 * `prefix=` the current hash prefix content downloaded.
 * `lc=` count of locally-cached content objects that did not require any request.
 * `et=` count of etag-match content objects that did not require re-download from source.
 * `rc=` count of remote-cached content objects that already existed at the edge-cache provider (ie Cloudflare).
 * `ro=` count of remote-origin content objects that needed to be retrieved from origin.
 * `xx=` count of content objects that have unknown remote cache status. 


## That "Note Below"
"As fast as Pythonly possible" famous last words...

The design of the main work loop in `hibp_download.py` uses a `multiprocessing.Pool` that fans out into chunks 
of async-workers.  This means that when a Pool threads finishes its chunk it then has to wait for the threads to 
catch up and rejoin.  The effect is that the downloads slow down, and you can see it happening if you watch long 
enough.

This means it is not quite "as fast as possible" and there is a better design using `multiprocessing.Queues` that 
could be implemented if really needed.  In practice its plenty fast enough for a dataset that generally only 
requires an update a few times a year.
