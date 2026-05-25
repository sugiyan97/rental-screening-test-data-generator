from typing import Literal

from pydantic import BaseModel


class DocumentSpec(BaseModel):
    document_type: str
    variant: str


class Company(BaseModel):
    company_name: str | None = None
    company_kana: str | None = None
    corporate_number: str | None = None
    head_office_address: str | None = None
    representative_name: str | None = None
    representative_birth_date: str | None = None
    representative_address: str | None = None
    phone: str | None = None
    email: str | None = None
    established_date: str | None = None
    capital: str | None = None
    business_description: str | None = None
    employee_count: str | None = None
    fiscal_year_end: str | None = None


class Applicant(BaseModel):
    name: str | None = None
    kana: str | None = None
    birth_date: str | None = None
    age: str | None = None
    gender: str | None = None
    current_address: str | None = None
    phone: str | None = None
    email: str | None = None
    id_document_type: str | None = None


class Employment(BaseModel):
    employer_name: str | None = None
    department: str | None = None
    job_title: str | None = None
    years_employed: str | None = None
    annual_income: str | None = None
    employer_phone: str | None = None
    employer_address: str | None = None


class Property(BaseModel):
    property_name: str | None = None
    room_number: str | None = None
    property_address: str | None = None
    rent: str | None = None
    management_fee: str | None = None
    desired_move_in_date: str | None = None
    usage_purpose: str | None = None


class Financials(BaseModel):
    fiscal_year: str | None = None
    sales: str | None = None
    operating_income: str | None = None
    ordinary_income: str | None = None
    net_income: str | None = None
    total_assets: str | None = None
    total_liabilities: str | None = None
    net_assets: str | None = None


class BusinessPlan(BaseModel):
    plan_period: str | None = None
    business_overview: str | None = None
    revenue_plan: str | None = None
    hiring_plan: str | None = None
    risk_factors: str | None = None


class EmergencyContact(BaseModel):
    name: str | None = None
    relation: str | None = None
    phone: str | None = None
    address: str | None = None


class Income(BaseModel):
    income_year: str | None = None
    annual_income: str | None = None
    monthly_income: str | None = None
    income_type: str | None = None
    issuer_name: str | None = None
    issue_date: str | None = None


class Case(BaseModel):
    case_id: str
    applicant_type: Literal["corporate", "individual", "sole_proprietor"]
    documents: list[DocumentSpec]
    company: Company | None = None
    financials: Financials | None = None
    business_plan: BusinessPlan | None = None
    applicant: Applicant | None = None
    employment: Employment | None = None
    emergency_contact: EmergencyContact | None = None
    income: Income | None = None
    property: Property | None = None
