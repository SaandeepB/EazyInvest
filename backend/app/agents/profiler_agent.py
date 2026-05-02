from app.schemas.schemas import OnboardingAnswers
from app.services.audit_service import add_event
from app.services.profile_target_service import (
    build_profile_attributes,
    build_profiler_output,
    derive_risk_profile,
)


def derive_profile_from_answers(answers: OnboardingAnswers, audit: dict | None = None) -> dict:
    risk_profile = derive_risk_profile(answers)
    if audit is not None:
        add_event(audit, "profiler_agent", "derive_profile", f"Derived {risk_profile} profile from onboarding answers.")
    return build_profile_attributes(answers, risk_profile)


def build_profiler_summary(user, holdings_count: int, audit: dict | None = None, custom_scenario_text: str | None = None) -> dict:
    summary = build_profiler_output(user, custom_scenario_text=custom_scenario_text, holdings_count=holdings_count)
    if audit is not None:
        add_event(audit, "profiler_agent", "build_summary", summary["reasoning"])
    return summary
