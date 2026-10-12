"""
SIVACINE AI — Supabase Storage Service.

Uploads generated scripts directly as JSON files into Supabase Storage buckets.
Stateless and async using httpx.
"""

import json
import logging
import uuid
import datetime
import re
from typing import Optional, Dict, Any, Tuple

import httpx

from ..config import settings

logger = logging.getLogger(__name__)


class SupabaseStorageService:
    """Uploads JSON scripts directly to Supabase Storage."""

    @classmethod
    async def upload_script_json(
        cls,
        script_dict: Dict[str, Any],
        custom_filename: Optional[str] = None
    ) -> Tuple[Optional[str], Optional[str]]:
        """
        Uploads a generated script as a .json file to Supabase Storage.

        Returns:
            Tuple of (storage_url, storage_path)
            If Supabase is not configured or upload fails, returns (None, None).
        """
        supabase_url = (settings.SUPABASE_URL or "").strip().rstrip("/")
        supabase_key = (settings.SUPABASE_KEY or "").strip()
        bucket = (settings.SUPABASE_SCRIPTS_BUCKET or "scripts").strip()

        if not supabase_url or not supabase_key:
            logger.info("Supabase storage not configured (SUPABASE_URL / SUPABASE_KEY empty). Skipping cloud upload.")
            return None, None

        # Structure path: Date / Time / Title.json
        # Example: 2026-10-12 / 16-25-30 / The_Ignited_Forge.json
        now = datetime.datetime.now()
        date_folder = now.strftime("%Y-%m-%d")
        time_folder = now.strftime("%H-%M-%S")

        raw_title = script_dict.get("title", "Untitled_Script").strip()
        safe_title = re.sub(r'[^a-zA-Z0-9_\-]', '', raw_title.replace(' ', '_'))
        if not safe_title:
            safe_title = "Untitled_Script"

        filename = custom_filename or f"{date_folder}/{time_folder}/{safe_title}.json"
        
        # Serialize to formatted JSON bytes
        json_bytes = json.dumps(script_dict, indent=2, ensure_ascii=False).encode("utf-8")

        headers = {
            "Authorization": f"Bearer {supabase_key}",
            "apiKey": supabase_key,
            "Content-Type": "application/json",
            "x-upsert": "true",
        }

        upload_url = f"{supabase_url}/storage/v1/object/{bucket}/{filename}"

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                # 1. Ensure bucket exists (or try to create it if it doesn't)
                try:
                    bucket_create_url = f"{supabase_url}/storage/v1/bucket"
                    bucket_payload = {"id": bucket, "name": bucket, "public": True}
                    await client.post(bucket_create_url, json=bucket_payload, headers=headers)
                except Exception:
                    # Bucket may already exist; proceed with upload
                    pass

                # 2. Upload file
                resp = await client.post(upload_url, content=json_bytes, headers=headers)

                if resp.status_code in (200, 201):
                    public_url = f"{supabase_url}/storage/v1/object/public/{bucket}/{filename}"
                    logger.info(f"Successfully uploaded script to Supabase Storage: {public_url}")
                    return public_url, f"{bucket}/{filename}"
                else:
                    logger.warning(
                        f"Supabase storage upload returned HTTP {resp.status_code}: {resp.text}"
                    )
                    return None, None

        except Exception as exc:
            logger.error(f"Error uploading script to Supabase Storage: {exc}")
            return None, None
