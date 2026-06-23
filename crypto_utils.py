"""
Encryption/Decryption utilities for securing sensitive Python modules.
Uses symmetric encryption (Fernet) from cryptography library.
This module is ALWAYS UNENCRYPTED as it's needed to decrypt others.
Bootstrap version with ENCRYPTION_KEY support ready.
"""

import os
import sys
import base64
import logging
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Files that should NEVER be encrypted (needed for bootstrap)
UNENCRYPTED_FILES = {
    'crypto_utils.py',
    'secure_bootstrap.py',
}


class ModuleEncryptor:
    """Encrypts and decrypts Python modules."""
    
    def __init__(self, encryption_key: str = None):
        """
        Initialize with encryption key.
        Args:
            encryption_key: Base64-encoded Fernet key. If None, reads from ENCRYPTION_KEY env var.
        """
        self.encryption_key = encryption_key or os.getenv("ENCRYPTION_KEY")
        if not self.encryption_key:
            raise ValueError(
                "ENCRYPTION_KEY not provided! Set it via:\n"
                "  export ENCRYPTION_KEY=$(python -c 'from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())')\n"
                "  Or: ENCRYPTION_KEY=$(python crypto_utils.py generate-key)"
            )
        
        try:
            self.cipher = Fernet(self.encryption_key.encode() if isinstance(self.encryption_key, str) else self.encryption_key)
        except Exception as e:
            raise ValueError(f"Invalid ENCRYPTION_KEY format: {e}")
    
    @staticmethod
    def generate_key() -> str:
        """Generate a new Fernet encryption key."""
        key = Fernet.generate_key()
        return key.decode()
    
    def encrypt_file(self, input_path: str, output_path: str = None) -> str:
        """
        Encrypt a Python file.
        
        Args:
            input_path: Path to original .py file
            output_path: Path to save encrypted file (default: .encrypted.py)
        
        Returns:
            Path to encrypted file
        """
        input_path = Path(input_path)
        
        if not input_path.exists():
            raise FileNotFoundError(f"Input file not found: {input_path}")
        
        if not input_path.suffix == '.py':
            raise ValueError(f"Expected .py file, got: {input_path}")
        
        # Skip bootstrap files that should stay unencrypted
        if input_path.name in UNENCRYPTED_FILES:
            logger.info(f"⏭️  Skipping (bootstrap): {input_path}")
            return str(input_path)
        
        # Read original file
        with open(input_path, 'rb') as f:
            plaintext = f.read()
        
        # Encrypt
        ciphertext = self.cipher.encrypt(plaintext)
        
        # Write encrypted file
        output_path = output_path or str(input_path).replace('.py', '.encrypted.py')
        output_path = Path(output_path)
        
        with open(output_path, 'wb') as f:
            f.write(ciphertext)
        
        logger.info(f"✅ Encrypted: {input_path} → {output_path}")
        
        # Remove original
        input_path.unlink()
        logger.info(f"🗑️  Removed original: {input_path}")
        
        return str(output_path)
    
    def decrypt_file(self, encrypted_path: str, output_path: str = None) -> str:
        """
        Decrypt an encrypted Python file.
        
        Args:
            encrypted_path: Path to .encrypted.py file
            output_path: Path to save decrypted file (default: removes .encrypted.py)
        
        Returns:
            Path to decrypted file
        """
        encrypted_path = Path(encrypted_path)
        
        if not encrypted_path.exists():
            raise FileNotFoundError(f"Encrypted file not found: {encrypted_path}")
        
        # Read encrypted file
        with open(encrypted_path, 'rb') as f:
            ciphertext = f.read()
        
        # Decrypt
        try:
            plaintext = self.cipher.decrypt(ciphertext)
        except Exception as e:
            raise ValueError(f"Decryption failed (invalid key?): {e}")
        
        # Write decrypted file
        if output_path is None:
            output_path = str(encrypted_path).replace('.encrypted.py', '.py')
        
        output_path = Path(output_path)
        
        with open(output_path, 'wb') as f:
            f.write(plaintext)
        
        logger.info(f"✅ Decrypted: {encrypted_path} → {output_path}")
        
        return str(output_path)
    
    def decrypt_and_load(self, encrypted_path: str) -> object:
        """
        Decrypt and dynamically load a Python module.
        
        Args:
            encrypted_path: Path to .encrypted.py file
        
        Returns:
            Decrypted module (as string)
        """
        encrypted_path = Path(encrypted_path)
        
        if not encrypted_path.exists():
            raise FileNotFoundError(f"Encrypted file not found: {encrypted_path}")
        
        # Read encrypted file
        with open(encrypted_path, 'rb') as f:
            ciphertext = f.read()
        
        # Decrypt
        try:
            plaintext = self.cipher.decrypt(ciphertext)
        except Exception as e:
            raise ValueError(f"Decryption failed (invalid key?): {e}")
        
        logger.info(f"✅ Decrypted in-memory: {encrypted_path}")
        
        return plaintext.decode('utf-8')
    
    def decrypt_all(self, root_directory: str = ".") -> int:
        """
        Decrypt ALL .encrypted.py files in a directory tree.
        
        Args:
            root_directory: Root directory to search recursively
        
        Returns:
            Number of files decrypted
        """
        root_directory = Path(root_directory)
        decrypted_count = 0
        
        # Find all encrypted files
        encrypted_files = sorted(root_directory.rglob("*.encrypted.py"))
        
        if not encrypted_files:
            logger.warning("⚠️  No .encrypted.py files found")
            return 0
        
        logger.info(f"Found {len(encrypted_files)} encrypted files")
        
        for encrypted_file in encrypted_files:
            try:
                self.decrypt_file(encrypted_file)
                decrypted_count += 1
            except Exception as e:
                logger.error(f"❌ Failed to decrypt {encrypted_file}: {e}")
        
        logger.info(f"✅ Decrypted {decrypted_count}/{len(encrypted_files)} files")
        return decrypted_count
    
    def encrypt_all(self, root_directory: str = ".") -> int:
        """
        Encrypt ALL .py files in a directory tree (except bootstrap files).
        
        Args:
            root_directory: Root directory to search recursively
        
        Returns:
            Number of files encrypted
        """
        root_directory = Path(root_directory)
        encrypted_count = 0
        
        # Find all .py files
        py_files = sorted(root_directory.rglob("*.py"))
        
        if not py_files:
            logger.warning("⚠️  No .py files found")
            return 0
        
        # Filter out already encrypted and bootstrap files
        files_to_encrypt = [
            f for f in py_files
            if not f.name.endswith('.encrypted.py') and f.name not in UNENCRYPTED_FILES
            and '.git' not in f.parts and '__pycache__' not in f.parts
        ]
        
        logger.info(f"Found {len(files_to_encrypt)} files to encrypt")
        
        for py_file in files_to_encrypt:
            try:
                self.encrypt_file(py_file)
                encrypted_count += 1
            except Exception as e:
                logger.error(f"❌ Failed to encrypt {py_file}: {e}")
        
        logger.info(f"✅ Encrypted {encrypted_count}/{len(files_to_encrypt)} files")
        return encrypted_count


