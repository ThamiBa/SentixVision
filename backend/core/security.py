import hashlib
import os

class SecurityManager:
    """Handles basic security features like encryption placeholders and hashing."""
    
    @staticmethod
    def hash_password(password: str) -> str:
        # Simple SHA-256 for now, in a real pro app we would use bcrypt
        return hashlib.sha256(password.encode()).hexdigest()

    @staticmethod
    def encrypt_data(data: str, key: str) -> str:
        # Placeholder for AES encryption
        # For now, just a dummy transform to show the pattern
        return f"ENC:{data[::-1]}" 

    @staticmethod
    def decrypt_data(encrypted_data: str, key: str) -> str:
        if encrypted_data.startswith("ENC:"):
            return encrypted_data[4:][::-1]
        return encrypted_data
