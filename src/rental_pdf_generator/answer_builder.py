from collections.abc import Callable
from typing import Any

from .models import Case


class UnsupportedDocumentTypeError(Exception):
    pass


def _get(obj: Any, attr: str) -> Any:
    return getattr(obj, attr, None) if obj is not None else None


def _build_rental_application_corporate(case: Case) -> dict[str, Any]:
    c = case.company
    p = case.property
    return {
        "company_name": _get(c, "company_name"),
        "company_kana": _get(c, "company_kana"),
        "corporate_number": _get(c, "corporate_number"),
        "head_office_address": _get(c, "head_office_address"),
        "representative_name": _get(c, "representative_name"),
        "representative_birth_date": _get(c, "representative_birth_date"),
        "representative_address": _get(c, "representative_address"),
        "phone": _get(c, "phone"),
        "email": _get(c, "email"),
        "established_date": _get(c, "established_date"),
        "capital": _get(c, "capital"),
        "business_description": _get(c, "business_description"),
        "employee_count": _get(c, "employee_count"),
        "property_name": _get(p, "property_name"),
        "room_number": _get(p, "room_number"),
        "property_address": _get(p, "property_address"),
        "rent": _get(p, "rent"),
        "management_fee": _get(p, "management_fee"),
        "desired_move_in_date": _get(p, "desired_move_in_date"),
        "usage_purpose": _get(p, "usage_purpose"),
    }


def _build_registry_certificate(case: Case) -> dict[str, Any]:
    c = case.company
    return {
        "company_name": _get(c, "company_name"),
        "corporate_number": _get(c, "corporate_number"),
        "head_office_address": _get(c, "head_office_address"),
        "representative_name": _get(c, "representative_name"),
        "established_date": _get(c, "established_date"),
        "capital": _get(c, "capital"),
        "business_description": _get(c, "business_description"),
        "fiscal_year_end": _get(c, "fiscal_year_end"),
    }


def _build_financial_statement(case: Case) -> dict[str, Any]:
    c = case.company
    f = case.financials
    return {
        "company_name": _get(c, "company_name"),
        "fiscal_year": _get(f, "fiscal_year"),
        "sales": _get(f, "sales"),
        "operating_income": _get(f, "operating_income"),
        "ordinary_income": _get(f, "ordinary_income"),
        "net_income": _get(f, "net_income"),
        "total_assets": _get(f, "total_assets"),
        "total_liabilities": _get(f, "total_liabilities"),
        "net_assets": _get(f, "net_assets"),
    }


def _build_business_plan(case: Case) -> dict[str, Any]:
    c = case.company
    bp = case.business_plan
    return {
        "company_name": _get(c, "company_name"),
        "representative_name": _get(c, "representative_name"),
        "plan_period": _get(bp, "plan_period"),
        "business_overview": _get(bp, "business_overview"),
        "revenue_plan": _get(bp, "revenue_plan"),
        "hiring_plan": _get(bp, "hiring_plan"),
        "risk_factors": _get(bp, "risk_factors"),
    }


