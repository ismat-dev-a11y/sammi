#!/usr/bin/env python3
"""Utility to test all GET-able endpoints defined in the Swagger (OpenAPI) schema.
It fetches the JSON schema from the local dev server and issues a simple GET request
for each path that supports the GET method. The responses (status code and a short
preview of the body) are printed to the console.

Usage:
    python test_swagger_apis.py

This script assumes the dev server is running at http://127.0.0.1:8000.
"""
import json
import sys
import urllib.request
from urllib.error import HTTPError, URLError

BASE_URL = "http://127.0.0.1:8000"
SCHEMA_ENDPOINT = f"{BASE_URL}/api/schema/"

def fetch_schema(url: str) -> dict:
    try:
        with urllib.request.urlopen(url) as resp:
            data = resp.read().decode("utf-8")
            return json.loads(data)
    except (HTTPError, URLError) as e:
        print(f"Failed to download schema: {e}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Invalid JSON received: {e}", file=sys.stderr)
        sys.exit(1)

def test_endpoint(path: str, method: str = "GET") -> None:
    url = f"{BASE_URL}{path}"
    try:
        req = urllib.request.Request(url, method=method)
        with urllib.request.urlopen(req) as resp:
            status = resp.getcode()
            body = resp.read().decode("utf-8", errors="replace")
            preview = body[:200].replace("\n", " ")
            print(f"{method} {path} -> {status} | {preview}")
    except HTTPError as e:
        print(f"{method} {path} -> {e.code} (error)")
    except URLError as e:
        print(f"{method} {path} -> connection error: {e.reason}")

def main():
    schema = fetch_schema(SCHEMA_ENDPOINT)
    paths = schema.get("paths", {})
    for path, ops in paths.items():
        # Prefer GET if available; otherwise try the first method listed.
        if "get" in ops:
            test_endpoint(path, "GET")
        else:
            # fallback to the first declared method (POST, PUT, etc.)
            method = next(iter(ops)).upper()
            test_endpoint(path, method)

if __name__ == "__main__":
    main()
