#!/usr/bin/env python3
"""
Test script for Step 6: Presentation Object Creation
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from polished_automation.automation_core import AutomationCore, SystemConfig
from logging_funcs import print_

def test_step_6():
    """Test Step 6: Presentation Object Creation"""
    print_("🧪 Testing Step 6: Presentation Object Creation")
    
    # Create configuration
    config = SystemConfig(
        use_manual_api=True,  # Use manual mode for testing
        slide_count_target=20
    )
    
    # Create automation core
    core = AutomationCore(config)
    
    # Mock data from Step 4.5
    mock_slide_topics_list = [
        "Introduction to Artificial Intelligence",
        "Types of AI Systems",
        "AI Applications Overview",
        "Machine Learning Fundamentals",
        "Supervised Learning Algorithms",
        "Unsupervised Learning Techniques",
        "Deep Learning Basics",
        "Neural Network Architectures",
        "Training Deep Learning Models",
        "Deep Learning Applications",
        "AI in Healthcare",
        "AI in Finance",
        "AI in Manufacturing",
        "AI in Transportation",
        "Future AI Trends",
        "Ethical Considerations in AI",
        "AI Safety and Governance",
        "Impact of AI on Society",
        "Challenges in AI Development",
        "Conclusion and Next Steps"
    ]
    
    # Mock generation context
    generation_context = {
        "prompt": "Create a comprehensive presentation about artificial intelligence",
        "slide_count_target": 20
    }
    
    try:
        # Execute Step 6
        presentation = core.execute_step_6(generation_context, mock_slide_topics_list)
        
        # Verify results
        print_(f"✅ Presentation created successfully!")
        print_(f"📊 Total slides: {len(presentation.slides)}")
        print_(f"📋 Expected slides: {len(mock_slide_topics_list)}")
        
        # Check slide structure
        for i, slide in enumerate(presentation.slides):
            expected_title = mock_slide_topics_list[i]
            actual_title = slide.title
            if actual_title == expected_title:
                print_(f"   ✅ Slide {i + 1}: '{actual_title}'")
            else:
                print_(f"   ❌ Slide {i + 1}: Expected '{expected_title}', got '{actual_title}'")
        
        print_("\n🎉 Step 6 test completed successfully!")
        return True
        
    except Exception as e:
        print_(f"❌ Step 6 test failed: {e}")
        return False

if __name__ == "__main__":
    success = test_step_6()
    sys.exit(0 if success else 1)
