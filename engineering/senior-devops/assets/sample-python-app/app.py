"""Minimal sample service used by pipeline_generator.py examples."""


def health() -> dict:
    """Return the health payload."""
    return {"status": "ok"}
