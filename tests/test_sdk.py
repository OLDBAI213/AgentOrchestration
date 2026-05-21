"""Tests for OrchestratorClient API key validation."""

import os
import pytest
from src.sdk.client import OrchestratorClient


class TestOrchestratorClientApiKeyValidation:
    """Test API key validation in OrchestratorClient."""

    def test_missing_api_key_raises_error(self):
        """Client should raise ValueError when API key is missing."""
        # Clear any existing AO_API_KEY
        os.environ.pop("AO_API_KEY", None)
        
        client = OrchestratorClient()
        
        with pytest.raises(ValueError) as exc_info:
            client._validate_api_key()
        
        assert "AO_API_KEY is not set" in str(exc_info.value)
        assert "https://agent-orchestrator.io/settings" in str(exc_info.value)

    def test_empty_string_api_key_raises_error(self):
        """Client should raise ValueError when API key is empty string."""
        os.environ["AO_API_KEY"] = ""
        
        client = OrchestratorClient()
        
        with pytest.raises(ValueError) as exc_info:
            client._validate_api_key()
        
        assert "AO_API_KEY is not set" in str(exc_info.value)

    def test_whitespace_only_api_key_raises_error(self):
        """Client should raise ValueError when API key is whitespace only."""
        os.environ["AO_API_KEY"] = "   "
        
        client = OrchestratorClient()
        
        with pytest.raises(ValueError) as exc_info:
            client._validate_api_key()
        
        assert "AO_API_KEY is not set" in str(exc_info.value)

    def test_valid_api_key_from_env(self):
        """Client should accept valid API key from environment variable."""
        os.environ["AO_API_KEY"] = "test-api-key-123"
        
        client = OrchestratorClient()
        
        # Should not raise
        client._validate_api_key()
        assert client.api_key == "test-api-key-123"

    def test_valid_api_key_from_constructor(self):
        """Client should accept valid API key from constructor parameter."""
        os.environ.pop("AO_API_KEY", None)
        
        client = OrchestratorClient(api_key="my-api-key")
        
        # Should not raise
        client._validate_api_key()
        assert client.api_key == "my-api-key"

    def test_constructor_overrides_env(self):
        """Constructor API key should override environment variable."""
        os.environ["AO_API_KEY"] = "env-key"
        
        client = OrchestratorClient(api_key="constructor-key")
        
        assert client.api_key == "constructor-key"

    def test_request_without_api_key_raises_error(self):
        """_request should raise ValueError when API key is missing."""
        os.environ.pop("AO_API_KEY", None)
        
        client = OrchestratorClient()
        
        with pytest.raises(ValueError) as exc_info:
            client._request("GET", "/agents")
        
        assert "AO_API_KEY is not set" in str(exc_info.value)

    def test_request_with_api_key_succeeds(self):
        """_request should proceed when API key is present."""
        os.environ["AO_API_KEY"] = "test-key"
        
        client = OrchestratorClient()
        
        # This will fail with connection error, but not with ValueError
        with pytest.raises((ValueError, Exception)) as exc_info:
            client._request("GET", "/agents")
        
        # Should NOT be a ValueError about missing API key
        assert "AO_API_KEY is not set" not in str(exc_info.value)
