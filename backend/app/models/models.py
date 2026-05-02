from datetime import datetime

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.db.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, default="EazyInvest User")
    risk_profile = Column(String, default="Balanced")
    goal = Column(String, default="Long-term growth")
    time_horizon = Column(String, default="10+ years")
    planned_withdrawal_pct = Column(Float, default=0.0)
    starting_amount = Column(Float, default=0.0)
    monthly_contribution = Column(Float, default=0.0)
    contribution_stability = Column(String, default="Stable")
    behavioral_risk = Column(String, default="Hold")
    has_emergency_fund = Column(String, default="Yes")
    account_type = Column(String, default="Taxable")
    has_external_holdings = Column(String, default="No")
    ux_mode = Column(String, default="Simple")
    created_at = Column(DateTime, default=datetime.utcnow)

    holdings = relationship("Holding", back_populates="user", cascade="all, delete-orphan")


class Holding(Base):
    __tablename__ = "holdings"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    symbol = Column(String, nullable=False, index=True)
    quantity = Column(Float, nullable=False)
    avg_cost = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="holdings")
