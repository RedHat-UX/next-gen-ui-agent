"""
Compatibility layer for A2A SDK exceptions.

This allows local development without the A2A SDK installed while keeping
the same runtime behavior when the SDK is present.
"""

try:
    # Prefer the real SDK type when available.
    from a2a.server.errors import InvalidParamsError  # type: ignore[attr-defined]
except Exception:

    class InvalidParamsError(ValueError):
        """Fallback InvalidParamsError used when A2A SDK is not installed."""

        pass
