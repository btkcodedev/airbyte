#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#

import json
import logging
import time
from typing import Any, Dict, List, Mapping
import sys
from pathlib import Path

# Add the parent directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
import requests
from destination_mockapi import DestinationMockapi
from destination_mockapi.client import MockAPIClient

from airbyte_cdk.models import (
    AirbyteMessage,
    AirbyteRecordMessage,
    AirbyteStateMessage,
    AirbyteStream,
    ConfiguredAirbyteCatalog,
    ConfiguredAirbyteStream,
    DestinationSyncMode,
    Status,
    SyncMode,
    Type,
)


TEST_USER_STREAM = "users"
TEST_DEAL_STREAM = "deals"
TEST_NAMESPACE = "test_namespace"


@pytest.fixture(name="config")
def config_fixture() -> Mapping[str, Any]:
    """Load configuration from secrets"""
    config_path = Path(__file__).parent.parent / "secrets" / "config.json"
    with open(config_path, "r") as f:
        return json.loads(f.read())


@pytest.fixture(name="invalid_config")
def invalid_config_fixture() -> Mapping[str, Any]:
    """Load invalid configuration for testing failures"""
    config_path = Path(__file__).parent / "invalid_config.json"
    with open(config_path, "r") as f:
        return json.loads(f.read())


@pytest.fixture(name="configured_catalog")
def configured_catalog_fixture() -> ConfiguredAirbyteCatalog:
    """Create configured catalog with users and deals streams"""
    # Schema matches MockAPI structure: id, createdAt, name, avatar
    shared_schema = {
        "type": "object",
        "properties": {
            "id": {"type": "string"},
            "createdAt": {"type": "string", "format": "date-time"},
            "name": {"type": "string"},
            "avatar": {"type": "string", "format": "uri"}
        },
        "required": ["name"],
        "additionalProperties": False
    }

    users_stream = ConfiguredAirbyteStream(
        stream=AirbyteStream(
            name=TEST_USER_STREAM, 
            json_schema=shared_schema, 
            supported_sync_modes=[SyncMode.full_refresh, SyncMode.incremental]
        ),
        sync_mode=SyncMode.full_refresh,
        destination_sync_mode=DestinationSyncMode.append,
    )

    deals_stream = ConfiguredAirbyteStream(
        stream=AirbyteStream(
            name=TEST_DEAL_STREAM, 
            json_schema=shared_schema, 
            supported_sync_modes=[SyncMode.full_refresh, SyncMode.incremental]
        ),
        sync_mode=SyncMode.full_refresh,
        destination_sync_mode=DestinationSyncMode.append,
    )

    return ConfiguredAirbyteCatalog(streams=[users_stream, deals_stream])


@pytest.fixture(name="client")
def client_fixture(config: Mapping[str, Any]) -> MockAPIClient:
    """Create MockAPI client for testing"""
    return MockAPIClient(
        api_url=config["api_url"],
        timeout=config.get("timeout", 30)
    )


@pytest.fixture(autouse=True)
def cleanup_test_records(config: Mapping[str, Any]):
    """Clean up test records after each test"""
    yield  # Run the test first
    
    # Cleanup after test
    client = MockAPIClient(api_url=config["api_url"])
    
    try:
        # Clean up test users
        users = client.get_users()
        for user in users:
            if "Test" in user.get("name", "") or "Batch" in user.get("name", "") or "Mixed" in user.get("name", ""):
                requests.delete(f"{config['api_url']}/users/{user['id']}")
        
        # Clean up test deals  
        deals = client.get_deals()
        for deal in deals:
            if "Test" in deal.get("name", "") or "Mapped" in deal.get("name", ""):
                requests.delete(f"{config['api_url']}/deals/{deal['id']}")
    except Exception:
        # Ignore cleanup errors
        pass


# Helper functions that were missing
def _state(data: Dict[str, Any]) -> AirbyteMessage:
    """Create state message"""
    return AirbyteMessage(type=Type.STATE, state=AirbyteStateMessage(data=data))


def _user_record(name: str = "Test User", avatar: str = "https://example.com/avatar.jpg", **extra_fields) -> AirbyteMessage:
    """Create user record message - only name and avatar are sent, id and createdAt are auto-generated"""
    data = {"name": name, "avatar": avatar}
    data.update(extra_fields)  # Allow additional fields for mapping tests
    
    return AirbyteMessage(
        type=Type.RECORD, 
        record=AirbyteRecordMessage(
            stream=TEST_USER_STREAM, 
            data=data, 
            emitted_at=int(time.time() * 1000),
            namespace=TEST_NAMESPACE
        )
    )


