"""
upload_to_onshape.py — Upload LUCKY BANDIT v4.3 STEP file to Onshape
=====================================================================
Standalone script that uses the Onshape REST API with API-key (HMAC)
authentication to:
  1. Create a new Onshape document
  2. Upload the STEP file into it

Prerequisites:
  pip install requests

Usage:
  python upload_to_onshape.py                          # uses defaults
  python upload_to_onshape.py --step path/to/file.step # custom path

Environment variables (or put them in a .env file next to this script):
  ONSHAPE_ACCESS_KEY=<your access key>
  ONSHAPE_SECRET_KEY=<your secret key>

Get your API keys at: https://dev-portal.onshape.com/keys
"""

import os
import sys
import hmac
import hashlib
import base64
import uuid
import datetime
import argparse

try:
    import requests
except ImportError:
    sys.exit("ERROR: 'requests' is required.  Install with:  pip install requests")

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
BASE_URL = "https://cad.onshape.com"
API_VERSION = "/api/v6"
DOC_NAME = "LUCKY BANDIT v4.3 — Pressure Vessel"

# Default STEP path (next to this script)
DEFAULT_STEP = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                            "lucky_bandit_v43.step")


# ---------------------------------------------------------------------------
# Load .env helper (minimal, no extra deps)
# ---------------------------------------------------------------------------
def _load_dotenv():
    """Load a .env file beside this script if it exists."""
    env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
    if not os.path.isfile(env_path):
        return
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, val = line.split("=", 1)
            os.environ.setdefault(key.strip(), val.strip())


_load_dotenv()

ACCESS_KEY = os.environ.get("ONSHAPE_ACCESS_KEY", "")
SECRET_KEY = os.environ.get("ONSHAPE_SECRET_KEY", "")


# ---------------------------------------------------------------------------
# Onshape HMAC-SHA256 authentication
# ---------------------------------------------------------------------------
def _make_auth_headers(method: str, path: str, query: str = "",
                       content_type: str = "application/json") -> dict:
    """Build Onshape On-Nonce / Date / Authorization headers."""
    nonce = uuid.uuid4().hex
    date = datetime.datetime.now(datetime.timezone.utc).strftime(
        "%a, %d %b %Y %H:%M:%S GMT"
    )

    # String to sign — each part lowercased, joined by newlines
    string_to_sign = "\n".join([
        method.lower(),
        content_type.lower(),
        nonce.lower(),
        date.lower(),
        path.lower(),
        query.lower(),
    ])

    # HMAC-SHA256 signature
    secret_bytes = SECRET_KEY.encode("utf-8")
    signature = hmac.new(
        secret_bytes,
        string_to_sign.encode("utf-8"),
        hashlib.sha256,
    ).digest()
    sig_b64 = base64.b64encode(signature).decode("utf-8")

    return {
        "Date": date,
        "On-Nonce": nonce,
        "Authorization": f"On {ACCESS_KEY}:HmacSHA256:{sig_b64}",
        "Accept": "application/json",
    }


# ---------------------------------------------------------------------------
# API calls
# ---------------------------------------------------------------------------
def create_document(name: str) -> dict:
    """Create a new Onshape document. Returns JSON with 'id' and
    'defaultWorkspace.id'."""
    path = f"{API_VERSION}/documents"
    url = f"{BASE_URL}{path}"
    ct = "application/json"

    headers = _make_auth_headers("POST", path, content_type=ct)
    headers["Content-Type"] = ct

    resp = requests.post(url, headers=headers, json={
        "name": name,
        "isPublic": False,
    })
    resp.raise_for_status()
    return resp.json()


def upload_step(did: str, wid: str, step_path: str) -> dict:
    """Upload a STEP file into an existing document/workspace.
    Uses the blobelements endpoint which auto-translates on import."""
    path = f"{API_VERSION}/blobelements/d/{did}/w/{wid}"
    url = f"{BASE_URL}{path}"

    filename = os.path.basename(step_path)

    # For multipart uploads, requests generates the Content-Type with boundary.
    # We sign with a placeholder; Onshape is lenient on multipart CT matching.
    ct = "application/json"  # signing content-type (Onshape ignores boundary in sig)

    headers = _make_auth_headers("POST", path, content_type=ct)
    # Remove Content-Type so requests can set multipart boundary itself
    headers.pop("Content-Type", None)

    with open(step_path, "rb") as f:
        files = {
            "file": (filename, f, "application/octet-stream"),
        }
        data = {
            "encodedFilename": filename,
            "formatName": "STEP",
            "flattenAssemblies": "true",
            "createComposite": "false",
        }
        resp = requests.post(url, headers=headers, files=files, data=data)

    resp.raise_for_status()
    return resp.json()


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(
        description="Upload a STEP file to Onshape"
    )
    parser.add_argument(
        "--step", default=DEFAULT_STEP,
        help="Path to the STEP file (default: lucky_bandit_v43.step)"
    )
    parser.add_argument(
        "--name", default=DOC_NAME,
        help="Onshape document name"
    )
    args = parser.parse_args()

    # Validate keys
    if not ACCESS_KEY or not SECRET_KEY:
        sys.exit(
            "ERROR: Set ONSHAPE_ACCESS_KEY and ONSHAPE_SECRET_KEY as\n"
            "environment variables or in a .env file next to this script.\n"
            "Get keys at: https://dev-portal.onshape.com/keys"
        )

    # Validate STEP file
    if not os.path.isfile(args.step):
        sys.exit(
            f"ERROR: STEP file not found: {args.step}\n"
            f"Run  python lucky_bandit_v43.py  first to generate it."
        )

    step_size = os.path.getsize(args.step)
    print(f"STEP file : {args.step}  ({step_size / 1024:.0f} KB)")

    # 1. Create document
    print(f"Creating Onshape document: '{args.name}' ...")
    doc = create_document(args.name)
    did = doc["id"]
    wid = doc["defaultWorkspace"]["id"]
    print(f"  Document ID : {did}")
    print(f"  Workspace ID: {wid}")

    # 2. Upload STEP
    print("Uploading STEP file ...")
    result = upload_step(did, wid, args.step)
    print("  Upload complete!")

    # 3. Print link
    doc_url = f"https://cad.onshape.com/documents/{did}/w/{wid}"
    print(f"\nOpen in Onshape:\n  {doc_url}\n")
    print("The STEP import may take a moment to translate in Onshape.")


if __name__ == "__main__":
    main()
