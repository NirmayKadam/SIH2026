"""
Base domain exceptions. Every bounded context defines its own specific exceptions
by subclassing these — but ALL failures must raise one of these, never fail silently.

Rule (ARCHITECTURE.md #2): no silent fallbacks. A caught exception must be re-raised
as one of these, logged, and propagated — never swallowed into a fake success response.
"""


class DomainError(Exception):
    """Base class for all domain-level errors across every bounded context."""


class NotFoundError(DomainError):
    """Raised when a requested entity/resource genuinely does not exist."""


class ValidationError(DomainError):
    """Raised when input violates a domain invariant."""


class ExternalServiceError(DomainError):
    """
    Raised when an infrastructure adapter (LLM API, Neo4j, Redis, file parser) fails.
    Adapters MUST raise this (or a subclass) on failure — never return a default/empty
    value that masks the failure.
    """


class RateLimitExceededError(ExternalServiceError):
    """Raised when a free-tier API rate limit is hit. Callers should retry with backoff,
    not silently skip the request."""
