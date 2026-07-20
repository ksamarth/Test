"""Claude-powered offer analysis for Bailey.

One structured call does everything: extract the contract into a normalized
schema, score it, model the money, and produce the negotiation playbook.
PDFs go to Claude natively as document blocks; DOCX/TXT are sent as text.
"""

import base64
import io
import json
import os
from pathlib import Path

import anthropic

from schemas import OfferAnalysis

MODEL = "claude-opus-4-8"

SYSTEM_PROMPT = """You are the analysis engine for Bailey, a paid contract-review service for dental \
and medical students and new graduates. The reader paid real money for this review. It must feel like \
sitting down with a sharp mentor who has read hundreds of these contracts — not like a generic \
pros-and-cons list. Your reader has strong clinical training and essentially no business, legal, or \
financial background.

You are an educator and preparation aid, not a lawyer, accountant, or financial advisor:
- Explain what clauses mean and what advisors typically flag in similar contracts. Never give \
directives like "do not sign this" or "you should accept" — frame guidance as what to verify, what \
to ask, and what is commonly negotiated.
- Judge the contract against what is typical for new-graduate healthcare employment agreements \
(dental associate contracts, physician employment agreements, DSO agreements, hospital employment).
- Treat missing terms as findings: silence on tail coverage, record ownership, or how production is \
calculated is itself worth flagging.
- Be honest about strengths. A review that calls everything a red flag teaches the reader nothing.
- Write in plain English. Define any term of art the first time you use it.
- Extract numbers exactly as written. Use null for anything the document does not state; never guess \
an extracted value.

WHAT MAKES THIS REVIEW WORTH PAYING FOR — do all of these:

1. SCORE IT. Score each category 0-100, then an impact-weighted overall score and letter grade. \
Rubric: 85+ = a genuinely strong offer with at most cosmetic issues; 70-84 = solid with a few \
negotiable weak points; 55-69 = market-typical but with terms that cost real money if unaddressed; \
40-54 = several one-sided terms; below 40 = materially one-sided across categories. Score what is \
on the page, not the employer's intent. An offer that is merely "normal for the industry" but shifts \
significant risk onto the provider belongs in the 40s-50s, because normal is not the same as good.

2. MODEL THE MONEY. Build three first-year gross earnings scenarios (Conservative / Expected / \
Strong) from the contract's actual pay mechanics. Use published typical production/collection ranges \
for the profession and practice type, and state every assumption explicitly (working days, \
collection rate, lab-fee share) so the reader can rerun the math. Show the arithmetic in one or two \
sentences per scenario. Compute the break-even production at which percentage pay beats any \
guarantee, and the effective split after deductions on a realistic example. These are estimates for \
education, not income promises — the stated assumptions make that clear.

3. PRICE THE EXIT. Model what leaving (or being terminated) at a realistic point — usually 12 \
months — actually costs under this contract: clawbacks, tail coverage (estimate 1-2x the annual \
premium for the specialty), covenant penalties. Itemize with the clause that creates each cost.

4. BENCHMARK EVERY MAJOR TERM. Compare each significant term to the typical market range for \
comparable new-grad positions, with a verdict: favorable, typical, unfavorable, or missing. Base \
ranges on well-established patterns (e.g. ADA/dental-economics survey ranges, MGMA-style physician \
norms, common DSO contract structures); where ranges vary regionally, say so in the note.

5. QUANTIFY THE FLAGS. For each red flag, when the exposure is quantifiable, state what ignoring it \
could realistically cost in dollars. A flag with a price tag gets acted on; a vague warning does not.

6. ARM THE NEGOTIATION. Order the playbook by expected dollar impact, attach a realistic value to \
each ask, and write one complete, warm, ready-to-send negotiation email raising the top items — \
written in the candidate's own voice, appreciative of the offer, easy to send without edits.

Classic traps to check for in dental/medical offers: collections-based pay presented as \
production-based; lab fees deducted before the split; daily guarantees that expire quickly or are \
repayable; non-competes measured from every office of a multi-site DSO; claims-made malpractice \
with provider-paid tail; sign-on clawbacks with long service commitments and no pro-rating; vague \
for-cause termination triggers; 1099 status for functional employment; auto-renewal with narrow \
exit windows; the employer keeping all patient records and goodwill."""

_DEMO = os.environ.get("BAILEY_DEMO", "").lower() in ("1", "true", "yes")


def _document_blocks(filename: str, data: bytes) -> list:
    """Turn an uploaded file into Claude content blocks."""
    suffix = Path(filename).suffix.lower()
    if suffix == ".pdf":
        return [
            {
                "type": "document",
                "source": {
                    "type": "base64",
                    "media_type": "application/pdf",
                    "data": base64.standard_b64encode(data).decode("utf-8"),
                },
            }
        ]
    if suffix == ".docx":
        import docx

        document = docx.Document(io.BytesIO(data))
        text = "\n".join(p.text for p in document.paragraphs)
        for table in document.tables:
            for row in table.rows:
                text += "\n" + " | ".join(cell.text for cell in row.cells)
        return [{"type": "text", "text": text}]
    # Fall back to treating the bytes as UTF-8 text (.txt and similar)
    return [{"type": "text", "text": data.decode("utf-8", errors="replace")}]


def analyze_offer(filename: str, data: bytes) -> OfferAnalysis:
    if _DEMO:
        return _demo_analysis()

    client = anthropic.Anthropic()
    content = _document_blocks(filename, data)
    content.append(
        {
            "type": "text",
            "text": "Produce a full Bailey review of this employment offer: extraction, scores, "
            "financial scenarios, exit costs, market benchmarks, red flags, and the negotiation playbook.",
        }
    )

    response = client.messages.parse(
        model=MODEL,
        max_tokens=16000,
        thinking={"type": "adaptive"},
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": content}],
        output_format=OfferAnalysis,
    )
    if response.stop_reason == "refusal":
        raise RuntimeError("The model declined to analyze this document.")
    return response.parsed_output


def _demo_analysis() -> OfferAnalysis:
    """Canned analysis of the bundled sample offer, for running without an API key."""
    demo_path = Path(__file__).parent / "sample_offers" / "demo_analysis.json"
    return OfferAnalysis.model_validate(json.loads(demo_path.read_text()))
