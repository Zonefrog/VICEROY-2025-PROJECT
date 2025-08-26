#!/usr/bin/env python3
"""
Minimal test to isolate the hanging issue
"""

print("Starting minimal test...")

try:
    print("Importing sys...")
    import sys
    print("✅ sys imported")
    
    print("Importing os...")
    import os
    print("✅ os imported")
    
    print("Importing pathlib...")
    from pathlib import Path
    print("✅ pathlib imported")
    
    print("Importing datetime...")
    from datetime import datetime
    print("✅ datetime imported")
    
    print("Importing dataclasses...")
    from dataclasses import dataclass
    print("✅ dataclasses imported")
    
    print("Importing typing...")
    from typing import Optional, Dict, Any
    print("✅ typing imported")
    
    print("Importing openai...")
    from openai import OpenAI
    print("✅ openai imported")
    
    print("Setting up path...")
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    print("✅ path setup complete")
    
    print("Importing ai_database...")
    import ai_database
    print("✅ ai_database imported")
    
    print("Importing logging_funcs...")
    from logging_funcs import print_, print_2
    print("✅ logging_funcs imported")
    
    print("🎉 All imports successful!")
    
except Exception as e:
    print(f"❌ Error during import: {e}")
    import traceback
    traceback.print_exc()










