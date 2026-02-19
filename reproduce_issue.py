import os
import sys
from dotenv import load_dotenv
from vision_skill import VisionSkill

load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    # Try to get it from arguments if not in env
    if len(sys.argv) > 1:
        api_key = sys.argv[1]
    else:
        print("No API Key found")
        sys.exit(1)

skill = VisionSkill(api_key)
file_path = "invoices_input/02. FEBRERO PRUEBA/DSP/TRACTO PARKING -CAMILO RIVERA.pdf"

print(f"Testing extraction for {file_path}")
try:
    data = skill.extract_data(file_path)
    print("Success!")
    print(data)
except Exception as e:
    print("\n--- CAUGHT EXCEPTION ---")
    print(e)
    # If it has a response attribute (like google.api_core.exceptions.InvalidArgument), print it
    if hasattr(e, 'response'):
        print(f"Response: {e.response}")
    if hasattr(e, 'args'):
        print(f"Args: {e.args}")
