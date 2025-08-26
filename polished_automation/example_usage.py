"""
Example usage of the polished automation core.

This script demonstrates how to use the AutomationCore class to initialize
the system and prepare for presentation generation.
"""

import sys
import os

# Add the parent directory to the path so we can import the original modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from automation_core import AutomationCore, SystemConfig


def example_basic_usage():
    """Demonstrate basic usage of the automation core."""
    print("=== Basic Usage Example ===")
    
    # Create a basic configuration
    config = SystemConfig(
        max_api_calls=100,  # Small limit for testing
        slide_count_target=20,
        input_mode=2,  # Use hardcoded prompt
        suppress_logs=False,
        suppress_prints=False
    )
    
    # Initialize the automation core
    core = AutomationCore(config)
    
    try:
        if core.initialize(require_confirmation=False):  # Skip confirmation for demo
            print("✅ System initialized successfully!")
            
            # Get system state
            state = core.get_system_state()
            print(f"📊 System state: {state}")
            
            # Get the initial prompt
            prompt = core.get_initial_prompt()
            print(f"📝 Retrieved prompt: {prompt[:100]}...")
            
            return True
        else:
            print("❌ Failed to initialize system")
            return False
            
    except Exception as e:
        print(f"❌ Error during initialization: {e}")
        return False


def example_manual_api_mode():
    """Demonstrate manual API mode where user provides responses."""
    print("\n=== Manual API Mode Example ===")
    
    # Create configuration with manual API mode
    config = SystemConfig(
        max_api_calls=5,  # Small limit for testing
        slide_count_target=10,
        input_mode=2,  # Use hardcoded prompt
        use_manual_api=True,  # Enable manual API mode
        suppress_logs=False,
        suppress_prints=False
    )
    
    print(f"🔧 Manual API mode configuration:")
    print(f"   - Use manual API: {config.use_manual_api}")
    print(f"   - Max API calls: {config.max_api_calls}")
    print(f"   - No API key required in manual mode")
    
    # Initialize the automation core
    core = AutomationCore(config)
    
    try:
        if core.initialize(require_confirmation=False):  # Skip confirmation for demo
            print("✅ Manual API mode initialized successfully!")
            
            # Test a manual API call
            if core.api_manager:
                test_prompt = "What is 2+2? Please respond with just the number."
                print(f"\n🧪 Testing manual API call with prompt: {test_prompt}")
                
                # Note: This would normally prompt the user, but for demo we'll skip
                print("📝 (In real usage, this would prompt you to copy/paste the response)")
                
            return True
        else:
            print("❌ Failed to initialize manual API mode")
            return False
            
    except Exception as e:
        print(f"❌ Error during manual API initialization: {e}")
        return False


def example_complete_setup_flow():
    """Demonstrate the complete setup flow up to Step 1."""
    print("\n=== Complete Setup Flow Example (Up to Step 1) ===")
    
    # Create configuration
    config = SystemConfig(
        max_api_calls=50,
        slide_count_target=30,
        input_mode=2,  # Use hardcoded prompt
        suppress_logs=False,
        suppress_prints=False
    )
    
    # Initialize the automation core
    core = AutomationCore(config)
    
    try:
        if core.initialize(require_confirmation=False):
            print("✅ System initialized successfully!")
            
            # Prepare for presentation generation
            print("\n🔄 Preparing for presentation generation...")
            generation_context = core.prepare_for_presentation_generation()
            
            # Show generation parameters
            print(f"\n📊 Generation Context:")
            print(f"   - Initial topic count: {generation_context['initial_topic_count']}")
            print(f"   - Database entries per topic: {generation_context['database_entries_per_topic']}")
            print(f"   - Slide count target: {generation_context['slide_count_target']}")
            
            # Create Step 1 prompt
            print("\n📝 Creating Step 1 prompt...")
            step_1_prompt = core.create_step_1_prompt(generation_context)
            print(f"   Step 1 prompt length: {len(step_1_prompt)} characters")
            print(f"   Preview: {step_1_prompt[:150]}...")
            
            print("\n🎉 Complete setup flow successful! Ready for Step 1 execution.")
            return True
            
        else:
            print("❌ Failed to initialize system")
            return False
            
    except Exception as e:
        print(f"❌ Error in complete setup flow: {e}")
        return False


