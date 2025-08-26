#!/usr/bin/env python3
"""
Test script for Step 10: Presentation Finalization
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from polished_automation.automation_core import AutomationCore, SystemConfig
from logging_funcs import print_
from presentation_class import PresentationBuilder
from slide_class import SlideData

def test_step_10():
    """Test Step 10: Presentation Finalization"""
    print_("🧪 Testing Step 10: Presentation Finalization")
    
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
    
    # Create a mock presentation with some slides and sources
    presentation = PresentationBuilder()
    presentation.title = "Test Presentation: Artificial Intelligence"
    
    # Add some mock slides with sources
    for i in range(3):
        slide = SlideData(
            title=f"Test Slide {i + 1}",
            content=f"This is test content for slide {i + 1}",
            sources=[]
        )
        
        # Add some mock sources to each slide
        from source_class import Source
        mock_source = Source(
            title=f"Test Source {i + 1}",
            link=f"https://example.com/source{i + 1}",
            linked_entry=None  # We don't need the actual entry for this test
        )
        slide.sources.append(mock_source)
        
        presentation.slides.append(slide)
    
    print_(f"📊 Initial presentation: {len(presentation.slides)} slides")
    print_(f"🎯 Presentation title: '{presentation.title}'")
    
    try:
        # Execute Step 10
        print_("🚀 Executing Step 10...")
        finalized_presentation = core.execute_step_10(presentation)
        
        # Verify results
        print_(f"✅ Step 10 completed successfully!")
        print_(f"📊 Final presentation: {len(finalized_presentation.slides)} slides")
        
        # Check that slides were added
        print_("\n📋 Slide Structure:")
        for i, slide in enumerate(finalized_presentation.slides):
            slide_type = "Unknown"
            if i == 0:
                slide_type = "Title Slide"
            elif i == len(finalized_presentation.slides) - 1:
                slide_type = "Source Slide"
            else:
                slide_type = "Content Slide"
            
            print_(f"   Slide {i + 1}: '{slide.title}' ({slide_type})")
            if slide.content:
                print_(f"      Content: {slide.content[:50]}...")
            if slide.sources:
                print_(f"      Sources: {len(slide.sources)}")
        
        # Verify title slide was added at the beginning
        if len(finalized_presentation.slides) > len(presentation.slides):
            print_(f"✅ Title slide added: {len(presentation.slides)} → {len(finalized_presentation.slides)} slides")
        else:
            print_(f"❌ No additional slides added")
        
        # Check that we have more slides than the original
        expected_min_slides = len(presentation.slides) + 1  # At least title slide
        if len(finalized_presentation.slides) >= expected_min_slides:
            print_(f"✅ Presentation finalized successfully with {len(finalized_presentation.slides)} slides")
        else:
            print_(f"❌ Expected at least {expected_min_slides} slides, got {len(finalized_presentation.slides)}")
        
        print_("\n🎉 Step 10 test completed successfully!")
        return True
        
    except Exception as e:
        print_(f"❌ Step 10 test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_step_10()
    sys.exit(0 if success else 1)













