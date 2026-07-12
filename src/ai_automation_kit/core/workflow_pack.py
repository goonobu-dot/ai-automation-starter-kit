from __future__ import annotations

import copy
import hashlib
import json
import string
from importlib import resources
from pathlib import Path
from typing import Any, Dict


PACK_KEYS = {
    "schema_version",
    "id",
    "display_name",
    "category",
    "period_type",
    "risk_tier",
    "business_outcome",
    "inputs",
    "questions",
    "prompt_template_id",
    "allowed_prompt_variables",
    "outputs",
    "approval",
    "prohibited_actions",
    "success_metrics",
}
QUESTION_TYPES = {"short_text", "long_text", "single_choice", "confirmation"}
PERIOD_TYPES = {"day", "month"}
PROHIBITED_REQUIRED = {
    "external_send",
    "publish",
    "payment",
    "production_write",
    "self_approve",
}
RISK_TIERS = {"low", "medium", "high"}
OUTPUT_SCHEMA_KEYS = {"missing_questions", "draft_markdown"}
PROMPT_TEMPLATE_KEYS = {"template_id", "allowed_variables", "template"}


def load_bundled_pack(pack_id: str) -> dict:
    payload = _load_trusted_json(pack_id=pack_id, kind="pack")
    if payload.get("id") != pack_id:
        raise ValueError("workflow pack id does not match manifest entry")
    return copy.deepcopy(validate_pack(payload))


def list_bundled_packs() -> list[dict]:
    return [load_bundled_pack(pack_id) for pack_id in _load_manifest()]


def load_bundled_output_schema(pack_id: str) -> dict:
    schema = _load_trusted_json(pack_id=pack_id, kind="output_schema")
    if set(schema.get("properties", {})) != OUTPUT_SCHEMA_KEYS:
        raise ValueError("workflow output schema must expose only missing_questions and draft_markdown")
    if set(schema.get("required", [])) != OUTPUT_SCHEMA_KEYS:
        raise ValueError("workflow output schema must require missing_questions and draft_markdown")
    if schema.get("additionalProperties") is not False:
        raise ValueError("workflow output schema must disable additional properties")
    return copy.deepcopy(schema)


def load_bundled_prompt_template(pack_id: str) -> dict:
    pack = load_bundled_pack(pack_id)
    prompt = _load_trusted_json(pack_id=pack_id, kind="prompt_template")
    if set(prompt) != PROMPT_TEMPLATE_KEYS:
        raise ValueError("workflow prompt template fields are invalid")
    if prompt["template_id"] != pack["prompt_template_id"]:
        raise ValueError("workflow prompt template id does not match the pack")
    if prompt["allowed_variables"] != pack["allowed_prompt_variables"]:
        raise ValueError("workflow prompt template variables do not match the pack")
    template = prompt["template"]
    _require_non_empty_string(template, "workflow prompt template")
    placeholders = []
    try:
        parsed = string.Formatter().parse(template)
        for _, field_name, format_spec, conversion in parsed:
            if field_name is None:
                continue
            if format_spec or conversion or not field_name:
                raise ValueError("workflow prompt template placeholder is invalid")
            placeholders.append(field_name)
    except (ValueError, KeyError, IndexError) as exc:
        raise ValueError("workflow prompt template placeholder is invalid") from exc
    if set(placeholders) != set(prompt["allowed_variables"]):
        raise ValueError("workflow prompt template contains an undeclared placeholder")
    return copy.deepcopy(prompt)


def validate_pack(payload: dict) -> dict:
    if not isinstance(payload, dict) or set(payload) != PACK_KEYS:
        raise ValueError("workflow pack fields do not match schema version 1")
    if payload["schema_version"] != 1 or payload["risk_tier"] not in RISK_TIERS:
        raise ValueError("unsupported workflow pack schema or risk tier")

    _require_non_empty_string(payload["id"], "workflow pack id")
    _validate_display_name(payload["display_name"])
    _require_non_empty_string(payload["category"], "workflow pack category")
    _validate_period_type(payload["period_type"])
    _require_non_empty_string(payload["business_outcome"], "workflow pack business outcome")
    _validate_inputs(payload["inputs"])
    _validate_questions(payload["questions"])
    _require_non_empty_string(payload["prompt_template_id"], "workflow pack prompt template id")
    _validate_string_list(payload["allowed_prompt_variables"], "workflow prompt variables")
    _validate_outputs(payload["outputs"])
    _validate_approval(payload["approval"])
    _validate_prohibited_actions(payload["prohibited_actions"])
    _validate_string_list(payload["success_metrics"], "workflow success metrics")
    return payload