def example_step_1_and_2_execution():
    """Demonstrate Step 1 and Step 2 execution."""
    print("\n=== Step 1 and Step 2 Execution Example ===")
    
    # Create configuration with smaller limits for testing
    config = SystemConfig(
        max_api_calls=20,  # Small limit for testing
        slide_count_target=20,
        input_mode=2,  # Use hardcoded prompt
        suppress_logs=False,
        suppress_prints=False
    )
    
    # Initialize the automation core
    core = AutomationCore(config)
    
    try:
        if core.initialize(require_confirmation=False):
            print("✅ System initialized successfully!")
            
            # Prepare for presentation generation
            print("\n🔄 Preparing for presentation generation...")
            generation_context = core.prepare_for_presentation_generation()
            
            # Execute Step 1
            print("\n📝 Executing Step 1...")
            topics = core.execute_step_1(generation_context)
            print(f"✅ Step 1 completed with {len(topics)} topics: {topics}")
            
            # Execute Step 2
            print("\n🔍 Executing Step 2...")
            core.execute_step_2(generation_context, topics)
            print(f"✅ Step 2 completed. Database now has {len(generation_context['knowledge_db'].entries)} entries.")
            
            return True
            
        else:
            print("❌ Failed to initialize system")
            return False
            
    except Exception as e:
        print(f"❌ Error in Step 1/2 execution: {e}")
        return False


def example_custom_configuration():
    """Demonstrate custom configuration options."""
    print("\n=== Custom Configuration Example ===")
    
    # Create a custom configuration
    config = SystemConfig(
        max_api_calls=500,
        slide_count_target=30,
        input_mode=1,  # Manual input mode
        rewrite_prompt=True,  # Use AI to rewrite prompts
        manual_input_prompt="Create a presentation about artificial intelligence",
        suppress_logs=False,
        suppress_prints=False
    )
    
    print(f"🔧 Configuration created:")
    print(f"   - Max API calls: {config.max_api_calls}")
    print(f"   - Slide target: {config.slide_count_target}")
    print(f"   - Input mode: {config.input_mode}")
    print(f"   - Rewrite prompt: {config.rewrite_prompt}")
    
    return config


def example_component_access():
    """Demonstrate how to access individual components."""
    print("\n=== Component Access Example ===")
    
    config = SystemConfig(
        max_api_calls=50,
        slide_count_target=10,
        input_mode=2
    )
    
    core = AutomationCore(config)
    
    if core.initialize(require_confirmation=False):
        print("✅ Components available:")
        
        # Access path manager
        if core.path_manager:
            print(f"   📁 Results path: {core.path_manager.results_path}")
            print(f"   📁 Logs path: {core.path_manager.logs_path}")
        
        # Access API manager
        if core.api_manager:
            print(f"   🔑 API calls remaining: {core.api_manager.calls_remaining}")
            print(f"   🤖 OpenAI model: {core.api_manager.config.openai_model}")
        
        # Access database manager
        if core.database_manager:
            print(f"   🗄️ Database name: {core.database_manager.database.name}")
            print(f"   📊 Database max size: {core.database_manager.database.max_size}")
        
        # Access logging manager
        if core.logging_manager:
            print(f"   📝 Run name: {core.logging_manager.run_name}")
        
        return True
    else:
        print("❌ Failed to initialize components")
        return False


def example_error_handling():
    """Demonstrate error handling capabilities."""
    print("\n=== Error Handling Example ===")
    
    # Try to initialize with invalid configuration
    try:
        config = SystemConfig(
            max_api_calls=0,  # Invalid: must be > 0
            slide_count_target=50
        )
        
        core = AutomationCore(config)
        core.initialize(require_confirmation=False)
        
    except ValueError as e:
        print(f"✅ Caught expected ValueError: {e}")
        return True
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False


def example_step_1_to_3_execution():
    """Demonstrate Step 1, Step 2, and Step 3 execution."""
    print("\n=== Step 1 → Step 3 Execution Example ===")
    
    config = SystemConfig(
        max_api_calls=40,
        slide_count_target=24,
        input_mode=2,
        suppress_logs=False,
        suppress_prints=False
    )
    core = AutomationCore(config)
    
    try:
        if core.initialize(require_confirmation=False):
            print("✅ System initialized successfully!")
            
            generation_context = core.prepare_for_presentation_generation()
            
            print("\n📝 Executing Step 1...")
            topics_1 = core.execute_step_1(generation_context)
            print(f"✅ Step 1 topics: {topics_1}")
            
            print("\n🔍 Executing Step 2...")
            core.execute_step_2(generation_context, topics_1)
            print(f"✅ Step 2 completed. DB entries: {len(generation_context['knowledge_db'].entries)}")
            
            print("\n➕ Executing Step 3...")
            topics_2 = core.execute_step_3(generation_context, topics_1)
            print(f"✅ Step 3 topics: {topics_2}")
            
            return True
        else:
            print("❌ Failed to initialize system")
            return False
    except Exception as e:
        print(f"❌ Error in Step 1→3 execution: {e}")
        return False


