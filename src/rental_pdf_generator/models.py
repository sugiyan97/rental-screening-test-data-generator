from typing import Literal

from pydantic import BaseModel


class DocumentSpec(BaseModel):
    document_type: str
    variant: str


class Company(BaseModel):
    company_name: str | None = None
    company_kana: str | None = None
    corporate_number: str | None = None
    postal_code: str | None = None
    head_office_address: str | None = None
    representative_name: str | None = None
    representative_kana: str | None = None
    representative_birth_date: str | None = None
    representative_age: str | None = None
    representative_gender: str | None = None
    representative_postal_code: str | None = None
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
    postal_code: str | None = None
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
    postal_code: str | None = None
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
    # 開業計画用の追加フィールド（個人・法人スタートアップ向け）
    trade_name: str | None = None              # 屋号（個人事業主）
    opening_date: str | None = None             # 開業予定日
    business_category: str | None = None        # 業種
    target_customers: str | None = None         # 想定顧客層
    initial_capital: str | None = None          # 開業資金（自己資金）
    funding_plan: str | None = None             # 資金調達計画（借入・出資）
    monthly_revenue_target: str | None = None   # 月次売上目標
    monthly_cost_estimate: str | None = None    # 月次費用見込
    founder_background: str | None = None       # 代表者・創業者の経歴
    competitive_advantage: str | None = None    # 競合優位性
    marketing_strategy: str | None = None       # マーケティング戦略


class EmergencyContact(BaseModel):
    name: str | None = None
    relation: str | None = None
    phone: str | None = None
    postal_code: str | None = None
    address: str | None = None


class Income(BaseModel):
    income_year: str | None = None
    annual_income: str | None = None
    monthly_income: str | None = None
    income_type: str | None = None
    issuer_name: str | None = None
    issue_date: str | None = None
    base_salary: str | None = None
    overtime_allowance: str | None = None
    commuting_allowance: str | None = None
    bonus: str | None = None
    certificate_expiry: str | None = None
    # 確定申告書型（自営業・フリーランス）
    business_income: str | None = None
    deductible_expenses: str | None = None
    taxable_income: str | None = None


class Guarantor(BaseModel):
    name: str | None = None
    kana: str | None = None
    birth_date: str | None = None
    age: str | None = None
    gender: str | None = None
    relationship: str | None = None
    postal_code: str | None = None
    current_address: str | None = None
    phone: str | None = None
    employer_name: str | None = None
    annual_income: str | None = None


class GuarantorIncome(BaseModel):
    income_year: str | None = None
    annual_income: str | None = None
    monthly_income: str | None = None
    income_type: str | None = None
    employer_name: str | None = None
    employer_phone: str | None = None
    employer_address: str | None = None
    issue_date: str | None = None
    base_salary: str | None = None
    bonus: str | None = None


class IdentityDocument(BaseModel):
    license_number: str | None = None
    my_number: str | None = None
    passport_number: str | None = None
    name_en: str | None = None
    nationality: str | None = None
    expiry: str | None = None
    issue_date: str | None = None
    issue_place: str | None = None
    # 在留カード用
    residence_card_number: str | None = None
    visa_type: str | None = None
    period_of_stay: str | None = None


class SealRegistrationCertificate(BaseModel):
    registration_number: str | None = None
    registration_date: str | None = None
    issuing_municipality: str | None = None
    issue_date: str | None = None


class ResidenceCertificate(BaseModel):
    gender: str | None = None
    honseki: str | None = None
    head_of_household: str | None = None
    relation_to_head: str | None = None
    resident_since: str | None = None
    issuing_municipality: str | None = None
    issue_date: str | None = None


class ParentCompany(BaseModel):
    company_name: str | None = None
    company_kana: str | None = None
    corporate_number: str | None = None
    head_office_address: str | None = None
    representative_name: str | None = None
    capital: str | None = None
    established_date: str | None = None
    business_description: str | None = None
    fiscal_year_end: str | None = None
    relationship: str | None = None


