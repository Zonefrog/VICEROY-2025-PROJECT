#!/usr/bin/env python3
"""
Test script for Step 8: Slide Title Generation
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from polished_automation.automation_core import AutomationCore, SystemConfig
from logging_funcs import print_
from presentation_class import PresentationBuilder
from slide_class import SlideData

def test_step_8():
    """Test Step 8: Slide Title Generation"""
    print_("🧪 Testing Step 8: Slide Title Generation")
    
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
    
    # Mock presentation object with content from Step 7
    presentation = PresentationBuilder()
    mock_content_themes = [
        "Overview of Artificial Intelligence",
        "Types of AI Systems and their Applications",
        "AI Applications Overview across Industries",
        "Machine Learning Fundamentals",
        "Supervised Learning Algorithms",
        "Unsupervised Learning Techniques",
        "Deep Learning Basics",
        "Neural Network Architectures",
        "Training Deep Learning Models",
        "Deep Learning Applications in Various Fields",
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
    
    for i, slide_topic in enumerate(mock_slide_topics_list):
        new_slide = SlideData(title=slide_topic, content=mock_content_themes[i], sources=[])
        presentation.slides.append(new_slide)
    
    # Mock knowledge database with some research entries
    class MockKnowledgeDB:
        def __init__(self):
            self.entries = [
                {
                    "title": "AI Fundamentals",
                    "keywords": ["artificial intelligence", "basics"],
                    "text": "Artificial intelligence is a branch of computer science that aims to create intelligent machines.",
                    "link": "https://example.com/ai-basics"
                },
                {
                    "title": "Machine Learning Overview",
                    "keywords": ["machine learning", "algorithms"],
                    "text": "Machine learning is a subset of AI that enables computers to learn without being explicitly programmed.",
                    "link": "https://example.com/ml-overview"
                },
                {
                    "title": "Deep Learning Networks",
                    "keywords": ["neural networks", "deep learning"],
                    "text": "Deep learning uses neural networks with multiple layers to model complex patterns in data.",
                    "link": "https://example.com/deep-learning"
                },
                {
                    "title": "AI in Industry",
                    "keywords": ["applications", "industry"],
                    "text": "AI is being applied across various industries including healthcare, finance, and manufacturing.",
                    "link": "https://example.com/ai-industry"
                },
                {
                    "title": "Future AI Trends",
                    "keywords": ["future", "trends"],
                    "text": "Emerging trends in AI include explainable AI, edge computing, and AI ethics.",
                    "link": "https://example.com/ai-future"
                }
            ]
        
        def search(self, search_term):
            """Mock search that returns entries containing keywords from search term"""
            results = []
            search_keywords = search_term.lower().split()
            
            for entry in self.entries:
                entry_keywords = " ".join(entry["keywords"]).lower()
                if any(keyword in entry_keywords for keyword in search_keywords):
                    results.append(entry)
            
            return results
    
    # Mock generation context
    generation_context = {
        "prompt": "Create a comprehensive presentation about artificial intelligence",
        "slide_count_target": 20,
        "knowledge_db": MockKnowledgeDB()
    }
    
    try:
        # Execute Step 8
        print_("🚀 Executing Step 8...")
        updated_presentation = core.execute_step_8(generation_context, mock_slide_topics_list, presentation)
        
        # Verify results
        print_(f"✅ Step 8 completed successfully!")
        print_(f"📊 Total slides processed: {len(updated_presentation.slides)}")
        
        # Check that slides have new titles
        slides_with_new_titles = 0
        print_("\n📋 Slide Titles Generated:")
        for i, slide in enumerate(updated_presentation.slides):
            if slide.title and slide.title.strip():
                slides_with_new_titles += 1
                print_(f"   ✅ Slide {i + 1}: '{slide.title}'")
            else:
                print_(f"   ❌ Slide {i + 1}: No title generated")
        
        print_(f"📝 Slides with titles: {slides_with_new_titles}/{len(updated_presentation.slides)}")
        
        # Check overall presentation title
        if updated_presentation.title and updated_presentation.title.strip():
            print_(f"🎯 Overall presentation title: '{updated_presentation.title}'")
        else:
            print_(f"❌ No overall presentation title generated")
        
        # Verify that titles are different from original topics
        print_("\n📊 Title Comparison:")
        for i, slide in enumerate(updated_presentation.slides):
            original_topic = mock_slide_topics_list[i]
            new_title = slide.title
            if new_title != original_topic:
                print_(f"   ✅ Slide {i + 1}: '{original_topic}' → '{new_title}'")
            else:
                print_(f"   ⚠️ Slide {i + 1}: Title unchanged '{new_title}'")
        
        print_("\n🎉 Step 8 test completed successfully!")
        return True
        
    except Exception as e:
        print_(f"❌ Step 8 test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_step_8()
    sys.exit(0 if success else 1)
















