"""
Secure Bootstrap Loader
Decrypts and loads encrypted agent modules at runtime.
This is the first import in main.py - it sets up the decryption environment.
"""

import os
import sys
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Import encryption utilities
from crypto_utils import ModuleEncryptor, SecureBootstrap, cleanup_decrypted_files


class RuntimeModuleDecryptor:
    """Handles secure decryption and loading of encrypted modules at runtime."""
    
    def __init__(self):
        """Initialize decryptor with environment key."""
        self.encryption_key = os.getenv("ENCRYPTION_KEY")
        self.bootstrap = None
        self.decrypted_files = []
        
        if self.encryption_key:
            self.bootstrap = SecureBootstrap(self.encryption_key)
            logger.info("🔓 Encryption key loaded from ENCRYPTION_KEY environment variable")
        else:
            logger.warning("⚠️  ENCRYPTION_KEY not set - encrypted modules cannot be loaded")
    
    def load_agent(self, agent_name: str):
        """
        Load an encrypted agent module.
        
        Args:
            agent_name: Name of agent (e.g., 'astrologer', 'uploader', etc.)
        
        Returns:
            Decrypted module object or raises error
        """
        if not self.bootstrap:
            raise RuntimeError(
                f"Cannot load encrypted agent '{agent_name}': ENCRYPTION_KEY not set!\n"
                "Set it in GitHub Actions secrets or environment variables."
            )
        
        encrypted_path = f"agents/{agent_name}.encrypted.py"
        
        if not Path(encrypted_path).exists():
            raise FileNotFoundError(
                f"Encrypted module not found: {encrypted_path}\n"
                "Run: python crypto_utils.py encrypt-all (locally) or update CI/CD"
            )
        
        try:
            module = self.bootstrap.load_encrypted_module(encrypted_path, agent_name)
            logger.info(f"✅ Loaded encrypted agent: {agent_name}")
            return module
        except Exception as e:
            logger.error(f"❌ Failed to load encrypted agent '{agent_name}': {e}")
            raise
    
    def ensure_agents_available(self):
        """Verify all encrypted agents are accessible."""
        agents_to_check = [
            "astrologer",
            "director",
            "uploader",
            "stock_fetcher",
        ]
        
        missing = []
        for agent in agents_to_check:
            encrypted_path = f"agents/{agent}.encrypted.py"
            if not Path(encrypted_path).exists():
                missing.append(agent)
        
        if missing:
            logger.warning(
                f"⚠️  Missing encrypted modules: {', '.join(missing)}\n"
                "These should exist as .encrypted.py files"
            )
        else:
            logger.info("✅ All encrypted agent modules present")
        
        return len(missing) == 0


def initialize_secure_environment():
    """
    Call this at the very start of main.py, before importing agents.
    Validates encryption key and logs bootstrap status.
    """
    logger.info("=" * 60)
    logger.info("🔐 SECURE BOOTSTRAP LOADER - Initializing...")
    logger.info("=" * 60)
    
    decryptor = RuntimeModuleDecryptor()
    
    # Check if running in CI environment
    is_ci = os.getenv("CI", "false").lower() == "true"
    if is_ci:
        logger.info("🚀 Running in CI environment")
    
    # Validate encryption setup
    if decryptor.bootstrap:
        logger.info("✅ Encryption system ready")
        decryptor.ensure_agents_available()
    else:
        # Fallback: try to load unencrypted modules (for local development)
        logger.warning("⚠️  Running in UNENCRYPTED MODE - for development only!")
        logger.warning("   Set ENCRYPTION_KEY to use encrypted modules")
    
    logger.info("=" * 60)
    
    return decryptor


# Global decryptor instance
_global_decryptor = None


def get_decryptor():
    """Get global decryptor instance."""
    global _global_decryptor
    if _global_decryptor is None:
        _global_decryptor = initialize_secure_environment()
    return _global_decryptor


def cleanup_on_exit():
    """Clean up decrypted files at job end."""
    logger.info("🧹 Cleaning up decrypted files...")
    cleanup_decrypted_files()
    logger.info("✅ Cleanup complete")


# Register cleanup on exit
import atexit
atexit.register(cleanup_on_exit)
