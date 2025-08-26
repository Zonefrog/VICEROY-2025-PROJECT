#!/usr/bin/env python3
"""
Test script for Step 4.5 functionality
"""

import sys
import os
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from polished_automation.automation_core import AutomationCore, SystemConfig
from logging_funcs import print_

def test_step_4_5():
    """Test Step 4.5 functionality with minimal setup."""
    print_("=== Testing Step 4.5 ===")
    
    # Create minimal config
    config = SystemConfig(
        max_api_calls=10,
        slide_count_target=8,
        input_mode=2,
        suppress_logs=False,
        suppress_prints=False
    )
    
    core = AutomationCore(config)
    
    try:
        # Initialize system
        if core.initialize(require_confirmation=False):
            print_("✅ System initialized successfully!")
            
            # Prepare generation context
            generation_context = core.prepare_for_presentation_generation()
            print_("✅ Generation context prepared!")
            
            # Test Step 4.5 directly
            print_("\n🔬 Testing Step 4.5...")
            step_4_5_data = core.execute_step_4_5(generation_context)
            
            print_(f"✅ Step 4.5 completed successfully!")
            print_(f"   - Topics: {step_4_5_data['total_topics_count']}")
            print_(f"   - Slide allocation: {step_4_5_data['slide_allocation']}")
            print_(f"   - Slide topics: {len(step_4_5_data['slide_topics_list'])}")
            print_(f"   - Teaching plan file: {step_4_5_data['teaching_plan_file']}")
            
            # Check if file actually exists
            filepath = Path(step_4_5_data['teaching_plan_file'])
            if filepath.exists():
                print_(f"✅ File exists at: {filepath}")
                print_(f"   File size: {filepath.stat().st_size} bytes")
            else:
                print_(f"❌ File does not exist at: {filepath}")
            
            return True
        else:
            print_("❌ Failed to initialize system")
            return False
            
    except Exception as e:
        print_(f"❌ Error in Step 4.5 test: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_step_4_5()
    if success:
        print_("\n🎉 Step 4.5 test completed successfully!")
    else:
        print_("\n💥 Step 4.5 test failed!")
        sys.exit(1)