def _build_rental_application_individual(case: Case) -> dict[str, Any]:
    a = case.applicant
    e = case.employment
    p = case.property
    ec = case.emergency_contact
    g = case.guarantor
    g2 = case.guarantor_2
    s = case.student
    return {
        "name": _get(a, "name"),
        "kana": _get(a, "kana"),
        "birth_date": _get(a, "birth_date"),
        "age": _get(a, "age"),
        "gender": _get(a, "gender"),
        "current_address": _get(a, "current_address"),
        "phone": _get(a, "phone"),
        "email": _get(a, "email"),
        "id_document_type": _get(a, "id_document_type"),
        "employer_name": _get(e, "employer_name"),
        "department": _get(e, "department"),
        "job_title": _get(e, "job_title"),
        "years_employed": _get(e, "years_employed"),
        "annual_income": _get(e, "annual_income"),
        "employer_phone": _get(e, "employer_phone"),
        "employer_address": _get(e, "employer_address"),
        "property_name": _get(p, "property_name"),
        "room_number": _get(p, "room_number"),
        "rent": _get(p, "rent"),
        "management_fee": _get(p, "management_fee"),
        "desired_move_in_date": _get(p, "desired_move_in_date"),
        "emergency_contact_name": _get(ec, "name"),
        "emergency_contact_relation": _get(ec, "relation"),
        "emergency_contact_phone": _get(ec, "phone"),
        "emergency_contact_address": _get(ec, "address"),
        "guarantor_name": _get(g, "name"),
        "guarantor_kana": _get(g, "kana"),
        "guarantor_birth_date": _get(g, "birth_date"),
        "guarantor_relationship": _get(g, "relationship"),
        "guarantor_current_address": _get(g, "current_address"),
        "guarantor_phone": _get(g, "phone"),
        "guarantor_employer_name": _get(g, "employer_name"),
        "guarantor_annual_income": _get(g, "annual_income"),
        "guarantor_2_name": _get(g2, "name"),
        "guarantor_2_kana": _get(g2, "kana"),
        "guarantor_2_birth_date": _get(g2, "birth_date"),
        "guarantor_2_relationship": _get(g2, "relationship"),
        "guarantor_2_current_address": _get(g2, "current_address"),
        "guarantor_2_phone": _get(g2, "phone"),
        "guarantor_2_employer_name": _get(g2, "employer_name"),
        "guarantor_2_annual_income": _get(g2, "annual_income"),
        "cohabitant_student_name": _get(s, "name"),
        "cohabitant_student_relationship": _get(s, "relationship_to_applicant"),
        "cohabitant_student_school_name": _get(s, "school_name"),
    }


def _build_income_certificate(case: Case) -> dict[str, Any]:
    a = case.applicant
    i = case.income
    pe = case.previous_employment
    return {
        "name": _get(a, "name"),
        "current_address": _get(a, "current_address"),
        "income_year": _get(i, "income_year"),
        "annual_income": _get(i, "annual_income"),
        "monthly_income": _get(i, "monthly_income"),
        "income_type": _get(i, "income_type"),
        "base_salary": _get(i, "base_salary"),
        "overtime_allowance": _get(i, "overtime_allowance"),
        "commuting_allowance": _get(i, "commuting_allowance"),
        "bonus": _get(i, "bonus"),
        "issuer_name": _get(i, "issuer_name"),
        "issue_date": _get(i, "issue_date"),
        "certificate_expiry": _get(i, "certificate_expiry"),
        "previous_employer_name": _get(pe, "employer_name"),
        "previous_employment_period": _get(pe, "employment_period"),
        "previous_gross_income": _get(pe, "gross_income"),
        "previous_withholding_tax": _get(pe, "withholding_tax"),
        "previous_social_insurance": _get(pe, "social_insurance"),
        "previous_end_date": _get(pe, "end_date"),
    }


def _build_corporate_guarantee_contract(case: Case) -> dict[str, Any]:
    c = case.company
    p = case.property
    cg = case.corporate_guarantee
    return {
        "company_name": _get(c, "company_name"),
        "company_address": _get(c, "head_office_address"),
        "property_name": _get(p, "property_name"),
        "property_address": _get(p, "property_address"),
        "rent": _get(p, "rent"),
        "guarantor_name": _get(cg, "guarantor_name"),
        "guarantor_kana": _get(cg, "guarantor_kana"),
        "guarantor_address": _get(cg, "guarantor_address"),
        "guarantor_birth_date": _get(cg, "guarantor_birth_date"),
        "relationship_to_company": _get(cg, "relationship_to_company"),
        "guarantee_amount": _get(cg, "guarantee_amount"),
        "guarantee_period": _get(cg, "guarantee_period"),
        "contract_date": _get(cg, "contract_date"),
    }


