# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

from __future__ import annotations

import json
import random
import re
from datetime import datetime

MAX_PRIORITY = 1000

HTTP_PREDICATES = {
    "http.method",
    "http.tls",
    "http.path",
    "http.header",
    "http.headers.keys",
    "http.headers.values",
    "http.headers.regexes",
    "http.body",
}

DNS_PREDICATES = {
    "dns.type",
}

HTTP_RESULTS = {
    "http.code",
    "http.header",
    "http.headers",
    "http.body",
    "http.passthru",
}

DNS_RESULTS = {
    "dns.data",
    "dns.type",
}

SHARED_RESULTS = {
    "var",
}

ALLOWED_PREDICATES = HTTP_PREDICATES | DNS_PREDICATES
ALLOWED_RESULTS = HTTP_RESULTS | DNS_RESULTS | SHARED_RESULTS


def parse_action_assignment(assignment: str) -> tuple[str, str]:
    if "=" not in assignment:
        raise ValueError(f"Expected action=value, got: {assignment}")
    action, value = assignment.split("=", 1)
    action_name = action.strip().lower()
    if not action_name:
        raise ValueError(f"Missing action name in assignment: {assignment}")
    return action_name, value.strip()


def validate_action_name(action_name: str, is_predicate: bool) -> None:
    action = action_name.strip().lower()
    allowed = ALLOWED_PREDICATES if is_predicate else ALLOWED_RESULTS
    if action not in allowed:
        action_type = "predicate" if is_predicate else "result"
        raise ValueError(f"Unsupported {action_type} action: {action_name}")


def normalize_protocol(protocol: str) -> str:
    normalized = protocol.strip().upper()
    if normalized not in {"HTTP", "DNS"}:
        raise ValueError("Protocol must be HTTP or DNS")
    return normalized


def infer_protocol(action_names: list[str], explicit_protocol: str | None = None) -> str:
    if explicit_protocol:
        protocol = normalize_protocol(explicit_protocol)
    else:
        protocol = ""

    seen_http = False
    seen_dns = False
    for action_name in action_names:
        action = action_name.strip().lower()
        if action.startswith("http."):
            seen_http = True
        if action.startswith("dns."):
            seen_dns = True

    if seen_http and seen_dns:
        raise ValueError("Mixed HTTP and DNS actions in one rule are not allowed")

    inferred = ""
    if seen_http:
        inferred = "HTTP"
    elif seen_dns:
        inferred = "DNS"

    if protocol:
        if inferred and inferred != protocol:
            raise ValueError(
                f"Action set implies {inferred} but --protocol is {protocol}"
            )
        return protocol

    if inferred:
        return inferred

    raise ValueError("Could not infer protocol. Provide --protocol HTTP|DNS")


def short_rule_name(protocol: str, action_hint: str | None = None) -> str:
    normalized_protocol = normalize_protocol(protocol).lower()
    hint = (action_hint or "rule").strip().lower()
    hint = re.sub(r"[^a-z0-9]+", "_", hint).strip("_") or "rule"
    hint = hint[:10]
    token = random.randint(100, 999)
    # keep names compact and human-friendly
    return f"{normalized_protocol}_{hint}_{token}"


def next_available_priority(
    existing_rules: list[dict],
    protocol: str,
    max_priority: int = MAX_PRIORITY,
) -> int:
    normalized = normalize_protocol(protocol)
    priorities: list[int] = []
    for rule in existing_rules:
        rule_protocol = str(rule.get("networkprotocol", "")).upper()
        if rule_protocol != normalized:
            continue
        priority = rule.get("priority")
        if isinstance(priority, int):
            priorities.append(priority)

    if not priorities:
        return 1

    next_priority = max(priorities) + 1
    if next_priority > max_priority:
        raise ValueError(
            f"No available priority under {max_priority} for protocol {normalized}"
        )
    return next_priority


def ensure_json_text(raw_value: str, field_name: str) -> str:
    try:
        json.loads(raw_value)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid JSON for {field_name}: {exc}") from exc
    return raw_value


def component(action_name: str, action_value: str, is_predicate: bool) -> dict:
    validate_action_name(action_name, is_predicate)
    return {
        "ispredicate": is_predicate,
        "actionname": action_name.strip().lower(),
        "actionvalue": action_value,
    }


def preview_rule(
    zone: str,
    protocol: str,
    name: str,
    priority: int,
    predicates: list[dict],
    results: list[dict],
) -> str:
    protocol_norm = normalize_protocol(protocol)
    predicate_text = " AND ".join(
        [f"{c['actionname']}={c['actionvalue']}" for c in predicates]
    ) or "(none)"
    result_text = " THEN ".join([f"{c['actionname']}={c['actionvalue']}" for c in results])
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return (
        f"[{timestamp}]\n"
        f"Zone: {zone}\n"
        f"Protocol: {protocol_norm}\n"
        f"Name: {name}\n"
        f"Priority: {priority}\n"
        f"IF {predicate_text}\n"
        f"THEN {result_text}\n"
    )
