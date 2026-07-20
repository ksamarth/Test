# OfferLens

Upload a dental or medical job offer (PDF, DOCX, or TXT) and get a plain-English
analysis back: extracted terms, red flags with severity, negotiation guidance,
and questions to bring to a real attorney. Upload more than one offer and a
side-by-side comparison view appears.

Built on the Claude API (`claude-opus-4-8`) using structured outputs — one call
extracts the contract into a normalized schema *and* produces the analysis. The
extraction schema doubles as the record format for the planned anonymized
benchmarking database.

> OfferLens is an educational tool. It does not provide legal, financial, or tax
> advice and is not a substitute for review by a licensed attorney or CPA.

## Run it

```bash
cd offerlens
pip install -r requirements.txt

export ANTHROPIC_API_KEY=sk-ant-...   # real analysis
# or, to try the UI without a key:
# export OFFERLENS_DEMO=1             # returns a canned analysis of the sample offer

uvicorn app:app --reload
```

Open http://127.0.0.1:8000 and drop in an offer. A realistic sample contract to
test with is in `sample_offers/sample_dso_offer.txt`.

## Layout

| File | Purpose |
|---|---|
| `app.py` | FastAPI server: upload endpoint + static frontend |
| `analyzer.py` | Claude call (structured outputs via `messages.parse`), file handling |
| `schemas.py` | Pydantic models: extraction schema + analysis schema |
| `static/index.html` | Single-page frontend (upload, analysis view, compare view) |
| `sample_offers/` | Sample contract + canned demo analysis |

## Notes for the roadmap

- **Privacy**: this prototype keeps nothing server-side — files are analyzed in
  memory and returned. Production needs an explicit retention/deletion policy and
  the "we never train AI models on your documents" commitment.
- **Benchmarks**: `OfferExtraction` is the normalized record that, de-identified
  and with user consent, feeds the Glassdoor-style comparison database
  ("your daily guarantee is below median for GPs in Dallas").
- **Output framing**: prompts instruct the model to educate and suggest questions,
  never to direct ("don't sign") — keep this constraint through any prompt changes.
