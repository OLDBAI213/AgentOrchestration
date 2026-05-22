"""SDK decorators for agent definitions."""

import functools
import re
import asyncio
from typing import Any, Callable, Dict, Optional

# Semantic version pattern: MAJOR.MINOR.PATCH with optional pre-release/build metadata
_SEMVER_PATTERN = re.compile(
    r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)"
    r"(?:-((?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*)(?:\.(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*))*))?"
    r"(?:\+([0-9a-zA-Z-]+(?:\.[0-9a-zA-Z-]+)*))?$"
)


def validate_semver(version: str) -> bool:
    """Validate that a version string follows semantic versioning (SemVer 2.0.0).

    Args:
        version: Version string to validate (e.g., "1.0.0", "2.1.0-beta.1").

    Returns:
        True if valid semver, False otherwise.
    """
    return bool(_SEMVER_PATTERN.match(version))


def task(name: Optional[str] = None, retries: int = 0, timeout: int = 300):
    """Decorator for marking a method as an agent task handler."""
    def decorator(func: Callable) -> Callable:
        func.__task_config__ = {
            "name": name or func.__name__,
            "retries": retries,
            "timeout": timeout,
        }

        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                result = await asyncio.wait_for(
                    func(*args, **kwargs),
                    timeout=timeout,
                )
                return result
            except asyncio.TimeoutError:
                raise TimeoutError(f"Task {name or func.__name__} timed out after {timeout}s")

        return wrapper
    return decorator


def agent(name: str, version: str = "1.0.0", description: str = ""):
    """Decorator for marking a class as an agent definition.

    Args:
        name: Agent name.
        version: Semantic version string (e.g., "1.0.0", "2.1.0-beta.1").
        description: Agent description.

    Raises:
        ValueError: If version is not a valid semantic version string.
    """
    if not validate_semver(version):
        raise ValueError(
            f"Invalid version '{version}' for agent '{name}'. "
            f"Version must follow semantic versioning (SemVer 2.0.0), "
            f"e.g., '1.0.0', '2.1.0-beta.1', '0.1.0+build.123'."
        )

    def decorator(cls: type) -> type:
        cls.__agent_config__ = {
            "name": name,
            "version": version,
            "description": description,
        }
        return cls
    return decorator


def on_event(event_type: str):
    """Decorator for marking a method as an event handler."""
    def decorator(func: Callable) -> Callable:
        func.__event_handler__ = event_type

        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            return await func(*args, **kwargs)

        return wrapper
    return decorator
