"""Tests for SDK decorators — version validation regression tests."""

import pytest
from src.sdk.decorators import agent, validate_semver


class TestValidateSemver:
    """Tests for the validate_semver function."""

    def test_valid_versions(self):
        """Valid semver strings should pass."""
        assert validate_semver("1.0.0") is True
        assert validate_semver("0.1.0") is True
        assert validate_semver("10.20.30") is True
        assert validate_semver("1.0.0-alpha") is True
        assert validate_semver("1.0.0-alpha.1") is True
        assert validate_semver("1.0.0-0.3.7") is True
        assert validate_semver("1.0.0-x.7.z.92") is True
        assert validate_semver("1.0.0+20130313144700") is True
        assert validate_semver("1.0.0-beta+exp.sha.5114f85") is True
        assert validate_semver("2.1.0-beta.1+build.123") is True

    def test_invalid_versions(self):
        """Invalid version strings should fail."""
        assert validate_semver("") is False
        assert validate_semver("1") is False
        assert validate_semver("1.0") is False
        assert validate_semver("v1.0.0") is False
        assert validate_semver("1.0.0.") is False
        assert validate_semver("1.0.0.0") is False
        assert validate_semver("abc") is False
        assert validate_semver("1.2.3-beta") is False  # missing patch
        assert validate_semver("latest") is False
        assert validate_semver("main") is False


class TestAgentDecorator:
    """Tests for the agent decorator version validation."""

    def test_valid_version(self):
        """Agent with valid semver should work."""
        @agent(name="test-agent", version="1.0.0")
        class TestAgent:
            pass

        assert TestAgent.__agent_config__["version"] == "1.0.0"

    def test_valid_version_with_prerelease(self):
        """Agent with pre-release version should work."""
        @agent(name="test-agent", version="1.0.0-beta.1")
        class TestAgent:
            pass

        assert TestAgent.__agent_config__["version"] == "1.0.0-beta.1"

    def test_valid_version_with_build_metadata(self):
        """Agent with build metadata should work."""
        @agent(name="test-agent", version="1.0.0+build.123")
        class TestAgent:
            pass

        assert TestAgent.__agent_config__["version"] == "1.0.0+build.123"

    def test_invalid_version_raises_valueerror(self):
        """Agent with invalid version should raise ValueError."""
        with pytest.raises(ValueError, match="Invalid version"):
            @agent(name="test-agent", version="not-a-version")
            class TestAgent:
                pass

    def test_invalid_version_latest(self):
        """Agent with 'latest' as version should raise ValueError."""
        with pytest.raises(ValueError, match="Invalid version"):
            @agent(name="test-agent", version="latest")
            class TestAgent:
                pass

    def test_invalid_version_v_prefix(self):
        """Agent with 'v' prefix should raise ValueError."""
        with pytest.raises(ValueError, match="Invalid version"):
            @agent(name="test-agent", version="v1.0.0")
            class TestAgent:
                pass

    def test_empty_version_raises_valueerror(self):
        """Agent with empty version should raise ValueError."""
        with pytest.raises(ValueError, match="Invalid version"):
            @agent(name="test-agent", version="")
            class TestAgent:
                pass

    def test_default_version_is_valid(self):
        """Default version '1.0.0' should be accepted."""
        @agent(name="test-agent")
        class TestAgent:
            pass

        assert TestAgent.__agent_config__["version"] == "1.0.0"
