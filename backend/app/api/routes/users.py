from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.agents.profiler_agent import derive_profile_from_answers
from app.db.database import get_db
from app.schemas.schemas import OnboardingAnswers, UserOut, UserResponse, UserUpdate
from app.services.audit_service import finalize_audit, start_audit
from app.services.holdings_service import get_or_create_user


router = APIRouter(prefix="/users", tags=["users"])


@router.get("/profile", response_model=UserResponse)
def get_profile(db: Session = Depends(get_db)):
    audit = start_audit("users.profile")
    user = get_or_create_user(db)
    return {"user": UserOut.model_validate(user), "audit": finalize_audit(audit)}


@router.post("/onboarding", response_model=UserResponse)
def complete_onboarding(answers: OnboardingAnswers, db: Session = Depends(get_db)):
    audit = start_audit("users.onboarding")
    user = get_or_create_user(db)
    profile = derive_profile_from_answers(answers, audit)
    for field, value in profile.items():
        setattr(user, field, value)
    db.commit()
    db.refresh(user)
    return {"user": UserOut.model_validate(user), "audit": finalize_audit(audit)}


@router.put("/profile", response_model=UserResponse)
def update_profile(update: UserUpdate, db: Session = Depends(get_db)):
    audit = start_audit("users.update")
    user = get_or_create_user(db)
    for field, value in update.model_dump(exclude_none=True).items():
        setattr(user, field, value)
    db.commit()
    db.refresh(user)
    return {"user": UserOut.model_validate(user), "audit": finalize_audit(audit)}