def example_step_1_to_4_execution():
    """Demonstrate Step 1, Step 2, Step 3, and Step 4 execution."""
    print("\n=== Step 1 → Step 4 Execution Example ===")
    
    config = SystemConfig(
        max_api_calls=60,
        slide_count_target=30,
        input_mode=2,
        suppress_logs=False,
        suppress_prints=False
    )
    core = AutomationCore(config)
    
    try:
        if core.initialize(require_confirmation=False):
            print("✅ System initialized successfully!")
            
            generation_context = core.prepare_for_presentation_generation()
            
            print("\n📝 Executing Step 1...")
            topics_1 = core.execute_step_1(generation_context)
            print(f"✅ Step 1 topics: {topics_1}")
            
            print("\n🔍 Executing Step 2...")
            core.execute_step_2(generation_context, topics_1)
            print(f"✅ Step 2 completed. DB entries: {len(generation_context['knowledge_db'].entries)}")
            
            print("\n➕ Executing Step 3...")
            topics_2 = core.execute_step_3(generation_context, topics_1)
            print(f"✅ Step 3 topics: {topics_2}")
            
            print("\n🔬 Executing Step 4...")
            core.execute_step_4(generation_context, topics_2)
            print(f"✅ Step 4 completed. Total DB entries: {len(generation_context['knowledge_db'].entries)}")
            
            return True
        else:
            print("❌ Failed to initialize system")
            return False
    except Exception as e:
        print(f"❌ Error in Step 1→4 execution: {e}")
        return False


def example_step_1_to_4_5_execution():
    """Demonstrate Step 1, Step 2, Step 3, Step 4, and Step 4.5 execution."""
    print("\n=== Step 1 → Step 4.5 Execution Example ===")
    
    config = SystemConfig(
        max_api_calls=80,
        slide_count_target=20,
        input_mode=2,
        suppress_logs=False,
        suppress_prints=False
    )
    core = AutomationCore(config)
    
    try:
        if core.initialize(require_confirmation=False):
            print("✅ System initialized successfully!")
            
            generation_context = core.prepare_for_presentation_generation()
            
            print("\n📝 Executing Step 1...")
            topics_1 = core.execute_step_1(generation_context)
            print(f"✅ Step 1 topics: {topics_1}")
            
            print("\n🔍 Executing Step 2...")
            core.execute_step_2(generation_context, topics_1)
            print(f"✅ Step 2 completed. DB entries: {len(generation_context['knowledge_db'].entries)}")
            
            print("\n➕ Executing Step 3...")
            topics_2 = core.execute_step_3(generation_context, topics_1)
            print(f"✅ Step 3 topics: {topics_2}")
            
            print("\n🔬 Executing Step 4...")
            core.execute_step_4(generation_context, topics_2)
            print(f"✅ Step 4 completed. Total DB entries: {len(generation_context['knowledge_db'].entries)}")
            
            print("\n📋 Executing Step 4.5...")
            step_4_5_data = core.execute_step_4_5(generation_context)
            print(f"✅ Step 4.5 completed.")
            print(f"   - Topics: {step_4_5_data['total_topics_count']}")
            print(f"   - Slide allocation: {step_4_5_data['slide_allocation']}")
            print(f"   - Slide topics: {len(step_4_5_data['slide_topics_list'])}")
            print(f"   - Teaching plan saved to: {step_4_5_data['teaching_plan_file']}")
            
            return True
        else:
            print("❌ Failed to initialize system")
            return False
    except Exception as e:
        print(f"❌ Error in Step 1→4.5 execution: {e}")
        return False


