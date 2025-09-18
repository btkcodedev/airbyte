import logging
from typing import Dict, Any, List
from .client import MockAPIClient

logger = logging.getLogger(__name__)

class MockAPIWriter:
    def __init__(self, client: MockAPIClient, batch_size: int = 100):
        self.client = client
        self.batch_size = batch_size
        self.buffer: Dict[str, List[Dict[str, Any]]] = {}
    
    def write_record(self, stream_name: str, record: Dict[str, Any]) -> None:
        """Write a single record to the buffer"""
        if stream_name not in self.buffer:
            self.buffer[stream_name] = []
        
        self.buffer[stream_name].append(record)
        
        # Flush if batch size reached
        if len(self.buffer[stream_name]) >= self.batch_size:
            self._flush_stream(stream_name)
    
    def flush(self) -> None:
        """Flush all buffered records"""
        for stream_name in list(self.buffer.keys()):
            if self.buffer[stream_name]:
                self._flush_stream(stream_name)
    
    def _flush_stream(self, stream_name: str) -> None:
        """Flush records for a specific stream"""
        if not self.buffer.get(stream_name):
            return
        
        records = self.buffer[stream_name]
        logger.info(f"Flushing {len(records)} records for stream {stream_name}")
        
        try:
            if stream_name.lower() == "users":
                self._write_users(records)
            elif stream_name.lower() == "deals":
                self._write_deals(records)
            else:
                logger.warning(f"Unknown stream: {stream_name}")
            
            # Clear buffer after successful write
            self.buffer[stream_name] = []
            
        except Exception as e:
            logger.error(f"Failed to write {stream_name} records: {e}")
            raise
    
    def _write_users(self, records: List[Dict[str, Any]]) -> None:
        """Write user records to MockAPI"""
        for record in records:
            try:
                mapped_user = self.map_user_data(record)
                self.client.create_user(mapped_user)
                logger.debug(f"Created user: {mapped_user.get('name', 'Unknown')}")
            except Exception as e:
                logger.error(f"Failed to create user: {e}")
                # Continue with other records
    
    def _write_deals(self, records: List[Dict[str, Any]]) -> None:
        """Write deal records to MockAPI"""
        for record in records:
            try:
                mapped_deal = self.map_deal_data(record)
                self.client.create_deal(mapped_deal)
                logger.debug(f"Created deal: {mapped_deal.get('title', 'Unknown')}")
            except Exception as e:
                logger.error(f"Failed to create deal: {e}")
    
    def map_user_data(self, data):
        """Simple user data mapping"""
        mapped = {}
        
        # Map name field
        if 'name' in data:
            mapped['name'] = data['name']
        elif 'first_name' in data and 'last_name' in data:
            mapped['name'] = f"{data['first_name']} {data['last_name']}"
        else:
            mapped['name'] = "Unknown User"
        
        # Map avatar field
        if 'avatar' in data:
            mapped['avatar'] = data['avatar']
        elif 'profile_picture' in data:
            mapped['avatar'] = data['profile_picture']
        else:
            mapped['avatar'] = "https://via.placeholder.com/150"
        
        return mapped

    def map_deal_data(self, data):
        """Simple deal data mapping"""
        mapped = {}
        
        # Map name field
        if 'name' in data:
            mapped['name'] = data['name']
        elif 'title' in data:
            mapped['name'] = data['title']
        else:
            mapped['name'] = "Unknown Deal"
        
        # Map avatar field
        if 'avatar' in data:
            mapped['avatar'] = data['avatar']
        elif 'image' in data:
            mapped['avatar'] = data['image']
        else:
            mapped['avatar'] = "https://via.placeholder.com/150"
        
        return mapped
