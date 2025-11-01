import os
import hashlib

class LicenseValidator:
    def __init__(self, allowed_cpu_ids):
        self.allowed_cpu_ids = allowed_cpu_ids

    def get_cpu_id(self):
        """Get the logical CPU ID (environment variable on Vercel)."""
        cpu_id = os.getenv("DEPLOYMENT_ID")
        if not cpu_id:
            raise ValueError("DEPLOYMENT_ID not set in environment variables")
        return cpu_id

    def validate_license(self, license_key: str) -> bool:
        """Validate the license key and virtual CPU ID."""
        try:
            current_cpu_id = self.get_cpu_id()
            hashed_cpu_id = hashlib.sha256(current_cpu_id.encode()).hexdigest()
            if hashed_cpu_id not in self.allowed_cpu_ids:
                print("Invalid license or deployment environment.")
                return False
            return True
        except Exception as e:
            print(f"Error validating license: {e}")
            return False


# Example allowed hashed ID (replace with your hashed DEPLOYMENT_ID)
ALLOWED_CPU_IDS = [
    "c0a23a8593e7f835eb8f7a88dbfdad8b60db31cbf82e32b6ffcd9a2aaab78810"
]

license_validator = LicenseValidator(ALLOWED_CPU_IDS)
