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
    "43431a85f73e77b25a980853a087b4189ae4e5e11c3b142f830b9132ccd19ab7"
]

license_validator = LicenseValidator(ALLOWED_CPU_IDS)