def _load_trusted_json(pack_id: str, kind: str) -> dict:
    manifest = _load_manifest()
    entry = manifest.get(pack_id)
    if not isinstance(entry, dict):
        raise ValueError(f"unknown workflow pack: {pack_id}")

    if kind == "pack":
        file_key = "pack_file"
        hash_key = "pack_sha256"
    elif kind == "output_schema":
        file_key = "output_schema_file"
        hash_key = "output_schema_sha256"
    elif kind == "prompt_template":
        file_key = "prompt_template_file"
        hash_key = "prompt_template_sha256"
    else:
        raise ValueError(f"unsupported workflow pack resource kind: {kind}")

    resource_name = entry.get(file_key)
    expected_hash = entry.get(hash_key)
    if not isinstance(resource_name, str) or not isinstance(expected_hash, str):
        raise ValueError("workflow pack manifest entry is invalid")

    payload_bytes = _read_pack_resource_bytes(resource_name)
    actual_hash = hashlib.sha256(payload_bytes).hexdigest()
    if actual_hash != expected_hash:
        raise ValueError("workflow pack manifest hash mismatch")

    try:
        payload = json.loads(payload_bytes.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError("workflow pack resource is not valid utf-8 json") from exc
    if not isinstance(payload, dict):
        raise ValueError("workflow pack resource must be a JSON object")
    return payload


def _load_manifest() -> Dict[str, Dict[str, Any]]:
    manifest_bytes = _read_pack_resource_bytes("manifest.json")
    try:
        manifest = json.loads(manifest_bytes.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError("workflow pack manifest is not valid utf-8 json") from exc
    if not isinstance(manifest, dict):
        raise ValueError("workflow pack manifest must be a JSON object")
    return manifest


def _read_pack_resource_bytes(name: str) -> bytes:
    return resources.files("ai_automation_kit").joinpath("packs", name).read_bytes()


def _validate_display_name(display_name: Any) -> None:
    if not isinstance(display_name, dict) or set(display_name) != {"ja", "en"}:
        raise ValueError("workflow display name must include ja and en")
    for label in display_name.values():
        _require_non_empty_string(label, "workflow display label")


def _validate_period_type(period_type: Any) -> None:
    if period_type not in PERIOD_TYPES:
        raise ValueError("workflow period_type is not supported")


def _validate_inputs(inputs: Any) -> None:
    if not isinstance(inputs, list) or not inputs:
        raise ValueError("workflow inputs must be a non-empty list")
    for item in inputs:
        if not isinstance(item, dict) or set(item) != {"id", "required", "accepted_extensions"}:
            raise ValueError("workflow input fields are invalid")
        _require_non_empty_string(item["id"], "workflow input id")
        if not isinstance(item["required"], bool):
            raise ValueError("workflow input required must be boolean")
        if not isinstance(item["accepted_extensions"], list) or not item["accepted_extensions"]:
            raise ValueError("workflow input accepted_extensions must be a non-empty list")
        for extension in item["accepted_extensions"]:
            if not isinstance(extension, str) or not extension.startswith(".") or "/" in extension or "\\" in extension:
                raise ValueError("workflow input accepted_extensions must be simple dot extensions")


def _validate_questions(questions: Any) -> None:
    if not isinstance(questions, list) or not questions:
        raise ValueError("workflow questions must be a non-empty list")
    for question in questions:
        if not isinstance(question, dict):
            raise ValueError("workflow question must be an object")
        question_type = question.get("type")
        if question_type not in QUESTION_TYPES:
            raise ValueError("workflow question type is not supported")
        allowed_keys = {"id", "type", "required"}
        if question_type in {"short_text", "long_text"}:
            allowed_keys.add("max_length")
        elif question_type == "single_choice":
            allowed_keys.add("options")
        if set(question) != allowed_keys:
            raise ValueError("workflow question fields are invalid")
        _require_non_empty_string(question["id"], "workflow question id")
        if not isinstance(question["required"], bool):
            raise ValueError("workflow question required must be boolean")
        if "max_length" in question and (not isinstance(question["max_length"], int) or question["max_length"] <= 0):
            raise ValueError("workflow question max_length must be a positive integer")
        if "options" in question:
            _validate_string_list(question["options"], "workflow question options")


def _validate_outputs(outputs: Any) -> None:
    if not isinstance(outputs, list) or not outputs:
        raise ValueError("workflow outputs must be a non-empty list")
    for output in outputs:
        if not isinstance(output, dict) or set(output) != {"id", "relative_path", "max_bytes"}:
            raise ValueError("workflow output fields are invalid")
        _require_non_empty_string(output["id"], "workflow output id")
        _validate_relative_output_path(output["relative_path"])
        if not isinstance(output["max_bytes"], int) or output["max_bytes"] <= 0:
            raise ValueError("workflow output max_bytes must be a positive integer")


def _validate_relative_output_path(value: Any) -> None:
    if not isinstance(value, str) or not value:
        raise ValueError("workflow output path must be a non-empty string")
    if "/" in value or "\\" in value:
        raise ValueError("workflow output must be one safe relative filename")
    relative = Path(value)
    if relative.is_absolute() or ".." in relative.parts or len(relative.parts) != 1 or value in {".", ".."}:
        raise ValueError("workflow output must be one safe relative filename")


def _validate_approval(approval: Any) -> None:
    if not isinstance(approval, dict) or set(approval) != {"required", "role"}:
        raise ValueError("workflow approval fields are invalid")
    if not isinstance(approval["required"], bool):
        raise ValueError("workflow approval required must be boolean")
    _require_non_empty_string(approval["role"], "workflow approval role")


def _validate_prohibited_actions(actions: Any) -> None:
    _validate_string_list(actions, "workflow prohibited actions")
    if not PROHIBITED_REQUIRED <= set(actions):
        raise ValueError("workflow pack is missing prohibited actions")


def _validate_string_list(value: Any, label: str) -> None:
    if not isinstance(value, list) or not value:
        raise ValueError(f"{label} must be a non-empty list")
    for item in value:
        _require_non_empty_string(item, label)


def _require_non_empty_string(value: Any, label: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{label} must be a non-empty string")
