"""
scripts/enroll.py
"""

import sys
import pathlib

# Add project root to path
sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))

from jarvis.auth.eye_enrollment import enroll_owner

if __name__ == "__main__":
    success = enroll_owner()
    if success:
        print("Now you can boot the system by running: python main.py")
    else:
        print("Enrollment cancelled or failed. Please try again.")