def example_step_1_to_5_execution():
    """Demonstrate execution of Steps 1 through 5 (Presentation Structure Planning)."""
    print("\n=== Step 1 to 5 Execution Example ===")
    
    # Create configuration for Step 5 execution
    config = SystemConfig(
        max_api_calls=30,  # More calls needed for Step 5
        slide_count_target=25,
        input_mode=2,  # Use hardcoded prompt
        suppress_logs=False,
        suppress_prints=False
    )
    
    # Initialize the automation core
    core = AutomationCore(config)
    
    try:
        if core.initialize(require_confirmation=False):
            print("✅ System initialized successfully!")
            
            generation_context = core.prepare_for_presentation_generation()
            
            print("\n📝 Executing Step 1...")
            topics_1 = core.execute_step_1(generation_context)
            print(f"✅ Step 1 topics: {topics_1}")
            
            print("\n🔍 Executing Step 2...")
            core.execute_step_2(generation_context, topics_1)
            print(f"✅ Step 2 completed. DB entries: {len(generation_context['knowledge_db'].entries)}")
            
            print("\n➕ Executing Step 3...")
            topics_2 = core.execute_step_3(generation_context, topics_1)
            print(f"✅ Step 3 topics: {topics_2}")
            
            print("\n🔬 Executing Step 4...")
            core.execute_step_4(generation_context, topics_2)
            print(f"✅ Step 4 completed. Total DB entries: {len(generation_context['knowledge_db'].entries)}")
            
            print("\n📋 Executing Step 4.5...")
            step_4_5_data = core.execute_step_4_5(generation_context)
            print(f"✅ Step 4.5 completed.")
            print(f"   - Topics: {step_4_5_data['total_topics_count']}")
            print(f"   - Slide allocation: {step_4_5_data['slide_allocation']}")
            print(f"   - Slide topics: {len(step_4_5_data['slide_topics_list'])}")
            print(f"   - Teaching plan saved to: {step_4_5_data['teaching_plan_file']}")
            
            print("\n🏗️ Executing Step 5...")
            step_5_data = core.execute_step_5(generation_context)
            print(f"✅ Step 5 completed.")
            print(f"   - Status: {step_5_data['status']}")
            print(f"   - Message: {step_5_data['message']}")
            print(f"   - Slide count target: {step_5_data['slide_count_target']}")
            print(f"   - Note: Detailed planning completed in step 4.5")
            
            return True
        else:
            print("❌ Failed to initialize system")
            return False
    except Exception as e:
        print(f"❌ Error in Step 1→5 execution: {e}")
        return False


def example_step_1_to_6_execution():
    """Example: Execute Steps 1-6 (Complete presentation structure creation)"""
    print_("\n" + "="*60)
    print_("📋 Example: Steps 1-6 Execution (Complete Structure)")
    print_("="*60)
    
    try:
        # Create configuration
        config = SystemConfig(
            use_manual_api=False,  # Use automatic API mode
            slide_count_target=20,
            initial_topic_count=5,
            database_entries_per_topic=2
        )
        
        # Create automation core
        core = AutomationCore(config)
        
        # Execute Steps 1-5
        print_("🚀 Executing Steps 1-5...")
        
        # Step 1: Initial topic generation
        step_1_result = core.execute_step_1({"prompt": "Create a presentation about artificial intelligence and machine learning"})
        print_(f"✅ Step 1: Generated {len(step_1_result)} initial topics")
        
        # Step 2: Initial research
        core.execute_step_2({"prompt": "Create a presentation about artificial intelligence and machine learning"}, step_1_result)
        print_(f"✅ Step 2: Completed initial research")
        
        # Step 3: Additional topic generation
        step_3_result = core.execute_step_3({"prompt": "Create a presentation about artificial intelligence and machine learning"}, step_1_result)
        print_(f"✅ Step 3: Generated {len(step_3_result)} additional topics")
        
        # Step 4: Second research round
        core.execute_step_4({"prompt": "Create a presentation about artificial intelligence and machine learning"}, step_3_result)
        print_(f"✅ Step 4: Completed second research round")
        
        # Step 5: Presentation structure planning (simplified)
        step_5_result = core.execute_step_5({
            "prompt": "Create a presentation about artificial intelligence and machine learning",
            "slide_count_target": 20
        })
        print_(f"✅ Step 5: {step_5_result['message']}")
        
        # Step 6: Presentation object creation
        print_("🚀 Executing Step 6...")
        # Note: For this example, we'll create a simple slide topics list
        # In the real pipeline, this comes from step 4.5
        simple_slide_topics = [f"AI and ML Topic {i+1}" for i in range(20)]
        presentation = core.execute_step_6({
            "prompt": "Create a presentation about artificial intelligence and machine learning",
            "slide_count_target": 20
        }, simple_slide_topics)
        
        print_(f"✅ Step 6: Created presentation with {len(presentation.slides)} slides")
        
        # Display presentation structure
        print_("\n📊 Presentation Structure:")
        for i, slide in enumerate(presentation.slides):
            print_(f"  Slide {i+1}: {slide.title}")
        
        print_("\n🎉 Steps 1-6 completed successfully!")
        return True
        
    except Exception as e:
        print_(f"❌ Steps 1-6 execution failed: {e}")
        return False


