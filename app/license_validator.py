import platform
import subprocess
import sys
import hashlib
from typing import List, Optional

class LicenseValidator:
    def __init__(self, allowed_cpu_ids: List[str]):
        self.allowed_cpu_ids = allowed_cpu_ids

    def get_cpu_id(self) -> str:
        """Get the CPU ID of the current system."""
        if platform.system() == "Windows":
            # Get CPU ID on Windows using wmic
            try:
                cpu_info = subprocess.check_output("wmic cpu get processorid", shell=True).decode()
                cpu_id = cpu_info.split("\n")[1].strip()
                return cpu_id
            except Exception as e:
                print(f"Error getting CPU ID: {e}")
                sys.exit(1)
        else:
            # Get CPU ID on Linux/Unix systems
            try:
                with open('/proc/cpuinfo', 'r') as f:
                    for line in f:
                        if line.startswith('Serial') or line.startswith('processor'):
                            cpu_id = line.split(':')[1].strip()
                            return cpu_id
            except Exception as e:
                print(f"Error getting CPU ID: {e}")
                sys.exit(1)
        return ""

    def validate_license(self, license_key: str) -> bool:
        """
        Validate the license key and CPU ID.
        Returns True if valid, False otherwise.
        """
        try:
            current_cpu_id = self.get_cpu_id()
            
            # Hash the CPU ID for comparison
            hashed_cpu_id = hashlib.sha256(current_cpu_id.encode()).hexdigest()
            
            # Check if the CPU ID is in the allowed list
            if hashed_cpu_id not in self.allowed_cpu_ids:
                print("Invalid CPU ID. This system is not licensed to run the server.")
                return False
                
            # Additional license key validation can be added here
            # For example, checking expiration date, features, etc.
            
            return True
            
        except Exception as e:
            print(f"Error validating license: {e}")
            return False

# List of allowed CPU IDs (hashed)
ALLOWED_CPU_IDS = [
    # Your system's CPU ID
    "0f8359ffdbe92cd4fa0b9a468bd1e427034ab40bae06d43c58f3c2a90ff6019f"
]

# Create a global instance
license_validator = LicenseValidator(ALLOWED_CPU_IDS)       