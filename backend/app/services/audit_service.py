from datetime import datetime, timezone
from uuid import uuid4


def start_audit(feature: str) -> dict:
    return {
        "request_id": uuid4().hex,
        "feature": feature,
        "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "agents": [],
        "checks": [],
        "events": [],
        "data_sources": [],
    }


def add_agent(audit: dict, agent: str) -> None:
    if agent not in audit["agents"]:
        audit["agents"].append(agent)


def add_check(audit: dict, name: str, status: str, detail: str) -> None:
    audit["checks"].append({"name": name, "status": status, "detail": detail})


def add_event(audit: dict, agent: str, action: str, detail: str) -> None:
    add_agent(audit, agent)
    audit["events"].append({"agent": agent, "action": action, "detail": detail})


def add_data_source(audit: dict, source: str) -> None:
    if source not in audit["data_sources"]:
        audit["data_sources"].append(source)


def finalize_audit(audit: dict) -> dict:
    return audit
