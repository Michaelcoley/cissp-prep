#!/usr/bin/env python3
"""Compute the Supabase Storage path for guide.pdf and upload it.

Usage:
    .venv/bin/python upload_guide.py

You'll be prompted for:
  - Your sync passphrase (the same one you set in Stats → Cloud sync)
  - Your Supabase Service Role key (Dashboard → Settings → API → service_role)
    Service Role keys bypass RLS so the upload can happen.

Nothing is persisted. The Service Role key is only used in-memory for the
upload request.
"""
import getpass
import hashlib
import sys
import urllib.request
import urllib.error
from pathlib import Path

SUPABASE_URL = "https://qoxgjjynjialntkvcdqn.supabase.co"
BUCKET = "cissp-resources"
GUIDE = Path("/Users/mike/cissp/guide.pdf")


def sha256_hex(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def main() -> int:
    if not GUIDE.exists():
        print(f"ERROR: {GUIDE} not found.", file=sys.stderr)
        return 1
    size_mib = GUIDE.stat().st_size / 1024 / 1024
    print(f"Found {GUIDE}  ({size_mib:.1f} MiB)")
    print()
    passphrase = getpass.getpass("Sync passphrase (same one you set in the app): ").strip()
    if len(passphrase) < 8:
        print("ERROR: passphrase too short.", file=sys.stderr)
        return 2
    sync_id = sha256_hex(passphrase)
    object_path = f"{sync_id}/guide.pdf"
    public_url = f"{SUPABASE_URL}/storage/v1/object/public/{BUCKET}/{object_path}"
    print()
    print(f"Sync ID hash : {sync_id}")
    print(f"Storage path : {BUCKET}/{object_path}")
    print(f"Public URL   : {public_url}")
    print()
    service_role = getpass.getpass(
        "Service Role key (Supabase Dashboard → Settings → API → service_role; not the publishable key): "
    ).strip()
    if not service_role.startswith(("eyJ", "sb_secret_")):
        print("WARNING: that doesn't look like a Service Role key. Continuing anyway.", file=sys.stderr)

    upload_url = f"{SUPABASE_URL}/storage/v1/object/{BUCKET}/{object_path}"
    print(f"\nUploading to {upload_url} …")

    with GUIDE.open("rb") as f:
        body = f.read()
    req = urllib.request.Request(
        upload_url,
        data=body,
        method="POST",
        headers={
            "apikey": service_role,
            "Authorization": f"Bearer {service_role}",
            "Content-Type": "application/pdf",
            "x-upsert": "true",  # overwrite if path already exists
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            resp = r.read().decode("utf-8", errors="replace")
            print(f"\nUpload OK ({r.status}). Response: {resp[:200]}")
    except urllib.error.HTTPError as e:
        print(f"\nUpload FAILED ({e.code}): {e.read().decode('utf-8', errors='replace')[:400]}")
        return 3
    except Exception as e:
        print(f"\nUpload FAILED: {type(e).__name__}: {e}")
        return 4
    print()
    print("✅ Done. Verify by opening this URL in a browser:")
    print(f"   {public_url}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