class BusinessLicense(BaseModel):
    license_name: str | None = None
    license_number: str | None = None
    licensee_name: str | None = None
    business_type: str | None = None
    license_address: str | None = None
    issue_date: str | None = None
    expiry: str | None = None
    issuing_authority: str | None = None


class CorporateGuarantee(BaseModel):
    guarantor_name: str | None = None
    guarantor_kana: str | None = None
    guarantor_address: str | None = None
    guarantor_birth_date: str | None = None
    relationship_to_company: str | None = None
    guarantee_amount: str | None = None
    guarantee_period: str | None = None
    contract_date: str | None = None


class Guarantor2(BaseModel):
    name: str | None = None
    kana: str | None = None
    birth_date: str | None = None
    age: str | None = None
    gender: str | None = None
    relationship: str | None = None
    postal_code: str | None = None
    current_address: str | None = None
    phone: str | None = None
    employer_name: str | None = None
    annual_income: str | None = None


class Guarantor2Income(BaseModel):
    income_year: str | None = None
    annual_income: str | None = None
    monthly_income: str | None = None
    income_type: str | None = None
    employer_name: str | None = None
    employer_phone: str | None = None
    employer_address: str | None = None
    issue_date: str | None = None
    base_salary: str | None = None
    bonus: str | None = None


class GuaranteeCompany(BaseModel):
    company_name: str | None = None
    company_address: str | None = None
    company_phone: str | None = None
    application_date: str | None = None
    plan_name: str | None = None
    initial_fee: str | None = None
    monthly_fee: str | None = None
    coverage_amount: str | None = None
    contract_period: str | None = None


class OfferLetter(BaseModel):
    employer_name: str | None = None
    employer_address: str | None = None
    employer_phone: str | None = None
    department: str | None = None
    job_title: str | None = None
    start_date: str | None = None
    expected_annual_income: str | None = None
    expected_monthly_income: str | None = None
    issue_date: str | None = None
    hr_contact_name: str | None = None


class PreviousEmployment(BaseModel):
    employer_name: str | None = None
    employer_address: str | None = None
    employment_period: str | None = None
    income_year: str | None = None
    gross_income: str | None = None
    withholding_tax: str | None = None
    social_insurance: str | None = None
    end_date: str | None = None


class BusinessOpeningNotice(BaseModel):
    issuing_tax_office: str | None = None
    submission_date: str | None = None
    tax_address: str | None = None
    owner_name: str | None = None
    owner_birth_date: str | None = None
    occupation: str | None = None
    trade_name: str | None = None
    opening_date: str | None = None
    business_overview: str | None = None
    employs_others: str | None = None


class BankBalanceCertificate(BaseModel):
    account_holder: str | None = None
    bank_name: str | None = None
    branch_name: str | None = None
    account_type: str | None = None
    account_number: str | None = None
    balance_as_of_date: str | None = None
    balance_amount: str | None = None
    issue_date: str | None = None
    issuer_staff: str | None = None


class FundingEvidence(BaseModel):
    as_of_date: str | None = None              # 基準日
    own_capital: str | None = None             # 自己資金（資本金）
    bank_loan: str | None = None               # 金融機関融資
    bank_loan_lender: str | None = None        # 融資元金融機関
    investment: str | None = None              # 出資（VC・エンジェル）
    investor_name: str | None = None           # 出資者
    subsidy: str | None = None                 # 補助金・助成金
    subsidy_source: str | None = None          # 補助金交付元
    total_funding: str | None = None           # 合計調達額
    fund_usage: str | None = None              # 資金使途
    monthly_rent_coverage: str | None = None   # 賃料支払能力（月額賃料の何ヶ月分か）
    evidence_documents: str | None = None      # 裏付け書類一覧


class TrialBalance(BaseModel):
    fiscal_period: str | None = None
    cash: str | None = None
    accounts_receivable: str | None = None
    inventory: str | None = None
    total_current_assets: str | None = None
    fixed_assets: str | None = None
    total_assets: str | None = None
    accounts_payable: str | None = None
    short_term_borrowings: str | None = None
    total_current_liabilities: str | None = None
    long_term_borrowings: str | None = None
    total_liabilities: str | None = None
    total_net_assets: str | None = None
    revenue: str | None = None
    cost_of_sales: str | None = None
    gross_profit: str | None = None
    sga_expenses: str | None = None
    operating_profit: str | None = None


