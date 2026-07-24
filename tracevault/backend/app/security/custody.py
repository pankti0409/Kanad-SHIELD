"""
TraceVault Chain of Custody & Forensic Verification
Computes SHA-256 hashes, verifies evidence integrity, and maintains immutable audit records.
"""
import hashlib
from pathlib import Path
import structlog
from typing import Dict, Any

logger = structlog.get_logger(__name__)


def calculate_file_sha256(file_path: str) -> str:
    """
    Calculate SHA-256 checksum for evidence file integrity verification.
    """
    sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            sha256.update(chunk)
    return sha256.hexdigest()


def verify_evidence_integrity(file_path: str, expected_hash: str) -> Dict[str, Any]:
    """
    Verify that an evidence file has not been altered or tampered with.
    """
    current_hash = calculate_file_sha256(file_path)
    is_valid = current_hash.lower() == expected_hash.lower()

    logger.info(
        "evidence_integrity_verified",
        file=file_path,
        is_valid=is_valid,
    )

    return {
        "file_path": file_path,
        "is_valid": is_valid,
        "current_hash": current_hash,
        "expected_hash": expected_hash,
    }