def _build_parent_company_guarantee_letter(case: Case) -> dict[str, Any]:
    c = case.company
    pc = case.parent_company
    p = case.property
    return {
        "subsidiary_name": _get(c, "company_name"),
        "subsidiary_address": _get(c, "head_office_address"),
        "subsidiary_representative_name": _get(c, "representative_name"),
        "parent_company_name": _get(pc, "company_name"),
        "parent_company_address": _get(pc, "head_office_address"),
        "parent_company_representative_name": _get(pc, "representative_name"),
        "parent_company_capital": _get(pc, "capital"),
        "parent_company_corporate_number": _get(pc, "corporate_number"),
        "relationship": _get(pc, "relationship"),
        "property_name": _get(p, "property_name"),
        "property_address": _get(p, "property_address"),
        "rent": _get(p, "rent"),
    }


def _build_parent_company_registry_certificate(case: Case) -> dict[str, Any]:
    pc = case.parent_company
    return {
        "company_name": _get(pc, "company_name"),
        "corporate_number": _get(pc, "corporate_number"),
        "head_office_address": _get(pc, "head_office_address"),
        "representative_name": _get(pc, "representative_name"),
        "established_date": _get(pc, "established_date"),
        "capital": _get(pc, "capital"),
        "business_description": _get(pc, "business_description"),
        "fiscal_year_end": _get(pc, "fiscal_year_end"),
    }


def _build_parent_company_financial_statement(case: Case) -> dict[str, Any]:
    pc = case.parent_company
    f = case.parent_company_financials
    return {
        "company_name": _get(pc, "company_name"),
        "fiscal_year": _get(f, "fiscal_year"),
        "sales": _get(f, "sales"),
        "operating_income": _get(f, "operating_income"),
        "ordinary_income": _get(f, "ordinary_income"),
        "net_income": _get(f, "net_income"),
        "total_assets": _get(f, "total_assets"),
        "total_liabilities": _get(f, "total_liabilities"),
        "net_assets": _get(f, "net_assets"),
    }


def _build_business_license(case: Case) -> dict[str, Any]:
    c = case.company
    bl = case.business_license
    return {
        "company_name": _get(c, "company_name"),
        "license_name": _get(bl, "license_name"),
        "license_number": _get(bl, "license_number"),
        "licensee_name": _get(bl, "licensee_name"),
        "business_type": _get(bl, "business_type"),
        "license_address": _get(bl, "license_address"),
        "issue_date": _get(bl, "issue_date"),
        "expiry": _get(bl, "expiry"),
        "issuing_authority": _get(bl, "issuing_authority"),
    }


def _build_guarantor_2_income_certificate(case: Case) -> dict[str, Any]:
    g = case.guarantor_2
    gi = case.guarantor_2_income
    return {
        "name": _get(g, "name"),
        "current_address": _get(g, "current_address"),
        "relationship": _get(g, "relationship"),
        "income_year": _get(gi, "income_year"),
        "annual_income": _get(gi, "annual_income"),
        "monthly_income": _get(gi, "monthly_income"),
        "income_type": _get(gi, "income_type"),
        "base_salary": _get(gi, "base_salary"),
        "bonus": _get(gi, "bonus"),
        "employer_name": _get(gi, "employer_name"),
        "employer_phone": _get(gi, "employer_phone"),
        "employer_address": _get(gi, "employer_address"),
        "issue_date": _get(gi, "issue_date"),
    }


def _build_guarantor_2_identity_document(case: Case) -> dict[str, Any]:
    g = case.guarantor_2
    gid = case.guarantor_2_identity_document
    return {
        "name": _get(g, "name"),
        "birth_date": _get(g, "birth_date"),
        "address": _get(g, "current_address"),
        "relationship": _get(g, "relationship"),
        "license_number": _get(gid, "license_number"),
        "my_number": _get(gid, "my_number"),
        "passport_number": _get(gid, "passport_number"),
        "expiry": _get(gid, "expiry"),
        "issue_date": _get(gid, "issue_date"),
        "issue_place": _get(gid, "issue_place"),
    }