class SohoUsage(BaseModel):
    residential_ratio: str | None = None
    business_ratio: str | None = None
    business_type: str | None = None
    business_overview: str | None = None
    visitor_frequency: str | None = None
    trade_name: str | None = None
    has_signboard: str | None = None


class CorporateHousingUsage(BaseModel):
    occupant_name: str | None = None
    occupant_relation: str | None = None
    occupant_department: str | None = None
    occupant_job_title: str | None = None
    occupant_family: str | None = None
    rent_subsidy_amount: str | None = None
    rent_subsidy_ratio: str | None = None
    contract_name: str | None = None
    parking_required: str | None = None


class CorporateStoreUsage(BaseModel):
    business_format: str | None = None
    operating_hours: str | None = None
    operating_days: str | None = None
    closed_days: str | None = None
    expected_visitors_per_day: str | None = None
    noise_level: str | None = None
    odor_level: str | None = None
    construction_required: str | None = None
    waste_type: str | None = None


class BusinessLicenseApplication(BaseModel):
    applicant_name: str | None = None
    business_type: str | None = None
    license_address: str | None = None
    application_date: str | None = None
    receipt_number: str | None = None
    issuing_authority: str | None = None
    expected_issue_date: str | None = None
    status_note: str | None = None


class BusinessUsePledge(BaseModel):
    pledger_name: str | None = None
    representative_name: str | None = None
    pledge_date: str | None = None
    original_business_type: str | None = None
    changed_business_type: str | None = None
    change_reason: str | None = None
    license_required: str | None = None


class Student(BaseModel):
    name: str | None = None
    kana: str | None = None
    birth_date: str | None = None
    school_name: str | None = None
    department: str | None = None
    grade: str | None = None
    student_number: str | None = None
    enrollment_date: str | None = None
    expected_graduation_date: str | None = None
    relationship_to_applicant: str | None = None


class Case(BaseModel):
    case_id: str
    description: str | None = None
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
    guarantor: Guarantor | None = None
    guarantor_income: GuarantorIncome | None = None
    identity_document: IdentityDocument | None = None
    guarantor_identity_document: IdentityDocument | None = None
    # グループ1: 法人系拡充
    parent_company: ParentCompany | None = None
    parent_company_financials: Financials | None = None
    business_license: BusinessLicense | None = None
    corporate_guarantee: CorporateGuarantee | None = None
    # グループ2: 保証人複数 / 保証会社
    guarantor_2: Guarantor2 | None = None
    guarantor_2_income: Guarantor2Income | None = None
    guarantor_2_identity_document: IdentityDocument | None = None
    guarantee_company: GuaranteeCompany | None = None
    # 連帯保証人（個人）の追加証明書
    guarantor_seal_certificate: SealRegistrationCertificate | None = None
    guarantor_residence_certificate: ResidenceCertificate | None = None
    guarantor_2_seal_certificate: SealRegistrationCertificate | None = None
    guarantor_2_residence_certificate: ResidenceCertificate | None = None
    # グループ3: 転職・学生
    offer_letter: OfferLetter | None = None
    previous_employment: PreviousEmployment | None = None
    student: Student | None = None
    # 営業許可書の有無パターン
    business_license_application: BusinessLicenseApplication | None = None
    business_use_pledge: BusinessUsePledge | None = None
    # 多年度書類対応
    previous_financials: Financials | None = None
    previous_income: Income | None = None
    trial_balance: TrialBalance | None = None
    # 用途別フィールド
    soho_usage: SohoUsage | None = None
    corporate_housing_usage: CorporateHousingUsage | None = None
    corporate_store_usage: CorporateStoreUsage | None = None
    # 開業時補助書類
    business_opening_notice: BusinessOpeningNotice | None = None
    bank_balance_certificate: BankBalanceCertificate | None = None
    funding_evidence: FundingEvidence | None = None
