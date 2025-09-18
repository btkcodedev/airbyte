#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#

import unittest
from unittest.mock import Mock, patch

from destination_mockapi import DestinationMockapi


class TestDestinationMockapi(unittest.TestCase):
    def setUp(self):
        self.destination = DestinationMockapi()
        self.config = {
            "api_url": "https://test.mockapi.io/api/v1",
            "batch_size": 100,
            "timeout": 30
        }

    def test_spec(self):
        spec = self.destination.spec(Mock())
        self.assertIsNotNone(spec.connectionSpecification)
        self.assertIn("api_url", spec.connectionSpecification["properties"])

    @patch('destination_mockapi.client.MockAPIClient.test_connection')
    def test_check_success(self, mock_test_connection):
        mock_test_connection.return_value = True
        result = self.destination.check(Mock(), self.config)
        self.assertEqual(result.status.name, "SUCCEEDED")

    @patch('destination_mockapi.client.MockAPIClient.test_connection')
    def test_check_failure(self, mock_test_connection):
        mock_test_connection.return_value = False
        result = self.destination.check(Mock(), self.config)
        self.assertEqual(result.status.name, "FAILED")


if __name__ == '__main__':
    unittest.main()