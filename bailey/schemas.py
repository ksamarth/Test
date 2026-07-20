"""Pydantic schemas for offer extraction and analysis.

These models serve two purposes:
1. They are the structured-output schema Claude fills in (via messages.parse).
2. The extraction portion is the normalized record that will later feed the
   anonymized benchmarking database (the Glassdoor-style data flywheel).
"""

from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field


class PracticeType(str, Enum):
    dso = "dso"
    private_practice = "private_practice"
    hospital = "hospital"
    academic = "academic"
    community_health_center = "community_health_center"
    other = "other"
    unknown = "unknown"


class CompensationBasis(str, Enum):
    production = "production"
    collections = "collections"
    salary_only = "salary_only"
    hybrid = "hybrid"
    unknown = "unknown"


class MalpracticeType(str, Enum):
    occurrence = "occurrence"
    claims_made_with_tail = "claims_made_with_tail"
    claims_made_no_tail = "claims_made_no_tail"
    not_specified = "not_specified"


class Severity(str, Enum):
    high = "high"
    medium = "medium"
    low = "low"


class Verdict(str, Enum):
    favorable = "favorable"
    typical = "typical"
    unfavorable = "unfavorable"
    missing = "missing"


class ScoreCategory(str, Enum):
    compensation = "compensation"
    restrictive_covenants = "restrictive_covenants"
    insurance_and_benefits = "insurance_and_benefits"
    termination_and_flexibility = "termination_and_flexibility"


class Compensation(BaseModel):
    base_salary_annual: Optional[float] = Field(
        None, description="Annual base salary in USD, if stated. Null if not specified."
    )
    daily_guarantee: Optional[float] = Field(
        None, description="Guaranteed daily rate in USD, if stated (common in dental associate contracts)."
    )
    production_percentage: Optional[float] = Field(
        None, description="Percentage of production or collections paid to the provider, e.g. 30 for 30%."
    )
    compensation_basis: CompensationBasis = Field(
        CompensationBasis.unknown,
        description="Whether percentage comp is based on production (billed), collections (received), salary only, or a hybrid. Collections-based comp shifts collection risk onto the provider — flag it.",
    )
    guarantee_duration_months: Optional[int] = Field(
        None, description="How many months any salary/daily guarantee lasts before switching to pure production."
    )
    sign_on_bonus: Optional[float] = Field(None, description="Sign-on bonus in USD, if any.")
    sign_on_bonus_clawback: Optional[str] = Field(
        None, description="Repayment/clawback terms attached to the sign-on bonus, quoted or paraphrased."
    )
    relocation_assistance: Optional[float] = Field(None, description="Relocation assistance in USD, if any.")
    student_loan_repayment: Optional[str] = Field(
        None, description="Student loan repayment terms, if any, including amounts and service commitments."
    )
    lab_fee_deduction: Optional[str] = Field(
        None, description="How lab fees are handled (deducted from production before or after the split, employer-paid, etc.). A classic dental-contract gotcha."
    )


class RestrictiveCovenants(BaseModel):
    non_compete_radius_miles: Optional[float] = Field(
        None, description="Non-compete radius in miles, if stated."
    )
    non_compete_duration_months: Optional[int] = Field(
        None, description="Non-compete duration in months after separation."
    )
    non_compete_scope: Optional[str] = Field(
        None, description="What activity the non-compete restricts, and from which locations it is measured (single office vs. every employer location — a major difference for multi-site DSOs)."
    )
    non_solicit_patients_months: Optional[int] = Field(
        None, description="Patient non-solicitation duration in months, if any."
    )
    non_solicit_staff_months: Optional[int] = Field(
        None, description="Staff non-solicitation duration in months, if any."
    )
    liquidated_damages: Optional[str] = Field(
        None, description="Any buyout or liquidated-damages amount for breaching the covenants."
    )


class TermAndTermination(BaseModel):
    initial_term_months: Optional[int] = Field(None, description="Initial contract term in months.")
    auto_renewal: Optional[bool] = Field(None, description="Whether the contract auto-renews.")
    termination_notice_days_employer: Optional[int] = Field(
        None, description="Days of notice the employer must give to terminate without cause."
    )
    termination_notice_days_provider: Optional[int] = Field(
        None, description="Days of notice the provider must give to terminate without cause."
    )
    for_cause_provisions: Optional[str] = Field(
        None, description="Summary of for-cause termination triggers, especially any vague or one-sided ones."
    )


