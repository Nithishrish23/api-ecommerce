import platform
import subprocess
import hashlib

def get_cpu_id():
    """Get both the raw and hashed CPU ID of the current system."""
    if platform.system() == "Windows":
        try:
            cpu_info = subprocess.check_output("wmic cpu get processorid", shell=True).decode()
            cpu_id = cpu_info.split("\n")[1].strip()
            hashed_cpu_id = hashlib.sha256(cpu_id.encode()).hexdigest()
            return cpu_id, hashed_cpu_id
        except Exception as e:
            print(f"Error getting CPU ID: {e}")
            return None, None
    else:
        try:
            with open('/proc/cpuinfo', 'r') as f:
                for line in f:
                    if line.startswith('Serial') or line.startswith('processor'):
                        cpu_id = line.split(':')[1].strip()
                        hashed_cpu_id = hashlib.sha256(cpu_id.encode()).hexdigest()
                        return cpu_id, hashed_cpu_id
        except Exception as e:
            print(f"Error getting CPU ID: {e}")
            return None, None
    return None, None

if __name__ == "__main__":
    print("Getting your CPU ID...")
    raw_cpu_id, hashed_cpu_id = get_cpu_id()
    
    if raw_cpu_id:
        print(f"\nYour CPU ID: {raw_cpu_id}")
        print(f"Your Hashed CPU ID: {hashed_cpu_id}")
        print("\nAdd this hashed CPU ID to the ALLOWED_CPU_IDS list in license_validator.py to authorize this system.")
    else:
        print("Failed to retrieve CPU ID")

