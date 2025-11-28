# src/config_loader.py

import yaml
from pathlib import Path
from dotenv import load_dotenv
import os

# Ensure environment variables are loaded FIRST
load_dotenv()

class ConfigLoader:
    """
    A utility class to load application configuration from a YAML file.
    Enforces a single source of truth for all parameters.
    """
    def __init__(self, config_path: str = "config/app_config.yaml"):
        self.config_path = Path(config_path)
        self._config = self._load_config()

    def _load_config(self) -> dict:
        """Loads and returns the YAML configuration."""
        if not self.config_path.exists():
            raise FileNotFoundError(
                f"Configuration file not found at: {self.config_path}. "
                "Ensure 'config/app_config.yaml' was created correctly."
            )
        
        with open(self.config_path, 'r') as f:
            return yaml.safe_load(f)

    @property
    def get_config(self) -> dict:
        """Returns the full loaded configuration."""
        return self._config

    @staticmethod
    def get_api_key(key_name: str = "OPENAI_API_KEY") -> str:
        """
        Retrieves API key from environment variables.
        Fails loudly if key is missing (Anti-chaos rule).
        """
        api_key = os.getenv(key_name)
        if not api_key:
            raise ValueError(
                f"The environment variable '{key_name}' is not set. "
                "Please update your '.env' file or environment."
            )
        return api_key

# Instantiate the loader globally for use across modules
# This enforces the "Single authoritative dependency file" principle
try:
    CONFIG = ConfigLoader()
except Exception as e:
    # A simple print is fine here, Streamlit will catch it on import
    print(f"FATAL CONFIG ERROR: {e}")