class SecureBootstrap:
    """Bootstrap loader for secure module decryption at runtime."""
    
    def __init__(self, encryption_key: str = None):
        self.encryptor = ModuleEncryptor(encryption_key)
    
    def load_encrypted_module(self, module_path: str, module_name: str = None):
        """
        Load an encrypted module and inject it into sys.modules.
        
        Args:
            module_path: Path to .encrypted.py file
            module_name: Name to use in sys.modules (default: extracted from filename)
        """
        if module_name is None:
            module_name = Path(module_path).stem.replace('.encrypted', '')
        
        # Decrypt to get source code
        source_code = self.encryptor.decrypt_and_load(module_path)
        
        # Compile and create module
        code = compile(source_code, module_path, 'exec')
        
        # Create module namespace
        module_dict = {}
        exec(code, module_dict)
        
        # Create module object
        import types
        module = types.ModuleType(module_name)
        module.__dict__.update(module_dict)
        module.__file__ = module_path
        
        # Inject into sys.modules
        sys.modules[module_name] = module
        
        logger.info(f"✅ Loaded encrypted module: {module_name} from {module_path}")
        
        return module


def cleanup_decrypted_files(directory: str = ".", pattern: str = "*.encrypted.py"):
    """
    Remove all temporarily decrypted files.
    Safely removes only the decrypted versions, keeping encrypted files.
    
    Args:
        directory: Directory to scan recursively
        pattern: Files to match during cleanup
    """
    directory = Path(directory)
    
    if not directory.exists():
        logger.warning(f"Directory not found: {directory}")
        return
    
    decrypted_files = []
    
    # Find all decrypted .py files (not .encrypted.py)
    for py_file in directory.rglob("*.py"):
        # Skip encrypted files
        if py_file.name.endswith('.encrypted.py'):
            continue
        
        # Skip unencrypted bootstrap files
        if py_file.name in UNENCRYPTED_FILES:
            continue
        
        # Skip .git and other special directories
        if '.git' in py_file.parts or '__pycache__' in py_file.parts:
            continue
        
        # This is a temporarily decrypted file - mark for removal
        corresponding_encrypted = py_file.with_name(py_file.stem + '.encrypted.py')
        if corresponding_encrypted.exists():
            decrypted_files.append(py_file)
    
    # Remove decrypted files
    for py_file in decrypted_files:
        try:
            py_file.unlink()
            logger.info(f"🗑️  Removed: {py_file}")
        except Exception as e:
            logger.warning(f"⚠️  Failed to remove {py_file}: {e}")
    
    if decrypted_files:
        logger.info(f"✅ Cleanup complete ({len(decrypted_files)} files removed)")
    else:
        logger.info("✅ No decrypted files to clean up")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python crypto_utils.py generate-key                                  # Generate new encryption key")
        print("  python crypto_utils.py encrypt <file.py>                            # Encrypt a single module")
        print("  python crypto_utils.py decrypt <file.encrypted.py>                  # Decrypt a single module")
        print("  python crypto_utils.py encrypt-all                                  # Encrypt all .py files (except bootstrap)")
        print("  python crypto_utils.py decrypt-all                                  # Decrypt all .encrypted.py files")
        print("")
        print("Environment:")
        print("  ENCRYPTION_KEY: Base64-encoded Fernet key (set for encrypt/decrypt)")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "generate-key":
        key = ModuleEncryptor.generate_key()
        print(f"Generated ENCRYPTION_KEY:\n{key}\n")
        print("Store this in GitHub Secrets as: ENCRYPTION_KEY")
        print("Local usage: export ENCRYPTION_KEY='<key_above>'")
    
    elif command == "encrypt":
        if len(sys.argv) < 3:
            print("Usage: python crypto_utils.py encrypt <file.py>")
            sys.exit(1)
        
        encryptor = ModuleEncryptor()
        encryptor.encrypt_file(sys.argv[2])
    
    elif command == "decrypt":
        if len(sys.argv) < 3:
            print("Usage: python crypto_utils.py decrypt <file.encrypted.py>")
            sys.exit(1)
        
        encryptor = ModuleEncryptor()
        encryptor.decrypt_file(sys.argv[2])
    
    elif command == "encrypt-all":
        try:
            encryptor = ModuleEncryptor()
            count = encryptor.encrypt_all()
            if count == 0:
                print("⚠️  No files were encrypted (already encrypted or no files found)")
                sys.exit(0)  # Don't fail, just warn
            else:
                print(f"✅ Successfully encrypted {count} file(s)")
        except ValueError as e:
            print(f"❌ ERROR: {e}")
            print("")
            print("Troubleshooting:")
            print("  1. Verify ENCRYPTION_KEY is set: echo $ENCRYPTION_KEY")
            print("  2. Verify it's a valid Fernet key (starts with 'gAAAAAB')")
            print("  3. Generate a new key: python crypto_utils.py generate-key")
            print("  4. Add it to GitHub Secrets: https://github.com/settings/secrets/actions")
            sys.exit(1)
        except Exception as e:
            print(f"❌ ERROR: Encryption failed: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)
    
    elif command == "decrypt-all":
        encryptor = ModuleEncryptor()
        count = encryptor.decrypt_all()
        if count == 0:
            print("❌ No files decrypted")
            sys.exit(1)
    
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)
