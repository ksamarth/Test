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


class RedFlag(BaseModel):
    title: str = Field(description="Short name for the issue, e.g. 'Collections-based pay with no collections control'.")
    severity: Severity = Field(description="high = could cost serious money or freedom; medium = unfavorable but common; low = worth knowing.")
    clause_reference: Optional[str] = Field(
        None, description="Section number or quoted fragment locating the clause in the document."
    )
    explanation: str = Field(
        description="Plain-English explanation of why this matters, written for a new grad with no business background. 2-4 sentences."
    )
    what_to_do: str = Field(
        description="Concrete next step: what to ask the employer, what change to request, or what to verify. Phrase as guidance, not a directive."
    )


class NegotiationPoint(BaseModel):
    topic: str = Field(description="What to negotiate, e.g. 'Daily guarantee duration'.")
    rationale: str = Field(description="Why this is reasonable to ask for, in plain English.")
    suggested_ask: str = Field(
        description="A polite, specific way to phrase the request to the employer."
    )


class OfferAnalysis(BaseModel):
    extraction: OfferExtraction
    summary: str = Field(
        description="3-5 sentence plain-English summary of the offer: who it's from, how you get paid, and the overall shape of the deal."
    )
    strengths: List[str] = Field(
        description="Genuinely favorable terms in this offer, one short sentence each. Be honest — don't pad."
    )
    red_flags: List[RedFlag] = Field(
        description="Issues ordered most severe first. Include missing-but-expected terms (e.g. no tail coverage mentioned) as flags."
    )
    negotiation_points: List[NegotiationPoint] = Field(
        description="The 3-6 highest-leverage things worth negotiating, ordered by impact."
    )
    questions_for_attorney: List[str] = Field(
        description="Specific questions the reader should bring to a healthcare contract attorney, referencing this contract's actual clauses."
    )
    overall_read: str = Field(
        description="2-3 sentence bottom line: how this offer compares to typical new-grad offers of this type, and the biggest thing to resolve before signing. Educational framing — never 'you should sign' or 'don't sign'."
    )
