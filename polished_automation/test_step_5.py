#!/usr/bin/env python3
"""
Test script for Step 5: Presentation Structure Planning
"""

import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from automation_core import AutomationCore, SystemConfig
import ai_database

def test_step_5():
    """Test Step 5 with mock data."""
    print("🧪 Testing Step 5: Presentation Structure Planning")
    print("=" * 60)
    
    # Create configuration
    config = SystemConfig(
        max_api_calls=10,
        slide_count_target=20,
        input_mode=2,
        suppress_logs=False,
        suppress_prints=False
    )
    
    # Initialize the automation core
    core = AutomationCore(config)
    
    try:
        if core.initialize(require_confirmation=False):
            print("✅ System initialized successfully!")
            
            # Create mock generation context with some database entries
            knowledge_db = ai_database.AIDatabase("Test Database", max_size=80)
            
            # Add some mock entries
            mock_entries = [
                {
                    "title": "LLM Content Detection Methods",
                    "keywords": ["detection", "LLM", "content"],
                    "text": "Various methods exist for detecting LLM-generated content including statistical analysis, linguistic patterns, and machine learning classifiers.",
                    "link": "https://example.com/detection"
                },
                {
                    "title": "Benchmarking Datasets for LLMs",
                    "keywords": ["benchmarking", "datasets", "evaluation"],
                    "text": "Common datasets used for evaluating LLM performance include GLUE, SuperGLUE, and various domain-specific corpora.",
                    "link": "https://example.com/benchmarks"
                },
                {
                    "title": "Evasion Techniques",
                    "keywords": ["evasion", "techniques", "adversarial"],
                    "text": "Adversarial techniques used to evade LLM detection include paraphrasing, style transfer, and prompt engineering.",
                    "link": "https://example.com/evasion"
                }
            ]
            
            for entry in mock_entries:
                knowledge_db.add_entry(entry["title"], entry["keywords"], entry["text"], entry["link"])
            
            print(f"📚 Created mock database with {len(knowledge_db.entries)} entries")
            
            # Create generation context
            generation_context = {
                'prompt': 'Module 2. LLM-Content\nTopic 2. LLM content generation and detection (2 weeks, 2 labs)\n2.1. LLM-content benchmarking datasets\n2.2. LLM-content detection\n2.3. Evading LLM detectors\n2.4. Watermarking LLM content',
                'knowledge_db': knowledge_db,
                'initial_topic_count': 2,
                'database_entries_per_topic': 10,
                'slide_count_target': 20
            }
            
            print("\n🏗️ Executing Step 5...")
            step_5_data = core.execute_step_5(generation_context)
            
            print(f"\n✅ Step 5 completed successfully!")
            print(f"📊 Results:")
            print(f"   - Status: {step_5_data['status']}")
            print(f"   - Message: {step_5_data['message']}")
            print(f"   - Slide count target: {step_5_data['slide_count_target']}")
            print(f"   - Note: Detailed planning is now handled in step 4.5")
            
            return True
        else:
            print("❌ Failed to initialize system")
            return False
            
    except Exception as e:
        print(f"❌ Error in Step 5 test: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_step_5()
    if success:
        print("\n🎉 Step 5 test completed successfully!")
    else:
        print("\n⚠️ Step 5 test failed.")
        sys.exit(1)