def example_step_1_to_7_execution():
    """Example: Execute Steps 1-7 (Complete content generation)"""
    print_("\n" + "="*60)
    print_("📋 Example: Steps 1-7 Execution (Content Generation)")
    print_("="*60)
    
    try:
        # Create configuration
        config = SystemConfig(
            use_manual_api=False,  # Use automatic API mode
            slide_count_target=20
        )
        
        # Create automation core
        core = AutomationCore(config)
        
        # Execute Steps 1-6
        print_("🚀 Executing Steps 1-6...")
        
        # Step 1: Initial topic generation
        step_1_result = core.execute_step_1({"prompt": "Create a presentation about artificial intelligence and machine learning"})
        print_(f"✅ Step 1: Generated {len(step_1_result)} initial topics")
        
        # Step 2: Initial research
        core.execute_step_2({"prompt": "Create a presentation about artificial intelligence and machine learning"}, step_1_result)
        print_(f"✅ Step 2: Completed initial research")
        
        # Step 3: Additional topic generation
        step_3_result = core.execute_step_3({"prompt": "Create a presentation about artificial intelligence and machine learning"}, step_1_result)
        print_(f"✅ Step 3: Generated {len(step_3_result)} additional topics")
        
        # Step 4: Second research round
        core.execute_step_4({"prompt": "Create a presentation about artificial intelligence and machine learning"}, step_3_result)
        print_(f"✅ Step 4: Completed second research round")
        
        # Step 4.5: Detailed teaching outline and slide topics
        step_4_5_result = core.execute_step_4_5({
            "prompt": "Create a presentation about artificial intelligence and machine learning",
            "slide_count_target": 20
        })
        print_(f"✅ Step 4.5: Created detailed teaching outline with {len(step_4_5_result['slide_topics_list'])} slide topics")
        
        # Step 5: Presentation structure planning
        step_5_result = core.execute_step_5({
            "prompt": "Create a presentation about artificial intelligence and machine learning",
            "slide_count_target": 20
        })
        print_(f"✅ Step 5: Created presentation structure with {step_5_result['total_topics_count']} topics")
        
        # Step 6: Presentation object creation
        presentation = core.execute_step_6({
            "prompt": "Create a presentation about artificial intelligence and machine learning",
            "slide_count_target": 20
        }, step_4_5_result["slide_topics_list"])
        print_(f"✅ Step 6: Created presentation with {len(presentation.slides)} slides")
        
        # Step 7: Slide content generation
        print_("🚀 Executing Step 7...")
        generation_context = {
            "prompt": "Create a presentation about artificial intelligence and machine learning",
            "slide_count_target": 20,
            "knowledge_db": core.database_manager.database
        }
        
        updated_presentation = core.execute_step_7(generation_context, step_4_5_result["slide_topics_list"], presentation)
        print_(f"✅ Step 7: Generated content for {len(updated_presentation.slides)} slides")
        
        # Display sample content
        print_("\n📊 Sample Slide Content:")
        for i, slide in enumerate(updated_presentation.slides[:5]):  # Show first 5 slides
            print_(f"  Slide {i + 1}: '{slide.title}'")
            print_(f"    Content: {slide.content[:100]}...")
            print_()
        
        print_("\n🎉 Steps 1-7 completed successfully!")
        return True
        
    except Exception as e:
        print_(f"❌ Steps 1-7 execution failed: {e}")
        return False


