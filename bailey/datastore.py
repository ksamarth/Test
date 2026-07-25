"""Anonymized benchmark capture — the seed of Bailey's proprietary dataset.

Every completed analysis is distilled into a structured, de-identified record
and appended to an append-only JSONL log. We deliberately never store the
uploaded file or its raw text — only the extracted terms and benchmarks, which
is what powers market benchmarking while keeping the "we don't keep your
contract" promise. Swap the JSONL sink for a database (Postgres) when ready;
the record shape is already the table schema.
"""

import json
import os
import time
import uuid
from pathlib import Path

DATA_DIR = Path(os.environ.get("BAILEY_DATA_DIR", Path(__file__).parent / "data"))
RECORDS = DATA_DIR / "benchmark_records.jsonl"

# Only these questionnaire fields are retained — all coarse buckets, never free
# text or anything identifying. (career stage, area ties, debt band, plans, priority)
_PROFILE_KEYS = ("stage", "ties", "debt", "plans", "priority")


def _as_dict(analysis) -> dict:
    if hasattr(analysis, "model_dump"):
        return analysis.model_dump(mode="json")
    return dict(analysis)


def record_analysis(analysis, profile: dict | None = None, source: str = "upload") -> str | None:
    """Best-effort: append one de-identified benchmark record. Never raises.

    Note what is intentionally absent: the raw contract, its text, the employer
    name, and any user identity. What remains is the shape of the *offer* — the
    benchmark signal — plus optional coarse reader context.
    """
    try:
        a = _as_dict(analysis)
        x = a.get("extraction", {}) or {}
        comp = x.get("compensation", {}) or {}
        rc = x.get("restrictive_covenants", {}) or {}
        ben = x.get("benefits", {}) or {}
        score = a.get("score", {}) or {}
        flags = a.get("red_flags") or []

        rec = {
            "id": uuid.uuid4().hex,
            "ts": int(time.time()),
            "source": source,
            "profession": x.get("profession"),
            "practice_type": x.get("practice_type"),
            "location": x.get("location"),          # city/region — regional benchmark signal, not user PII
            "employment_status": x.get("employment_status"),
            "grade": score.get("grade"),
            "overall": score.get("overall"),
            "category_scores": {c.get("category"): c.get("score") for c in (score.get("categories") or [])},
            "compensation": {
                "basis": comp.get("compensation_basis"),
                "production_percentage": comp.get("production_percentage"),
                "daily_guarantee": comp.get("daily_guarantee"),
                "guarantee_duration_months": comp.get("guarantee_duration_months"),
                "base_salary_annual": comp.get("base_salary_annual"),
                "sign_on_bonus": comp.get("sign_on_bonus"),
            },
            "restrictive_covenants": {
                "non_compete_radius_miles": rc.get("non_compete_radius_miles"),
                "non_compete_duration_months": rc.get("non_compete_duration_months"),
            },
            "benefits": {
                "malpractice_type": ben.get("malpractice_type"),
                "pto": ben.get("pto"),
            },
            "red_flag_count": len(flags),
            "high_severity_flags": sum(1 for f in flags if f.get("severity") == "high"),
            "market_verdicts": {b.get("term"): b.get("verdict") for b in (a.get("market_comparison") or [])},
            "profile": ({k: profile.get(k) for k in _PROFILE_KEYS if profile.get(k)} or None) if profile else None,
        }

        DATA_DIR.mkdir(parents=True, exist_ok=True)
        with RECORDS.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
        return rec["id"]
    except Exception:
        # Capture is never allowed to break a user's review.
        return None
