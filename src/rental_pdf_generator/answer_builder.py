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
    }


def _build_income_certificate(case: Case) -> dict[str, Any]:
    a = case.applicant
    i = case.income
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
    }


_BUILDERS: dict[str, Callable[[Case], dict[str, Any]]] = {
    "rental_application_corporate": _build_rental_application_corporate,
    "registry_certificate": _build_registry_certificate,
    "financial_statement": _build_financial_statement,
    "business_plan": _build_business_plan,
    "rental_application_individual": _build_rental_application_individual,
    "income_certificate": _build_income_certificate,
    "identity_document": _build_identity_document,
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
