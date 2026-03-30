# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

from __future__ import annotations

from .api_client import ApiClient


def create_rule_with_components(
    client: ApiClient,
    zone: str,
    protocol: str,
    name: str,
    priority: int,
    predicates: list[dict],
    results: list[dict],
) -> dict:
    """Create a rule and its components, rolling back on partial failures."""

    created_rule_id = ""
    created_component_ids: list[str] = []
    components = predicates + results

    try:
        created_rule = client.create_rule(
            {
                "zone": zone,
                "name": name,
                "networkprotocol": protocol,
                "priority": priority,
            }
        )
        created_rule_id = str(created_rule.get("ruleid", ""))
        if not created_rule_id:
            raise RuntimeError("API did not return ruleid for created rule")

        for component in components:
            created_component = client.add_rule_component(zone, created_rule_id, component)
            component_id = created_component.get("componentid")
            if component_id:
                created_component_ids.append(str(component_id))

        return {
            "rule": created_rule,
            "components_created": len(created_component_ids),
            "rolled_back": False,
        }
    except Exception as create_error:
        rollback_messages: list[str] = []

        if created_rule_id:
            for component_id in reversed(created_component_ids):
                try:
                    client.delete_rule_component(zone, created_rule_id, component_id)
                except Exception as rollback_component_error:
                    rollback_messages.append(
                        f"component rollback failed ({component_id}): {rollback_component_error}"
                    )

            try:
                client.delete_rule(zone, created_rule_id)
            except Exception as rollback_rule_error:
                rollback_messages.append(f"rule rollback failed: {rollback_rule_error}")

        rollback_suffix = ""
        if rollback_messages:
            rollback_suffix = " | rollback errors: " + " ; ".join(rollback_messages)

        raise RuntimeError(f"Rule creation failed: {create_error}{rollback_suffix}") from create_error
