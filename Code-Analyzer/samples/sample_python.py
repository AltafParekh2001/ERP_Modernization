"""Sample Python module for testing transpilation."""

from typing import List, Optional, Dict


# Constants
MAX_RETRIES = 3
DEFAULT_TIMEOUT = 30


class Config:
    """Configuration class for the application."""
    
    def __init__(self, host: str, port: int, debug: bool = False):
        self.host = host
        self.port = port
        self.debug = debug
    
    def get_url(self) -> str:
        """Get the full URL."""
        return f"http://{self.host}:{self.port}"


class Server:
    """HTTP server implementation."""
    
    def __init__(self, config: Config):
        self.config = config
        self.running = False
    
    def start(self) -> bool:
        """Start the server."""
        if self.running:
            return False
        self.running = True
        return True
    
    def stop(self) -> bool:
        """Stop the server."""
        if not self.running:
            return False
        self.running = False
        return True
    
    def is_running(self) -> bool:
        """Check if server is running."""
        return self.running


def calculate_sum(numbers: List[int]) -> int:
    """Calculate sum of numbers."""
    total = 0
    for num in numbers:
        total += num
    return total


def find_max(numbers: List[int]) -> Optional[int]:
    """Find maximum value in list."""
    if not numbers:
        return None
    max_val = numbers[0]
    for num in numbers:
        if num > max_val:
            max_val = num
    return max_val


def process_data(data: str) -> str:
    """Process input data."""
    return data.strip().upper()