def example_step_1_to_8_execution():
    """Example: Execute Steps 1-8 (Complete title generation)"""
    print_("\n" + "="*60)
    print_("📋 Example: Steps 1-8 Execution (Title Generation)")
    print_("="*60)
    
    try:
        # Create configuration
        config = SystemConfig(
            use_manual_api=False,  # Use automatic API mode
            slide_count_target=20
        )
        
        # Create automation core
        core = AutomationCore(config)
        
        # Execute Steps 1-7
        print_("🚀 Executing Steps 1-7...")
        
        # Step 1: Initial topic generation
        step_1_result = core.execute_step_1({"prompt": "Create a presentation about artificial intelligence and machine learning"})
        print_(f"✅ Step 1: Generated {len(step_1_result)} initial topics")
        
        # Step 2: Initial research
        core.execute_step_2({"prompt": "Create a presentation about artificial intelligence and machine learning"}, step_1_result)
        print_(f"✅ Step 2: Completed initial research")
        
        # Step 3: Additional topic generation
        step_3_result = core.execute_step_3({"prompt": "Create a presentation about artificial intelligence and machine learning"}, step_1_result)
        print_(f"✅ Step 3: Generated {len(step_3_result)} additional topics")
        
        # Step 4: Second research round
        core.execute_step_4({"prompt": "Create a presentation about artificial intelligence and machine learning"}, step_3_result)
        print_(f"✅ Step 4: Completed second research round")
        
        # Step 4.5: Detailed teaching outline and slide topics
        step_4_5_result = core.execute_step_4_5({
            "prompt": "Create a presentation about artificial intelligence and machine learning",
            "slide_count_target": 20
        })
        print_(f"✅ Step 4.5: Created detailed teaching outline with {len(step_4_5_result['slide_topics_list'])} slide topics")
        
        # Step 5: Presentation structure planning
        step_5_result = core.execute_step_5({
            "prompt": "Create a presentation about artificial intelligence and machine learning",
            "slide_count_target": 20
        })
        print_(f"✅ Step 5: Created presentation structure with {step_5_result['total_topics_count']} topics")
        
        # Step 6: Presentation object creation
        presentation = core.execute_step_6({
            "prompt": "Create a presentation about artificial intelligence and machine learning",
            "slide_count_target": 20
        }, step_4_5_result["slide_topics_list"])
        print_(f"✅ Step 6: Created presentation with {len(presentation.slides)} slides")
        
        # Step 7: Slide content generation
        generation_context = {
            "prompt": "Create a presentation about artificial intelligence and machine learning",
            "slide_count_target": 20,
            "knowledge_db": core.database_manager.database
        }
        
        updated_presentation = core.execute_step_7(generation_context, step_4_5_result["slide_topics_list"], presentation)
        print_(f"✅ Step 7: Generated content for {len(updated_presentation.slides)} slides")
        
        # Step 8: Slide title generation
        print_("🚀 Executing Step 8...")
        final_presentation = core.execute_step_8(generation_context, step_4_5_result["slide_topics_list"], updated_presentation)
        print_(f"✅ Step 8: Generated titles for {len(final_presentation.slides)} slides")
        
        # Display final results
        print_(f"\n🎯 Overall Presentation Title: '{final_presentation.title}'")
        print_("\n📊 Final Slide Titles:")
        for i, slide in enumerate(final_presentation.slides[:5]):  # Show first 5 slides
            print_(f"  Slide {i + 1}: '{slide.title}'")
            print_(f"    Content: {slide.content[:50]}...")
            print_()
        
        print_("\n🎉 Steps 1-8 completed successfully!")
        
        # Step 9: Source association and content enhancement
        print_("🚀 Executing Step 9...")
        enhanced_presentation = core.execute_step_9(generation_context, step_4_5_result["slide_topics_list"], step_4_5_result["teaching_outline"], final_presentation)
        print_(f"✅ Step 9: Associated sources and enhanced content for {len(enhanced_presentation.slides)} slides")
        
        # Display final results with sources
        print_(f"\n🎯 Overall Presentation Title: '{enhanced_presentation.title}'")
        print_("\n📊 Final Slide Details (first 3 slides):")
        for i, slide in enumerate(enhanced_presentation.slides[:3]):
            print_(f"  Slide {i + 1}: '{slide.title}'")
            print_(f"    Content: {slide.content[:100]}...")
            print_(f"    Sources: {len(slide.sources)} associated")
            for j, source in enumerate(slide.sources[:2]):  # Show first 2 sources
                print_(f"      Source {j + 1}: {source.title}")
            print_()
        
        print_("\n🎉 Steps 1-9 completed successfully!")
        return True
        
    except Exception as e:
        print_(f"❌ Steps 1-9 execution failed: {e}")
        return False


