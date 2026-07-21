# Bailey

*Before you sign, ask Bailey.*

Bailey is a paid-review-grade contract analysis tool for dental and medical
students and new graduates. Upload a job offer (PDF, DOCX, or TXT) and get back
the review a sharp mentor would give you:

- **A grade for the offer** — overall score plus four category scores
  (compensation, restrictive covenants, insurance & benefits,
  termination & flexibility) with rationale
- **The money, modeled** — three first-year earnings scenarios with the
  arithmetic shown, the break-even production number, the effective split after
  deductions, and every assumption stated
- **The price of leaving** — an itemized estimate of what exiting at month 12
  actually costs (clawbacks, tail coverage, covenant exposure)
- **Market benchmarks** — every major term compared to typical new-grad ranges
  with a favorable / typical / unfavorable / missing verdict
- **Red flags with price tags** — each flag states what ignoring it could cost
- **A negotiation playbook** — asks ordered by dollar impact, each with a value
  estimate and suggested phrasing, plus a complete ready-to-send negotiation
  email with a copy button

The frontend is the "Classical" design direction: a marketing landing page, an
animated analyzing stage, and the full scored report. Reviews accumulate into a
persistent, client-side **library** (kept in `localStorage`), so you can switch
between offers and — with two or more — open a **side-by-side compare view** led
by grade, expected year-one gross, cost-of-exit, high-severity flag count, and
the key contract terms.

The name: Harvey (the legal AI) is named for Harvey Specter from the lawyer
show. Bailey is named for Dr. Miranda Bailey — the mentor from the doctor show
who looks out for new residents.

Demo mode ships two contrasting sample contracts (a weak DSO offer and a strong
private-practice offer) and alternates between them on each run, so you can try
the compare view without an API key.

> Bailey is an educational tool. It does not provide legal, financial, or tax
> advice and is not a substitute for review by a licensed attorney or CPA.
> Earnings figures are illustrative estimates, not income promises.

## Run it

```bash
cd bailey
pip install -r requirements.txt

export ANTHROPIC_API_KEY=sk-ant-...   # real analysis
# or, to try the UI without a key:
# export BAILEY_DEMO=1                # returns a canned review of the sample offer

uvicorn app:app --reload
```

Open http://127.0.0.1:8000 and drop in an offer. A realistic sample contract to
test with is in `sample_offers/sample_dso_offer.txt`.

Built on the Claude API (`claude-opus-4-8`) using structured outputs — one call
extracts the contract into a normalized schema *and* produces the full scored
review. The extraction schema doubles as the record format for the planned
anonymized benchmarking database.

## Layout

| File | Purpose |
|---|---|
| `app.py` | FastAPI server: upload endpoint + static frontend |
| `analyzer.py` | Claude call (structured outputs via `messages.parse`), file handling |
| `schemas.py` | Pydantic models: extraction schema + scored-review schema |
| `static/index.html` | Single-page frontend (upload, review, compare view) |
| `sample_offers/` | Sample contract + canned demo review |

## Notes for the roadmap

- **Privacy**: this prototype keeps nothing server-side — files are analyzed in
  memory and returned. Production needs an explicit retention/deletion policy and
  the "we never train AI models on your documents" commitment.
- **Benchmarks**: `OfferExtraction` is the normalized record that, de-identified
  and with user consent, feeds the real comparison database ("your daily
  guarantee is below median for GPs in Dallas"). Until then, typical ranges come
  from published survey data and common contract patterns, and the UI says so.
- **Output framing**: prompts instruct the model to educate and suggest asks,
  never to direct ("don't sign") — keep this constraint through any prompt
  changes. Financial scenarios must always ship with their assumptions.
- **Naming**: trademark/domain diligence on "Bailey" still to be done.