class BenefitsAndInsurance(BaseModel):
    malpractice_type: MalpracticeType = Field(
        MalpracticeType.not_specified,
        description="Type of malpractice coverage. Claims-made without employer-paid tail leaves the provider owing the tail premium at exit — flag it.",
    )
    tail_coverage_paid_by: Optional[str] = Field(
        None, description="Who pays tail coverage on exit: employer, provider, or split/conditional."
    )
    health_insurance: Optional[str] = Field(None, description="Health insurance terms, briefly.")
    retirement: Optional[str] = Field(None, description="Retirement plan terms (401k match etc.), briefly.")
    ce_allowance: Optional[str] = Field(
        None, description="Continuing-education allowance and paid CE days, if any."
    )
    pto: Optional[str] = Field(None, description="Paid time off terms, briefly.")
    licensure_dues_covered: Optional[str] = Field(
        None, description="Whether licensure, DEA, association dues are covered."
    )


class OfferExtraction(BaseModel):
    employer_name: Optional[str] = Field(None, description="Employer / practice name.")
    position_title: Optional[str] = Field(None, description="Position title, e.g. Associate Dentist.")
    profession: Optional[str] = Field(
        None, description="Profession/specialty, e.g. general dentistry, oral surgery, family medicine."
    )
    location: Optional[str] = Field(None, description="City and state of the primary work location.")
    practice_type: PracticeType = Field(
        PracticeType.unknown, description="Type of practice/employer."
    )
    employment_status: Optional[str] = Field(
        None, description="W-2 employee vs 1099 independent contractor. 1099 status in an associate contract deserves scrutiny."
    )
    full_time: Optional[bool] = Field(None, description="Whether the position is full-time.")
    days_per_week: Optional[float] = Field(None, description="Scheduled days per week, if stated.")
    compensation: Compensation
    restrictive_covenants: RestrictiveCovenants
    term_and_termination: TermAndTermination
    benefits: BenefitsAndInsurance
    patient_records_ownership: Optional[str] = Field(
        None, description="Who owns patient records and charts after separation."
    )
    other_notable_clauses: List[str] = Field(
        default_factory=list, description="Any other clauses worth the reader's attention, one short sentence each."
    )


class CategoryScore(BaseModel):
    category: ScoreCategory
    score: int = Field(description="0-100 for this category, per the scoring rubric.")
    rationale: str = Field(description="One or two sentences justifying the score, citing the decisive terms.")


class OfferScore(BaseModel):
    overall: int = Field(
        description="0-100 overall score per the scoring rubric, weighting categories by financial impact for a new graduate."
    )
    grade: str = Field(
        description="Letter grade from the overall score: A (90+), A- (85-89), B+ (80-84), B (75-79), B- (70-74), C+ (65-69), C (55-64), C- (45-54), D (35-44), F (<35)."
    )
    headline: str = Field(
        description="One punchy sentence a well-informed friend would text you about this offer."
    )
    categories: List[CategoryScore] = Field(description="Exactly four entries, one per ScoreCategory value.")


class EarningsScenario(BaseModel):
    label: str = Field(description="Scenario name: 'Conservative', 'Expected', or 'Strong'.")
    assumed_daily_production: Optional[float] = Field(
        None, description="Assumed daily production (or equivalent volume driver) in USD for this scenario. Null for pure-salary offers."
    )
    estimated_annual_gross: float = Field(
        description="Estimated first-year gross compensation in USD under this scenario, accounting for guarantee periods, splits, and stated deductions."
    )
    how_calculated: str = Field(
        description="One or two sentences showing the arithmetic so the reader can check it."
    )


class FinancialAnalysis(BaseModel):
    scenarios: List[EarningsScenario] = Field(
        description="Three first-year earnings scenarios: Conservative, Expected, Strong. For pure-salary offers, model realistic variations (bonus attainment, call pay) instead."
    )
    break_even_daily_production: Optional[float] = Field(
        None, description="Daily production in USD at which percentage pay equals any stated guarantee. Null if not applicable."
    )
    break_even_explanation: Optional[str] = Field(
        None, description="Plain-English explanation of the break-even number and what happens below it."
    )
    effective_split_note: Optional[str] = Field(
        None, description="If deductions (lab fees, supplies) reduce the stated percentage, quantify the effective percentage on a realistic example."
    )
    assumptions: List[str] = Field(
        description="Every assumption used (working days per year, collection rate, lab fee share, typical production ranges for this profession), stated explicitly so the reader can adjust."
    )


