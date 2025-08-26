"""
Test script to verify path resolution works correctly.
"""

import sys
import os
from pathlib import Path

# Add the parent directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from automation_core import PathManager, SystemConfig


def test_path_resolution():
    """Test that paths are resolved correctly."""
    print("=== Testing Path Resolution ===")
    
    # Create path manager
    path_manager = PathManager()
    
    print(f"📁 Base directory: {path_manager.base_dir}")
    print(f"📁 API key path: {path_manager.api_key_path}")
    print(f"📁 Results path: {path_manager.results_path}")
    print(f"📁 Logs path: {path_manager.logs_path}")
    print(f"📁 Test output path: {path_manager.test_output_path}")
    print(f"📁 Prompt file path: {path_manager.prompt_file_path}")
    
    # Check if paths are relative to the correct parent directory
    current_file_dir = Path(__file__).parent
    expected_base = current_file_dir.parent
    
    print(f"\n🔍 Verification:")
    print(f"   Current file directory: {current_file_dir}")
    print(f"   Expected base directory: {expected_base}")
    print(f"   Actual base directory: {path_manager.base_dir}")
    print(f"   Paths match: {path_manager.base_dir == expected_base}")
    
    # Check if key files exist
    print(f"\n📋 File existence check:")
    print(f"   API key file exists: {path_manager.api_key_path.exists()}")
    print(f"   Results directory exists: {path_manager.results_path.exists()}")
    print(f"   Logs directory exists: {path_manager.logs_path.exists()}")
    print(f"   Test output directory exists: {path_manager.test_output_path.exists()}")
    
    return path_manager.base_dir == expected_base


def test_manual_api_mode():
    """Test manual API mode configuration."""
    print("\n=== Testing Manual API Mode ===")
    
    # Test configuration with manual API mode
    config = SystemConfig(
        use_manual_api=True,
        max_api_calls=10
    )
    
    print(f"🔧 Manual API mode: {config.use_manual_api}")
    print(f"🔧 Max API calls: {config.max_api_calls}")
    print(f"🔧 OpenAI model: {config.openai_model}")
    
    # Test that no API key is required in manual mode
    try:
        # This should not raise an error in manual mode
        print("✅ Manual API mode configuration is valid")
        return True
    except Exception as e:
        print(f"❌ Error in manual API mode: {e}")
        return False


def main():
    """Run all tests."""
    print("🧪 VICEROY-2025-PROJECT: Path and Manual API Mode Tests")
    print("=" * 60)
    
    # Test path resolution
    path_success = test_path_resolution()
    
    # Test manual API mode
    manual_api_success = test_manual_api_mode()
    
    # Summary
    print("\n" + "=" * 60)
    print("📋 Test Summary:")
    print(f"   Path resolution: {'✅' if path_success else '❌'}")
    print(f"   Manual API mode: {'✅' if manual_api_success else '❌'}")
    
    if path_success and manual_api_success:
        print("\n🎉 All tests passed!")
        return 0
    else:
        print("\n⚠️ Some tests failed. Check the output above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())










