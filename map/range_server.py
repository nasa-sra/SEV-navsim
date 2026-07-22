"""
A tiny static file server that actually supports HTTP Range requests.
Needed because Python's built-in `http.server` ignores the Range header
and always returns the full file with 200 OK, which breaks PMTiles
(which relies on 206 Partial Content responses to read byte ranges
out of a large archive without downloading the whole thing).

Usage:
    python range_server.py [port]
"""

import http.server
import os
import re
import sys
from urllib.parse import unquote


class RangeRequestHandler(http.server.SimpleHTTPRequestHandler):
    def send_head(self):
        path = self.translate_path(self.path)

        if os.path.isdir(path):
            return super().send_head()

        if not os.path.exists(path):
            self.send_error(404, "File not found")
            return None

        file_size = os.path.getsize(path)
        range_header = self.headers.get("Range")

        if range_header is None:
            # behave like a normal server if no range requested
            f = open(path, "rb")
            self.send_response(200)
            self.send_header("Content-type", self.guess_type(path))
            self.send_header("Content-Length", str(file_size))
            self.send_header("Accept-Ranges", "bytes")
            self.end_headers()
            return f

        # Parse "Range: bytes=START-END"
        match = re.match(r"bytes=(\d*)-(\d*)", range_header)
        if not match:
            self.send_error(416, "Invalid Range header")
            return None

        start_str, end_str = match.groups()
        if start_str == "" and end_str == "":
            self.send_error(416, "Invalid Range header")
            return None

        if start_str == "":
            # suffix range: last N bytes
            length = int(end_str)
            start = max(file_size - length, 0)
            end = file_size - 1
        else:
            start = int(start_str)
            end = int(end_str) if end_str != "" else file_size - 1

        if start >= file_size or end >= file_size or start > end:
            self.send_response(416)
            self.send_header("Content-Range", f"bytes */{file_size}")
            self.end_headers()
            return None

        length = end - start + 1

        f = open(path, "rb")
        f.seek(start)

        self.send_response(206)
        self.send_header("Content-type", self.guess_type(path))
        self.send_header("Content-Length", str(length))
        self.send_header("Content-Range", f"bytes {start}-{end}/{file_size}")
        self.send_header("Accept-Ranges", "bytes")
        self.end_headers()

        self._range_start = start
        self._range_length = length
        return f

    def copyfile(self, source, outputfile):
        if hasattr(self, "_range_length"):
            remaining = self._range_length
            buf_size = 64 * 1024
            while remaining > 0:
                chunk = source.read(min(buf_size, remaining))
                if not chunk:
                    break
                outputfile.write(chunk)
                remaining -= len(chunk)
        else:
            super().copyfile(source, outputfile)

    def guess_type(self, path):
        if path.endswith(".pmtiles"):
            return "application/octet-stream"
        return super().guess_type(path)


def run(port=8000):
    handler = RangeRequestHandler
    with http.server.ThreadingHTTPServer(("0.0.0.0", port), handler) as httpd:
        print(f"Serving {os.getcwd()} at http://localhost:{port} (Range requests supported)")
        httpd.serve_forever()


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    run(port)