def _build_guarantee_company_application(case: Case) -> dict[str, Any]:
    a = case.applicant
    p = case.property
    gc = case.guarantee_company
    return {
        "applicant_name": _get(a, "name"),
        "applicant_birth_date": _get(a, "birth_date"),
        "applicant_current_address": _get(a, "current_address"),
        "applicant_phone": _get(a, "phone"),
        "property_name": _get(p, "property_name"),
        "property_address": _get(p, "property_address"),
        "rent": _get(p, "rent"),
        "guarantee_company_name": _get(gc, "company_name"),
        "guarantee_company_address": _get(gc, "company_address"),
        "guarantee_company_phone": _get(gc, "company_phone"),
        "application_date": _get(gc, "application_date"),
        "plan_name": _get(gc, "plan_name"),
        "initial_fee": _get(gc, "initial_fee"),
        "monthly_fee": _get(gc, "monthly_fee"),
        "coverage_amount": _get(gc, "coverage_amount"),
        "contract_period": _get(gc, "contract_period"),
    }


def _build_offer_letter(case: Case) -> dict[str, Any]:
    a = case.applicant
    ol = case.offer_letter
    return {
        "applicant_name": _get(a, "name"),
        "applicant_current_address": _get(a, "current_address"),
        "employer_name": _get(ol, "employer_name"),
        "employer_address": _get(ol, "employer_address"),
        "employer_phone": _get(ol, "employer_phone"),
        "department": _get(ol, "department"),
        "job_title": _get(ol, "job_title"),
        "start_date": _get(ol, "start_date"),
        "expected_annual_income": _get(ol, "expected_annual_income"),
        "expected_monthly_income": _get(ol, "expected_monthly_income"),
        "issue_date": _get(ol, "issue_date"),
        "hr_contact_name": _get(ol, "hr_contact_name"),
    }


def _build_business_license_application(case: Case) -> dict[str, Any]:
    c = case.company
    p = case.property
    bla = case.business_license_application
    return {
        "company_name": _get(c, "company_name"),
        "applicant_name": _get(bla, "applicant_name"),
        "business_type": _get(bla, "business_type"),
        "license_address": _get(bla, "license_address"),
        "application_date": _get(bla, "application_date"),
        "receipt_number": _get(bla, "receipt_number"),
        "issuing_authority": _get(bla, "issuing_authority"),
        "expected_issue_date": _get(bla, "expected_issue_date"),
        "status_note": _get(bla, "status_note"),
        "property_name": _get(p, "property_name"),
    }


def _build_business_use_pledge(case: Case) -> dict[str, Any]:
    c = case.company
    p = case.property
    bup = case.business_use_pledge
    return {
        "company_name": _get(c, "company_name"),
        "pledger_name": _get(bup, "pledger_name"),
        "representative_name": _get(bup, "representative_name"),
        "pledge_date": _get(bup, "pledge_date"),
        "original_business_type": _get(bup, "original_business_type"),
        "changed_business_type": _get(bup, "changed_business_type"),
        "change_reason": _get(bup, "change_reason"),
        "license_required": _get(bup, "license_required"),
        "property_name": _get(p, "property_name"),
        "property_address": _get(p, "property_address"),
    }


def _build_student_id(case: Case) -> dict[str, Any]:
    s = case.student
    return {
        "name": _get(s, "name"),
        "kana": _get(s, "kana"),
        "birth_date": _get(s, "birth_date"),
        "school_name": _get(s, "school_name"),
        "department": _get(s, "department"),
        "grade": _get(s, "grade"),
        "student_number": _get(s, "student_number"),
        "enrollment_date": _get(s, "enrollment_date"),
        "expected_graduation_date": _get(s, "expected_graduation_date"),
        "relationship_to_applicant": _get(s, "relationship_to_applicant"),
    }


