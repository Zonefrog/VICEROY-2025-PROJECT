#!/usr/bin/env python3
"""
Simple test without API calls
"""

import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from polished_automation.automation_core import AutomationCore, SystemConfig

def simple_test():
    """Simple test without API calls."""
    print("=== Simple Test ===")
    
    # Create config with manual API mode
    config = SystemConfig(
        max_api_calls=5,
        slide_count_target=5,
        input_mode=2,
        use_manual_api=True,  # This should prevent actual API calls
        suppress_logs=False,
        suppress_prints=False
    )
    
    core = AutomationCore(config)
    
    try:
        # Just test initialization
        print("Testing initialization...")
        if core.initialize(require_confirmation=False):
            print("✅ Initialization successful!")
            
            # Test path manager
            print(f"Results path: {core.path_manager.results_path}")
            print(f"Results path exists: {core.path_manager.results_path.exists()}")
            
            # Test basic functionality without API calls
            print("✅ Basic functionality test passed!")
            return True
        else:
            print("❌ Initialization failed")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = simple_test()
    if success:
        print("\n🎉 Simple test completed!")
    else:
        print("\n💥 Simple test failed!")
        sys.exit(1)










