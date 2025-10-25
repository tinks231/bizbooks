# Vercel entry point
import sys
import os

# Add parent directory to path so we can import app
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)

# Set environment flag for Vercel
os.environ['VERCEL'] = '1'

try:
    from app import app
    print("✅ Flask app imported successfully!")
except Exception as e:
    print(f"❌ Error importing app: {str(e)}")
    import traceback
    traceback.print_exc()
    raise

# Vercel expects the WSGI app to be called 'app'
# This file imports it from our main app.py
