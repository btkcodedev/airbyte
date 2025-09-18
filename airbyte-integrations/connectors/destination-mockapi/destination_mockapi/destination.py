#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#

import json
import logging
from pathlib import Path
from typing import Any, Iterable, Mapping

from airbyte_cdk.destinations import Destination
from airbyte_cdk.models import (
    AirbyteConnectionStatus,
    AirbyteMessage,
    ConfiguredAirbyteCatalog,
    ConnectorSpecification,
    Status,
    Type,
)

from .client import MockAPIClient
from .config import get_config_from_dict
from .writer import MockAPIWriter

logger = logging.getLogger(__name__)


class DestinationMockapi(Destination):
    def spec(self, logger: logging.Logger) -> ConnectorSpecification:
        """Return the spec for this destination."""
        spec_path = Path(__file__).parent / "spec.json"
        with open(spec_path, "r") as f:
            spec_json = json.load(f)
        
        # Use model_validate for compatibility with CDK ^4.0.0
        return ConnectorSpecification.model_validate(spec_json)

    def check(self, logger: logging.Logger, config: Mapping[str, Any]) -> AirbyteConnectionStatus:
        """Test the configuration by attempting to connect to MockAPI."""
        try:
            parsed_config = get_config_from_dict(dict(config))
            client = MockAPIClient(
                api_url=parsed_config.api_url,
                timeout=parsed_config.timeout
            )
            
            if client.test_connection():
                return AirbyteConnectionStatus(status=Status.SUCCEEDED)
            else:
                return AirbyteConnectionStatus(
                    status=Status.FAILED,
                    message="Could not connect to MockAPI endpoint"
                )
        except Exception as e:
            return AirbyteConnectionStatus(
                status=Status.FAILED,
                message=f"Connection failed: {str(e)}"
            )

    def write(
        self,
        config: Mapping[str, Any],
        configured_catalog: ConfiguredAirbyteCatalog,
        input_messages: Iterable[AirbyteMessage],
    ) -> Iterable[AirbyteMessage]:
        """Write data to MockAPI destination."""
        try:
            parsed_config = get_config_from_dict(dict(config))
            
            client = MockAPIClient(
                api_url=parsed_config.api_url,
                timeout=parsed_config.timeout
            )
            
            writer = MockAPIWriter(
                client=client,
                batch_size=parsed_config.batch_size
            )
            
            for message in input_messages:
                if message.type == Type.STATE:
                    yield message
                elif message.type == Type.RECORD:
                    writer.write_record(
                        stream_name=message.record.stream,
                        record=message.record.data
                    )
            
            writer.flush()
            
        except Exception as e:
            logger.error(f"Error writing to MockAPI: {e}")
            raise