def _deal_record(name: str = "Test Deal", avatar: str = "https://example.com/deal.jpg", **extra_fields) -> AirbyteMessage:
    """Create deal record message - only name and avatar are sent, id and createdAt are auto-generated"""
    data = {"name": name, "avatar": avatar}
    data.update(extra_fields)  # Allow additional fields for mapping tests
    
    return AirbyteMessage(
        type=Type.RECORD, 
        record=AirbyteRecordMessage(
            stream=TEST_DEAL_STREAM, 
            data=data, 
            emitted_at=int(time.time() * 1000),
            namespace=TEST_NAMESPACE
        )
    )


def retrieve_all_users(client: MockAPIClient) -> List[Dict[str, Any]]:
    """Retrieve all users from MockAPI"""
    return client.get_users()


def retrieve_all_deals(client: MockAPIClient) -> List[Dict[str, Any]]:
    """Retrieve all deals from MockAPI"""
    return client.get_deals()


# Test functions
def test_check_valid_config(config: Mapping[str, Any]):
    """Test connection check with valid config"""
    destination = DestinationMockapi()
    outcome = destination.check(logging.getLogger("airbyte"), config)
    assert outcome.status == Status.SUCCEEDED


def test_check_invalid_config(invalid_config: Mapping[str, Any]):
    """Test connection check with invalid config"""
    destination = DestinationMockapi()
    outcome = destination.check(logging.getLogger("airbyte"), invalid_config)
    assert outcome.status == Status.FAILED


def test_spec():
    """Test that spec returns valid connector specification"""
    destination = DestinationMockapi()
    spec = destination.spec(logging.getLogger("airbyte"))
    
    assert spec.connectionSpecification is not None
    assert "api_url" in spec.connectionSpecification["properties"]
    assert spec.connectionSpecification["properties"]["api_url"]["type"] == "string"


def test_mockapi_schema_structure(client: MockAPIClient):
    """Test that MockAPI returns the expected schema structure"""
    users = retrieve_all_users(client)
    if users:
        user = users[0]
        # Verify MockAPI schema: id, createdAt, name, avatar
        assert "id" in user
        assert "createdAt" in user  
        assert "name" in user
        assert "avatar" in user
        
        # Verify types
        assert isinstance(user["id"], str)
        assert isinstance(user["createdAt"], str)
        assert isinstance(user["name"], str)


def test_write_users_append_mode(config: Mapping[str, Any], 
                                configured_catalog: ConfiguredAirbyteCatalog, 
                                client: MockAPIClient):
    """Test writing users in append mode"""
    destination = DestinationMockapi()
    
    # Get initial count
    initial_users = retrieve_all_users(client)
    initial_count = len(initial_users)
    
    # Create test messages - only sending name and avatar, MockAPI will add id and createdAt
    state_message = _state({"state": "test_users_append"})
    user_records = [
        _user_record("Test User Alpha", "https://example.com/alpha.jpg"),
        _user_record("Test User Beta", "https://example.com/beta.jpg")
    ]
    
    # Write data
    output_states = list(destination.write(config, configured_catalog, [*user_records, state_message]))
    assert [state_message] == output_states
    
    # Wait for API processing
    time.sleep(2)
    
    # Verify records were added
    final_users = retrieve_all_users(client)
    assert len(final_users) == initial_count + 2
    
    # Check that our test users exist and have the correct schema
    test_users = [user for user in final_users if "Test User" in user.get("name", "")]
    assert len(test_users) == 2
    
    for user in test_users:
        # Verify MockAPI schema structure
        assert "id" in user
        assert "createdAt" in user
        assert "name" in user
        assert "avatar" in user
        
        # Verify our data was stored correctly
        assert user["name"] in ["Test User Alpha", "Test User Beta"]


def test_write_deals_append_mode(config: Mapping[str, Any], 
                                configured_catalog: ConfiguredAirbyteCatalog, 
                                client: MockAPIClient):
    """Test writing deals in append mode"""
    destination = DestinationMockapi()
    
    # Get initial count
    initial_deals = retrieve_all_deals(client)
    initial_count = len(initial_deals)
    
    # Create test messages
    state_message = _state({"state": "test_deals_append"})
    deal_records = [
        _deal_record("Test Deal Gamma", "https://example.com/gamma.jpg"),
        _deal_record("Test Deal Delta", "https://example.com/delta.jpg")
    ]
    
    # Write data
    output_states = list(destination.write(config, configured_catalog, [*deal_records, state_message]))
    assert [state_message] == output_states
    
    # Wait for API processing
    time.sleep(2)
    
    # Verify records were added
    final_deals = retrieve_all_deals(client)
    assert len(final_deals) == initial_count + 2
    
    # Check that our test deals exist and have the correct schema
    test_deals = [deal for deal in final_deals if "Test Deal" in deal.get("name", "")]
    assert len(test_deals) == 2
    
    for deal in test_deals:
        # Verify MockAPI schema structure (same as users)
        assert "id" in deal
        assert "createdAt" in deal
        assert "name" in deal
        assert "avatar" in deal


