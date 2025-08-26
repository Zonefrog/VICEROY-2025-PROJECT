#!/usr/bin/env python3
"""
Run the existing example with original prompt and slide count
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from polished_automation.automation_core import AutomationCore, SystemConfig
from logging_funcs import print_

def main():
    """Run the complete pipeline with original settings"""
    print_("🚀 Running Complete Pipeline with Original Settings")
    print_("=" * 80)
    
    # Original settings
    ORIGINAL_PROMPT = """Module 2. LLM-Content
Topic 2. LLM content generation and detection (2 weeks, 2 labs)
2.1. LLM-content benchmarking datasets
2.2. LLM-content detection
2.3. Evading LLM detectors
2.4. Watermarking LLM content"""
    
    print_(f"📝 Original Prompt: {ORIGINAL_PROMPT}")
    print_(f"📊 Target Slides: 50")
    print_("=" * 80)
    
    try:
        # Create configuration
        config = SystemConfig(
            use_manual_api=False,
            slide_count_target=50
        )
        
        # Create automation core
        core = AutomationCore(config)
        if not core.initialize():
            print_("❌ Failed to initialize automation core")
            return False
        
        # Create generation context
        generation_context = {
            "prompt": ORIGINAL_PROMPT,
            "slide_count_target": 50,
            "knowledge_db": core.database_manager.database,
            "ai_role_prompt": config.ai_role_prompt
        }
        
        # Execute Steps 1-4.5
        step_1_result = core.execute_step_1(generation_context)
        print_(f"✅ Step 1: Generated {len(step_1_result['initial_topics'])} initial topics")
        
        step_2_result = core.execute_step_2(generation_context, step_1_result['initial_topics'])
        print_(f"✅ Step 2: Researched {len(step_2_result['research_entries'])} topics")
        
        step_3_result = core.execute_step_3(generation_context, step_1_result['initial_topics'], step_2_result['research_entries'])
        print_(f"✅ Step 3: Generated {len(step_3_result['additional_topics'])} additional topics")
        
        step_4_result = core.execute_step_4(generation_context, step_3_result['additional_topics'])
        print_(f"✅ Step 4: Researched {len(step_4_result['research_entries'])} additional topics")
        
        step_4_5_result = core.execute_step_4_5(generation_context, step_1_result['initial_topics'], step_3_result['additional_topics'], step_2_result['research_entries'], step_4_result['research_entries'])
        print_(f"✅ Step 4.5: Created teaching outline with {len(step_4_5_result['slide_topics_list'])} slides")
        
        # Execute Steps 5-11
        step_5_result = core.execute_step_5(generation_context, step_4_5_result['slide_topics_list'])
        print_(f"✅ Step 5: Planned presentation structure")
        
        presentation = core.execute_step_6(generation_context, step_4_5_result['slide_topics_list'])
        print_(f"✅ Step 6: Created presentation with {len(presentation.slides)} slides")
        
        updated_presentation = core.execute_step_7(generation_context, step_4_5_result["slide_topics_list"], presentation)
        print_(f"✅ Step 7: Generated content for {len(updated_presentation.slides)} slides")
        
        final_presentation = core.execute_step_8(generation_context, step_4_5_result["slide_topics_list"], updated_presentation)
        print_(f"✅ Step 8: Generated titles for {len(final_presentation.slides)} slides")
        
        enhanced_presentation = core.execute_step_9(generation_context, step_4_5_result["slide_topics_list"], step_4_5_result["teaching_outline"], final_presentation)
        print_(f"✅ Step 9: Associated sources and enhanced content for {len(enhanced_presentation.slides)} slides")
        
        finalized_presentation = core.execute_step_10(enhanced_presentation)
        print_(f"✅ Step 10: Finalized presentation with {len(finalized_presentation.slides)} total slides")
        
        saved_file_path = core.execute_step_11(finalized_presentation)
        print_(f"✅ Step 11: Presentation saved to {saved_file_path}")
        
        # Final summary
        print_("\n" + "=" * 80)
        print_("🎊 PIPELINE COMPLETE!")
        print_("=" * 80)
        print_(f"🎯 Presentation Title: '{finalized_presentation.title}'")
        print_(f"📁 Saved File: {saved_file_path}")
        print_(f"📊 Total Slides: {len(finalized_presentation.slides)}")
        print_(f"📚 Research Entries: {len(core.database_manager.database.entries)}")
        print_(f"🔢 API Calls Used: {1000 - core.api_manager.calls_remaining}")
        print_("=" * 80)
        
        return True
        
    except Exception as e:
        print_(f"❌ Pipeline execution failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
