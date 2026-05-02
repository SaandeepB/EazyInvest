from sqlalchemy.orm import Session

from app.models.models import Holding, User
from app.services.audit_service import add_event
from app.services.syndicated_data_service import normalize_symbol
from app.utils.defaults import DEFAULT_USER_PROFILE, PRIMARY_USER_ID


def get_or_create_user(db: Session) -> User:
    user = db.query(User).filter(User.id == PRIMARY_USER_ID).first()
    if not user:
        user = User(id=PRIMARY_USER_ID, **DEFAULT_USER_PROFILE)
        db.add(user)
        db.commit()
        db.refresh(user)
    return user


def list_holdings(db: Session, user_id: int = PRIMARY_USER_ID) -> list[Holding]:
    return db.query(Holding).filter(Holding.user_id == user_id).order_by(Holding.updated_at.desc()).all()


def create_holding(db: Session, symbol: str, quantity: float, avg_cost: float, audit: dict) -> Holding:
    user = get_or_create_user(db)
    normalized = normalize_symbol(symbol)
    holding = Holding(user_id=user.id, symbol=normalized, quantity=quantity, avg_cost=avg_cost)
    db.add(holding)
    db.commit()
    db.refresh(holding)
    add_event(audit, "holdings_service", "create_holding", f"Created holding {holding.symbol} with quantity {holding.quantity}.")
    return holding


def update_holding(db: Session, holding_id: int, quantity: float | None, avg_cost: float | None, audit: dict) -> Holding | None:
    holding = db.query(Holding).filter(Holding.id == holding_id, Holding.user_id == PRIMARY_USER_ID).first()
    if holding is None:
        return None
    if quantity is not None:
        holding.quantity = quantity
    if avg_cost is not None:
        holding.avg_cost = avg_cost
    db.commit()
    db.refresh(holding)
    add_event(audit, "holdings_service", "update_holding", f"Updated holding {holding.symbol}.")
    return holding


def delete_holding(db: Session, holding_id: int, audit: dict) -> Holding | None:
    holding = db.query(Holding).filter(Holding.id == holding_id, Holding.user_id == PRIMARY_USER_ID).first()
    if holding is None:
        return None
    db.delete(holding)
    db.commit()
    add_event(audit, "holdings_service", "delete_holding", f"Deleted holding {holding.symbol}.")
    return holding