def example_step_1_to_10_execution():
    """Example: Execute Steps 1 through 10 (Presentation Finalization)"""
    try:
        print_("🚀 Example: Steps 1-10 Execution (Presentation Finalization)")
        
        # Create configuration
        config = SystemConfig(
            use_manual_api=False,
            slide_count_target=20
        )
        
        # Create automation core
        core = AutomationCore(config)
        if not core.initialize():
            print_("❌ Failed to initialize automation core")
            return False
        
        # Execute Steps 1-4.5 (same as previous example)
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
        
        # Execute Steps 5-9 (same as previous example)
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
        
        # Execute Step 10: Presentation finalization
        print_("🚀 Executing Step 10...")
        finalized_presentation = core.execute_step_10(enhanced_presentation)
        print_(f"✅ Step 10: Finalized presentation with {len(finalized_presentation.slides)} total slides")
        
        # Display final results
        print_(f"\n🎯 Overall Presentation Title: '{finalized_presentation.title}'")
        print_(f"📊 Total Slides: {len(finalized_presentation.slides)}")
        print_("\n📋 Final Slide Structure:")
        for i, slide in enumerate(finalized_presentation.slides):
            slide_type = "Content"
            if i == 0:
                slide_type = "Title"
            elif i == len(finalized_presentation.slides) - 1:
                slide_type = "Sources"
            
            print_(f"  Slide {i + 1}: '{slide.title}' ({slide_type})")
        
        print_("\n🎉 Steps 1-10 completed successfully!")
        return True
        
    except Exception as e:
        print_(f"❌ Steps 1-10 execution failed: {e}")
        return False


def example_step_1_to_9_execution():
    """Example: Execute Steps 1 through 9 (Source Association and Content Enhancement)"""
    try:
        print_("🚀 Example: Steps 1-9 Execution (Source Association and Content Enhancement)")
        
        # Create configuration
        config = SystemConfig(
            use_manual_api=False,
            slide_count_target=20
        )
        
        # Create automation core
        core = AutomationCore(config)
        if not core.initialize():
            print_("❌ Failed to initialize automation core")
            return False
        
        # Execute Steps 1-4.5 (same as previous example)
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
        
        # Execute Steps 5-8 (same as previous example)
        step_5_result = core.execute_step_5(generation_context, step_4_5_result['slide_topics_list'])
        print_(f"✅ Step 5: Planned presentation structure")
        
        presentation = core.execute_step_6(generation_context, step_4_5_result['slide_topics_list'])
        print_(f"✅ Step 6: Created presentation with {len(presentation.slides)} slides")
        
        updated_presentation = core.execute_step_7(generation_context, step_4_5_result["slide_topics_list"], presentation)
        print_(f"✅ Step 7: Generated content for {len(updated_presentation.slides)} slides")
        
        final_presentation = core.execute_step_8(generation_context, step_4_5_result["slide_topics_list"], updated_presentation)
        print_(f"✅ Step 8: Generated titles for {len(final_presentation.slides)} slides")
        
        # Execute Step 9: Source association and content enhancement
        print_("🚀 Executing Step 9...")
        enhanced_presentation = core.execute_step_9(generation_context, step_4_5_result["slide_topics_list"], step_4_5_result["teaching_outline"], final_presentation)
        print_(f"✅ Step 9: Associated sources and enhanced content for {len(enhanced_presentation.slides)} slides")
        
        # Execute Step 10: Presentation finalization
        print_("🚀 Executing Step 10...")
        finalized_presentation = core.execute_step_10(enhanced_presentation)
        print_(f"✅ Step 10: Finalized presentation with {len(finalized_presentation.slides)} total slides")
        
        # Execute Step 11: Save presentation to file
        print_("🚀 Executing Step 11...")
        saved_file_path = core.execute_step_11(finalized_presentation)
        print_(f"✅ Step 11: Presentation saved to {saved_file_path}")
        
        # Display final results
        print_(f"\n🎯 Overall Presentation Title: '{finalized_presentation.title}'")
        print_(f"📁 Saved File: {saved_file_path}")
        print_(f"📊 Total Slides: {len(finalized_presentation.slides)}")
        
        print_("\n🎉 Steps 1-11 completed successfully!")
        return True
        
    except Exception as e:
        print_(f"❌ Steps 1-11 execution failed: {e}")
        return False


