"""`local-router`: an OpenAI-compatible local gateway registered like any compat vendor."""

from coworker.providers.capabilities import capabilities_for
from coworker.providers.registry import DESCRIPTORS


def _descriptor():
    return next(d for d in DESCRIPTORS if d.name == "local-router")


def test_descriptor_defaults_to_localhost_gateway():
    d = _descriptor()
    fields = {f.key: f for f in d.fields}
    assert d.needs_key and "api_key" in fields
    assert fields["base_url"].default == "http://127.0.0.1:4000/v1"


def test_router_models_get_ollama_style_capabilities():
    # Same local models as `ollama:` — no parallel tool calls, vision by name only.
    assert capabilities_for("local-router:ornith").parallel_tool_calls is False
    assert capabilities_for("local-router:ornith-vision").vision is True
