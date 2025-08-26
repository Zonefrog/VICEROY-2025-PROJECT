#!/usr/bin/env python3
"""
Debug script to test path resolution
"""

import sys
import os
from pathlib import Path
from datetime import datetime

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from polished_automation.automation_core import PathManager

def debug_paths():
    """Debug the path resolution."""
    print("=== Debugging Path Resolution ===")
    
    # Test PathManager
    path_manager = PathManager()
    
    print(f"Base directory: {path_manager.base_dir}")
    print(f"Results path: {path_manager.results_path}")
    print(f"Results path exists: {path_manager.results_path.exists()}")
    
    # Test file creation
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"test_teaching_outline_{timestamp}.txt"
    filepath = path_manager.results_path / filename
    
    print(f"Test file path: {filepath}")
    print(f"Test file parent exists: {filepath.parent.exists()}")
    
    # Try to create a test file
    try:
        test_content = f"""Test Teaching Plan
Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

This is a test file to verify path resolution.
"""
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(test_content)
        
        print(f"✅ Test file created successfully at: {filepath}")
        print(f"   File size: {filepath.stat().st_size} bytes")
        
        # List files in results directory
        print(f"\nFiles in results directory:")
        for file in path_manager.results_path.iterdir():
            if file.is_file():
                print(f"   {file.name} ({file.stat().st_size} bytes)")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating test file: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = debug_paths()
    if success:
        print("\n🎉 Path debugging completed successfully!")
    else:
        print("\n💥 Path debugging failed!")
        sys.exit(1)