class ExitCostItem(BaseModel):
    item: str = Field(description="The cost, e.g. 'Sign-on bonus repayment'.")
    estimated_cost: str = Field(description="Dollar figure or range as a string, e.g. '$15,000' or '$4,000-$8,000'.")
    basis: str = Field(description="Which clause creates this cost and how the estimate was derived.")


class ExitCostAnalysis(BaseModel):
    scenario: str = Field(description="The modeled exit point, e.g. 'If you leave — or are let go — 12 months in'.")
    items: List[ExitCostItem]
    estimated_total: str = Field(description="Total estimated cost as a string or range.")
    note: str = Field(
        description="One or two sentences of context, including non-dollar costs like the non-compete's effect on where you can work next."
    )


class MarketComparisonRow(BaseModel):
    term: str = Field(description="The contract term being compared, e.g. 'Production split'.")
    this_offer: str = Field(description="What this contract says, compactly.")
    typical_range: str = Field(description="The typical market range for comparable new-grad positions.")
    verdict: Verdict = Field(
        description="favorable = better than typical for the reader; unfavorable = worse; missing = the contract is silent where it shouldn't be."
    )
    note: Optional[str] = Field(None, description="Optional one-line nuance.")


class RedFlag(BaseModel):
    title: str = Field(description="Short name for the issue, e.g. 'Collections-based pay with no collections control'.")
    severity: Severity = Field(description="high = could cost serious money or freedom; medium = unfavorable but common; low = worth knowing.")
    clause_reference: Optional[str] = Field(
        None, description="Section number or quoted fragment locating the clause in the document."
    )
    explanation: str = Field(
        description="Plain-English explanation of why this matters, written for a new grad with no business background. 2-4 sentences."
    )
    cost_if_ignored: Optional[str] = Field(
        None, description="Where quantifiable, the realistic dollar exposure of leaving this clause as-is, e.g. 'roughly $6,000-$12,000 over the initial term'."
    )
    what_to_do: str = Field(
        description="Concrete next step: what to ask the employer, what change to request, or what to verify. Phrase as guidance, not a directive."
    )


class NegotiationPoint(BaseModel):
    priority: int = Field(description="1 = highest leverage. Order by expected dollar impact.")
    topic: str = Field(description="What to negotiate, e.g. 'Tail coverage'.")
    rationale: str = Field(description="Why this is reasonable to ask for, in plain English.")
    estimated_value: Optional[str] = Field(
        None, description="What winning this ask is realistically worth in dollars, as a string range."
    )
    suggested_ask: str = Field(
        description="A polite, specific way to phrase the request to the employer."
    )


class OfferAnalysis(BaseModel):
    extraction: OfferExtraction
    score: OfferScore
    summary: str = Field(
        description="3-5 sentence plain-English summary of the offer: who it's from, how you get paid, and the overall shape of the deal."
    )
    financial_analysis: FinancialAnalysis
    exit_costs: ExitCostAnalysis
    market_comparison: List[MarketComparisonRow] = Field(
        description="8-14 rows covering the terms that matter most, ordered with unfavorable/missing verdicts first."
    )
    strengths: List[str] = Field(
        description="Genuinely favorable terms in this offer, one short sentence each. Be honest — don't pad."
    )
    red_flags: List[RedFlag] = Field(
        description="Issues ordered most severe first. Include missing-but-expected terms (e.g. no tail coverage mentioned) as flags."
    )
    negotiation_playbook: List[NegotiationPoint] = Field(
        description="The 3-6 highest-leverage asks, ordered by priority."
    )
    negotiation_email: str = Field(
        description="A complete, ready-to-send email to the employer raising the top 3-4 playbook items. Warm, professional, appreciative in tone — written as the candidate, not as a lawyer. Use [Name] placeholders for the greeting and signature unless the document names the hiring contact."
    )
    value_at_stake: str = Field(
        description="One sentence quantifying what successfully negotiating this playbook is typically worth over the initial term, e.g. 'Winning even two of these asks is typically worth $15,000-$40,000 over the two-year term.'"
    )
    overall_read: str = Field(
        description="2-3 sentence bottom line: how this offer compares to typical new-grad offers of this type, and the biggest thing to resolve before signing. Educational framing — never 'you should sign' or 'don't sign'."
    )