def test_field_mapping(config: Mapping[str, Any], 
                      configured_catalog: ConfiguredAirbyteCatalog, 
                      client: MockAPIClient):
    """Test that field mapping works correctly - mapping various field names to MockAPI schema"""
    destination = DestinationMockapi()
    
    # Test various field mapping scenarios
    state_message = _state({"state": "test_field_mapping"})
    
    # User with different field names that should be mapped to MockAPI schema
    user_with_mapping = AirbyteMessage(
        type=Type.RECORD,
        record=AirbyteRecordMessage(
            stream=TEST_USER_STREAM,
            data={
                "first_name": "John",
                "last_name": "Mapper", 
                "profile_picture": "https://example.com/john-mapper.jpg"
                # These should map to: name="John Mapper", avatar="https://example.com/john-mapper.jpg"
            },
            emitted_at=int(time.time() * 1000)
        )
    )
    
    # Deal with title field that should map to name
    deal_with_mapping = AirbyteMessage(
        type=Type.RECORD,
        record=AirbyteRecordMessage(
            stream=TEST_DEAL_STREAM,
            data={
                "title": "Mapped Deal Title",
                "image": "https://example.com/mapped-deal.jpg"
                # These should map to: name="Mapped Deal Title", avatar="https://example.com/mapped-deal.jpg"
            },
            emitted_at=int(time.time() * 1000)
        )
    )
    
    # Write data
    output_states = list(destination.write(config, configured_catalog, [user_with_mapping, deal_with_mapping, state_message]))
    assert [state_message] == output_states
    
    # Wait for API processing
    time.sleep(2)
    
    # Verify field mapping worked
    users = retrieve_all_users(client)
    deals = retrieve_all_deals(client)
    
    # Check that first_name + last_name was mapped to name
    mapped_user = next((u for u in users if "John Mapper" in u.get("name", "")), None)
    assert mapped_user is not None
    assert mapped_user["name"] == "John Mapper"
    assert mapped_user["avatar"] == "https://example.com/john-mapper.jpg"
    # Verify MockAPI added id and createdAt
    assert "id" in mapped_user
    assert "createdAt" in mapped_user
    
    # Check that title was mapped to name
    mapped_deal = next((d for d in deals if "Mapped Deal Title" in d.get("name", "")), None)
    assert mapped_deal is not None
    assert mapped_deal["name"] == "Mapped Deal Title"
    assert mapped_deal["avatar"] == "https://example.com/mapped-deal.jpg"
    # Verify MockAPI added id and createdAt
    assert "id" in mapped_deal
    assert "createdAt" in mapped_deal


def test_batch_processing(config: Mapping[str, Any], 
                         configured_catalog: ConfiguredAirbyteCatalog):
    """Test that batch processing works with custom batch size"""
    # Override batch size for testing
    test_config = {**config, "batch_size": 2}
    
    destination = DestinationMockapi()
    
    # Create more records than batch size
    state_message = _state({"state": "test_batch_processing"})
    batch_records = [
        _user_record(f"Batch User {i}", f"https://example.com/batch{i}.jpg") 
        for i in range(5)
    ]
    
    # Write data
    output_states = list(destination.write(test_config, configured_catalog, [*batch_records, state_message]))
    assert [state_message] == output_states


def test_empty_record_stream(config: Mapping[str, Any], 
                           configured_catalog: ConfiguredAirbyteCatalog):
    """Test handling empty record streams"""
    destination = DestinationMockapi()
    
    # Only send state message, no records
    state_message = _state({"state": "test_empty_stream"})
    
    # Should handle empty stream gracefully
    output_states = list(destination.write(config, configured_catalog, [state_message]))
    assert [state_message] == output_states


def test_required_field_validation():
    """Test that name field is required for both users and deals"""
    # Test with missing name field - should be handled by schema mapping
    user_without_name = {
        "avatar": "https://example.com/test.jpg"
        # Missing name - schema mapper should provide default
    }
    
    # Import the mapping functions from writer
    from destination_mockapi.writer import MockAPIWriter
    
    # Create a mock writer to test the mapping functions
    writer = MockAPIWriter(client=None, batch_size=100)
    
    mapped_user = writer.map_user_data(user_without_name)
    assert "name" in mapped_user  # Should have default name
    assert mapped_user["name"] == "Unknown User"
    
    mapped_deal = writer.map_deal_data(user_without_name)
    assert "name" in mapped_deal  # Should have default name
    assert mapped_deal["name"] == "Unknown Deal"