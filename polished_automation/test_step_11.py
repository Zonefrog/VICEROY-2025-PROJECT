#!/usr/bin/env python3
"""
Test script for Step 11: Save Presentation to File
"""

import sys
import os
import tempfile
import shutil
from pathlib import Path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from polished_automation.automation_core import AutomationCore, SystemConfig
from logging_funcs import print_
from presentation_class import PresentationBuilder
from slide_class import SlideData

def test_step_11():
    """Test Step 11: Save Presentation to File"""
    print_("🧪 Testing Step 11: Save Presentation to File")
    
    # Create configuration
    config = SystemConfig(
        use_manual_api=False,  # Use automatic API mode for testing
        slide_count_target=20
    )
    
    # Create automation core and initialize it
    core = AutomationCore(config)
    if not core.initialize():
        print_("❌ Failed to initialize automation core")
        return False
    
    # Create a mock presentation with a title that needs cleaning
    presentation = PresentationBuilder()
    presentation.title = "Test Presentation: AI & ML <with> special:chars"
    
    # Add some mock slides
    for i in range(3):
        slide = SlideData(
            title=f"Test Slide {i + 1}",
            content=f"This is test content for slide {i + 1}",
            sources=[]
        )
        presentation.slides.append(slide)
    
    print_(f"📊 Test presentation: {len(presentation.slides)} slides")
    print_(f"🎯 Presentation title: '{presentation.title}'")
    
    try:
        # Execute Step 11
        print_("🚀 Executing Step 11...")
        saved_file_path = core.execute_step_11(presentation)
        
        # Verify results
        print_(f"✅ Step 11 completed successfully!")
        print_(f"📁 Saved file path: {saved_file_path}")
        
        # Check that the file was actually created
        file_path = Path(saved_file_path)
        if file_path.exists():
            print_(f"✅ File exists at: {file_path}")
            print_(f"📊 File size: {file_path.stat().st_size} bytes")
        else:
            print_(f"❌ File not found at: {file_path}")
            return False
        
        # Check filename format
        filename = file_path.name
        print_(f"📝 Filename: {filename}")
        
        # Verify filename cleaning
        if "<" in filename or ">" in filename or ":" in filename:
            print_(f"❌ Filename still contains invalid characters: {filename}")
            return False
        else:
            print_(f"✅ Filename properly cleaned")
        
        # Verify timestamp format
        if "_2025-" in filename or "_2024-" in filename:
            print_(f"✅ Timestamp properly added to filename")
        else:
            print_(f"⚠️ Timestamp format may be incorrect: {filename}")
        
        # Verify .pptx extension
        if filename.endswith(".pptx"):
            print_(f"✅ File has correct .pptx extension")
        else:
            print_(f"❌ File missing .pptx extension: {filename}")
            return False
        
        print_("\n🎉 Step 11 test completed successfully!")
        return True
        
    except Exception as e:
        print_(f"❌ Step 11 test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_step_11()
    sys.exit(0 if success else 1)













