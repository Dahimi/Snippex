"""
Telemetry writer — stores RequestLog entries to GCS (primary) or a local
JSONL file (fallback when GCS is not configured).

Called as a fire-and-forget BackgroundTask — errors are caught and logged,
never propagated to the caller.
"""

import json
import logging
import os
from datetime import timezone
from pathlib import Path

from telemetry.schema import RequestLog

logger = logging.getLogger(__name__)

# Local fallback path — one JSONL file, one JSON object per line
_LOCAL_LOG_PATH = Path("telemetry_logs.jsonl")


def _gcs_client_and_bucket():
    """Return (storage.Client, bucket_name) or (None, None) if not configured."""
    try:
        from config import settings
        bucket = getattr(settings, "GCS_LOG_BUCKET", None)
        if not bucket:
            return None, None
        from google.cloud import storage  # type: ignore
        return storage.Client(), bucket
    except Exception as exc:
        logger.warning("GCS not available: %s", exc)
        return None, None


def _gcs_object_name(log: RequestLog) -> str:
    dt = log.timestamp.astimezone(timezone.utc)
    return f"requests/{dt.year}/{dt.month:02d}/{dt.day:02d}/{log.request_id}.json"


async def write_log(log: RequestLog) -> None:
    """
    Persist a RequestLog. Tries GCS first; falls back to a local JSONL file.
    Never raises — all errors are swallowed so the API response is unaffected.
    """
    payload = log.model_dump_json(indent=2)

    client, bucket_name = _gcs_client_and_bucket()
    if client and bucket_name:
        try:
            blob_name = _gcs_object_name(log)
            bucket = client.bucket(bucket_name)
            blob = bucket.blob(blob_name)
            blob.upload_from_string(payload, content_type="application/json")
            logger.debug("Telemetry written to gs://%s/%s", bucket_name, blob_name)
            return
        except Exception as exc:
            logger.warning("GCS write failed, falling back to local: %s", exc)

    # Local fallback
    try
        with _LOCAL_LOG_PATH.open("a", encoding="utf-8") as f:
            f.write(log.model_dump_json() + "\n")
        logger.debug("Telemetry written locally to %s", _LOCAL_LOG_PATH)
    except Exception as exc:
        logger.error("Local telemetry write also failed: %s", exc)
