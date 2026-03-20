#!/usr/bin/env python
"""
Utility to verify factual claims before stating them.

Usage:
    python verify_claim.py file-exists path/to/file
    python verify_claim.py file-contains path/to/file "text"
    python verify_claim.py command "command here"
    python verify_claim.py http-url http://localhost:8000/health
"""

import sys
import os
import subprocess
import urllib.request
import urllib.error


def verify_file_exists(path):
    """Verify a file exists."""
    if os.path.exists(path):
        print(f"✓ File exists: {path}")
        return True
    else:
        print(f"✗ File does NOT exist: {path}")
        return False


def verify_file_contains(path, text):
    """Verify a file contains specific text."""
    if not os.path.exists(path):
        print(f"✗ File does NOT exist: {path}")
        return False
    
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    if text in content:
        print(f"✓ File contains '{text}': {path}")
        return True
    else:
        print(f"✗ File does NOT contain '{text}': {path}")
        # Show actual content for verification
        print(f"\nActual content:\n{content[:500]}")
        return False


def verify_command(cmd):
    """Verify a command runs successfully."""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print(f"✓ Command succeeded: {cmd}")
            if result.stdout:
                print(f"  stdout: {result.stdout[:200]}")
            return True
        else:
            print(f"✗ Command failed (exit {result.returncode}): {cmd}")
            if result.stderr:
                print(f"  stderr: {result.stderr[:200]}")
            return False
    except Exception as e:
        print(f"✗ Command error: {cmd}")
        print(f"  exception: {e}")
        return False


def verify_http_url(url):
    """Verify an HTTP URL is accessible."""
    try:
        response = urllib.request.urlopen(url, timeout=5)
        print(f"✓ HTTP URL accessible: {url}")
        print(f"  Status: {response.status}")
        return True
    except urllib.error.URLError as e:
        print(f"✗ HTTP URL NOT accessible: {url}")
        print(f"  Error: {e}")
        return False
    except Exception as e:
        print(f"✗ HTTP URL error: {url}")
        print(f"  Exception: {e}")
        return False


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)
    
    mode = sys.argv[1]
    
    if mode == "file-exists":
        success = verify_file_exists(sys.argv[2])
    elif mode == "file-contains":
        success = verify_file_contains(sys.argv[2], sys.argv[3])
    elif mode == "command":
        success = verify_command(sys.argv[2])
    elif mode == "http-url":
        success = verify_http_url(sys.argv[2])
    else:
        print(f"Unknown mode: {mode}")
        sys.exit(1)
    
    sys.exit(0 if success else 1)