def _build_identity_document(case: Case) -> dict[str, Any]:
    a = case.applicant
    idoc = case.identity_document
    return {
        "name": _get(a, "name"),
        "birth_date": _get(a, "birth_date"),
        "address": _get(a, "current_address"),
        "license_number": _get(idoc, "license_number"),
        "my_number": _get(idoc, "my_number"),
        "passport_number": _get(idoc, "passport_number"),
        "name_en": _get(idoc, "name_en"),
        "nationality": _get(idoc, "nationality"),
        "expiry": _get(idoc, "expiry"),
        "issue_date": _get(idoc, "issue_date"),
        "issue_place": _get(idoc, "issue_place"),
        "residence_card_number": _get(idoc, "residence_card_number"),
        "visa_type": _get(idoc, "visa_type"),
        "period_of_stay": _get(idoc, "period_of_stay"),
    }


def _build_guarantor_income_certificate(case: Case) -> dict[str, Any]:
    g = case.guarantor
    gi = case.guarantor_income
    return {
        "name": _get(g, "name"),
        "current_address": _get(g, "current_address"),
        "relationship": _get(g, "relationship"),
        "income_year": _get(gi, "income_year"),
        "annual_income": _get(gi, "annual_income"),
        "monthly_income": _get(gi, "monthly_income"),
        "income_type": _get(gi, "income_type"),
        "base_salary": _get(gi, "base_salary"),
        "bonus": _get(gi, "bonus"),
        "employer_name": _get(gi, "employer_name"),
        "employer_phone": _get(gi, "employer_phone"),
        "employer_address": _get(gi, "employer_address"),
        "issue_date": _get(gi, "issue_date"),
    }


def _build_guarantor_identity_document(case: Case) -> dict[str, Any]:
    g = case.guarantor
    gid = case.guarantor_identity_document
    return {
        "name": _get(g, "name"),
        "birth_date": _get(g, "birth_date"),
        "address": _get(g, "current_address"),
        "relationship": _get(g, "relationship"),
        "license_number": _get(gid, "license_number"),
        "my_number": _get(gid, "my_number"),
        "passport_number": _get(gid, "passport_number"),
        "expiry": _get(gid, "expiry"),
        "issue_date": _get(gid, "issue_date"),
        "issue_place": _get(gid, "issue_place"),
    }


_BUILDERS: dict[str, Callable[[Case], dict[str, Any]]] = {
    "rental_application_corporate": _build_rental_application_corporate,
    "registry_certificate": _build_registry_certificate,
    "financial_statement": _build_financial_statement,
    "business_plan": _build_business_plan,
    "rental_application_individual": _build_rental_application_individual,
    "income_certificate": _build_income_certificate,
    "identity_document": _build_identity_document,
    "guarantor_income_certificate": _build_guarantor_income_certificate,
    "guarantor_identity_document": _build_guarantor_identity_document,
    "corporate_guarantee_contract": _build_corporate_guarantee_contract,
    "parent_company_guarantee_letter": _build_parent_company_guarantee_letter,
    "parent_company_registry_certificate": _build_parent_company_registry_certificate,
    "parent_company_financial_statement": _build_parent_company_financial_statement,
    "business_license": _build_business_license,
    "guarantor_2_income_certificate": _build_guarantor_2_income_certificate,
    "guarantor_2_identity_document": _build_guarantor_2_identity_document,
    "guarantee_company_application": _build_guarantee_company_application,
    "offer_letter": _build_offer_letter,
    "student_id": _build_student_id,
    "business_license_application": _build_business_license_application,
    "business_use_pledge": _build_business_use_pledge,
}


def build_answer(case: Case, document_type: str, variant: str) -> dict[str, Any]:
    if document_type not in _BUILDERS:
        raise UnsupportedDocumentTypeError(
            f"answer_builderに対応するbuilderがありません。\n"
            f"  document_type: {document_type}\n"
            f"  対応済み: {list(_BUILDERS.keys())}"
        )
    fields = _BUILDERS[document_type](case)
    return {
        "case_id": case.case_id,
        "document_type": document_type,
        "variant": variant,
        "fields": fields,
    }