def example_step_1_to_11_execution():
    """Example: Execute Steps 1 through 11 (Complete Pipeline)"""
    try:
        print_("🚀 Example: Steps 1-11 Execution (Complete Pipeline)")
        
        # Create configuration
        config = SystemConfig(
            use_manual_api=False,
            slide_count_target=20
        )
        
        # Create automation core
        core = AutomationCore(config)
        if not core.initialize():
            print_("❌ Failed to initialize automation core")
            return False
        
        # Execute Steps 1-4.5 (same as previous example)
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
        
        # Execute Steps 5-10 (same as previous example)
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
        
        # Execute Step 11: Save presentation to file
        print_("🚀 Executing Step 11...")
        saved_file_path = core.execute_step_11(finalized_presentation)
        print_(f"✅ Step 11: Presentation saved to {saved_file_path}")
        
        # Display final results
        print_(f"\n🎯 Overall Presentation Title: '{finalized_presentation.title}'")
        print_(f"📁 Saved File: {saved_file_path}")
        print_(f"📊 Total Slides: {len(finalized_presentation.slides)}")
        
        print_("\n🎉 Complete pipeline (Steps 1-11) finished successfully!")
        print_("🎊 Presentation generation complete!")
        return True
        
    except Exception as e:
        print_(f"❌ Steps 1-11 execution failed: {e}")
        return False


def main():
    """Run all examples."""
    print("🚀 VICEROY-2025-PROJECT: Polished Automation Core Examples")
    print("=" * 60)
    
    # Example 1: Basic usage
    success1 = example_basic_usage()
    
    # Example 2: Complete setup flow
    success2 = example_complete_setup_flow()
    
    # Example 3: Step 1 and 2 execution
    success3 = example_step_1_and_2_execution()
    
    # Example 4: Manual API mode
    success4 = example_manual_api_mode()
    
    # Example 5: Custom configuration
    config = example_custom_configuration()
    
    # Example 6: Component access
    success6 = example_component_access()
    
    # Example 7: Error handling
    success7 = example_error_handling()
    
    # Example 8: Step 1 to 3 execution
    success8 = example_step_1_to_3_execution()
    
    # Example 9: Step 1 to 4 execution
    success9 = example_step_1_to_4_execution()
    
    # Example 10: Step 1 to 4.5 execution
    success10 = example_step_1_to_4_5_execution()
    
    # Example 11: Step 1 to 5 execution
    success11 = example_step_1_to_5_execution()
    
    # Example 12: Step 1 to 6 execution
    success12 = example_step_1_to_6_execution()
    
    # Example 13: Step 1 to 7 execution
    success13 = example_step_1_to_7_execution()
    
    # Example 14: Step 1 to 8 execution
    success14 = example_step_1_to_8_execution()
    
    # Example 15: Step 1 to 9 execution
    success15 = example_step_1_to_9_execution()
    
    # Example 16: Step 1 to 10 execution
    success16 = example_step_1_to_10_execution()
    
    # Example 17: Step 1 to 11 execution (Complete Pipeline)
    success17 = example_step_1_to_11_execution()
    
    # Summary
    print("\n" + "=" * 60)
    print("📋 Example Summary:")
    print(f"   Basic usage: {'✅' if success1 else '❌'}")
    print(f"   Complete setup flow: {'✅' if success2 else '❌'}")
    print(f"   Step 1 and 2 execution: {'✅' if success3 else '❌'}")
    print(f"   Manual API mode: {'✅' if success4 else '❌'}")
    print(f"   Custom config: ✅")
    print(f"   Component access: {'✅' if success6 else '❌'}")
    print(f"   Error handling: {'✅' if success7 else '❌'}")
    print(f"   Step 1 to 3 execution: {'✅' if success8 else '❌'}")
    print(f"   Step 1 to 4 execution: {'✅' if success9 else '❌'}")
    print(f"   Step 1 to 4.5 execution: {'✅' if success10 else '❌'}")
    print(f"   Step 1 to 5 execution: {'✅' if success11 else '❌'}")
    print(f"   Step 1 to 6 execution: {'✅' if success12 else '❌'}")
    print(f"   Step 1 to 7 execution: {'✅' if success13 else '❌'}")
    print(f"   Step 1 to 8 execution: {'✅' if success14 else '❌'}")
    print(f"   Step 1 to 9 execution: {'✅' if success15 else '❌'}")
    print(f"   Step 1 to 10 execution: {'✅' if success16 else '❌'}")
    print(f"   Step 1 to 11 execution: {'✅' if success17 else '❌'}")
    
    if all([success1, success2, success3, success4, success6, success7, success8, success9, success10, success11, success12, success13, success14, success15, success16, success17]):
        print("\n🎉 All examples completed successfully!")
        return 0
    else:
        print("\n⚠️ Some examples failed. Check the output above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
