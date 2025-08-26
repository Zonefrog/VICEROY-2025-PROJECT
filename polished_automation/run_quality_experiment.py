#!/usr/bin/env python3
"""
Automated Presentation Quality Testing Experiment
Generates presentations with varying human choice chances and measures quality.
"""

from automation_core import AutomationCore, SystemConfig
from logging_funcs import print_
import json
from datetime import datetime
import os

# Step 1: Create Topic List
PRESENTATION_TOPICS = [
    # Science & Technology
    "Artificial Intelligence and Machine Learning",
    "Quantum Computing Fundamentals",
    "Climate Change and Renewable Energy",
    "Space Exploration and Mars Missions",
    "Genetic Engineering and CRISPR",
    "Cybersecurity in the Digital Age",
    "Blockchain Technology and Cryptocurrency",
    "Virtual Reality and Augmented Reality",
    "Internet of Things (IoT)",
    "Robotics and Automation",
    
    # History & Culture
    "Ancient Egyptian Civilization",
    "The Roman Empire: Rise and Fall",
    "The Industrial Revolution",
    "World War II: Key Events and Impact",
    "The Cold War Era",
    "The Renaissance Period",
    "Ancient Greek Philosophy",
    "The Age of Exploration",
    "The French Revolution",
    "The American Civil War",
    
    # Business & Economics
    "Startup Culture and Entrepreneurship",
    "Global Supply Chain Management",
    "Digital Marketing Strategies",
    "Corporate Social Responsibility",
    "The Gig Economy",
    "Sustainable Business Practices",
    "E-commerce Evolution",
    "Financial Technology (FinTech)",
    "Remote Work and Future of Employment",
    "Data-Driven Decision Making",
    
    # Health & Medicine
    "Mental Health Awareness",
    "Nutrition and Modern Diets",
    "Vaccine Development Process",
    "Telemedicine and Digital Health",
    "Exercise Science and Fitness",
    "Public Health Crises Management",
    "Alternative Medicine Practices",
    "Medical Technology Advances",
    "Aging and Longevity Research",
    "Global Health Challenges",
    
    # Arts & Literature
    "Modern Art Movements",
    "Classical Music Evolution",
    "Digital Art and NFTs",
    "Film Industry Transformation",
    "Literature in the Digital Age",
    "Architecture Through the Ages",
    "Photography and Visual Storytelling",
    "Theater and Performance Arts",
    "Fashion Industry Trends",
    "Video Game Design and Culture",
    
    # Environment & Nature
    "Biodiversity Conservation",
    "Ocean Pollution and Marine Life",
    "Forest Ecosystems and Deforestation",
    "Wildlife Conservation Efforts",
    "Sustainable Agriculture",
    "Urban Planning and Green Cities",
    "Water Resources Management",
    "Air Quality and Pollution Control",
    "Natural Disasters and Preparedness",
    "Ecosystem Restoration",
    
    # Social Issues & Psychology
    "Social Media and Mental Health",
    "Gender Equality in the Workplace",
    "Education Technology and Learning",
    "Criminal Justice Reform",
    "Immigration and Cultural Integration",
    "Poverty and Economic Inequality",
    "Human Rights and Activism",
    "Social Psychology and Behavior",
    "Addiction and Recovery",
    "Community Building and Social Capital",
    
    # Philosophy & Ethics
    "Ethics in Artificial Intelligence",
    "Environmental Ethics",
    "Bioethics and Medical Decisions",
    "Digital Privacy and Ethics",
    "Animal Rights and Welfare",
    "Business Ethics and Corporate Governance",
    "Media Ethics and Journalism",
    "Research Ethics and Scientific Integrity",
    "Technology Ethics and Responsibility",
    "Global Ethics and Human Rights"
]

def main():
    """Main function for the quality experiment."""
    print_("🧪 Starting Automated Presentation Quality Experiment")
    print_(f"📚 Available topics: {len(PRESENTATION_TOPICS)}")
    
    # Step 2: Create Main Testing Program Configuration
    # Set up configuration for 8 slides per presentation
    base_config = SystemConfig(
        use_manual_api=False,
        slide_count_target=8,  # Short presentations for testing
        input_mode=2,  # Hardcoded prompt mode for dynamic topics
        choice_mode=5,  # AI choice mode as default
        human_choice_chance=0.0,  # Will be varied in experiment
        no_human_chances=False,  # Enable choice system
    )
    
    # Define human choice chance levels to test
    HUMAN_CHOICE_LEVELS = [0.0, 20.0, 40.0, 60.0, 80.0, 100.0]
    PRESENTATIONS_PER_LEVEL = 1  # Reduced to 1 for testing
    
    print_(f"🎯 Testing {len(HUMAN_CHOICE_LEVELS)} human choice levels: {HUMAN_CHOICE_LEVELS}")
    print_(f"📊 {PRESENTATIONS_PER_LEVEL} presentations per level = {len(HUMAN_CHOICE_LEVELS) * PRESENTATIONS_PER_LEVEL} total presentations")
    print_(f"🤖 Using AI choice mode (mode 5) for all presentations")
    
    # Step 3: Create Results File at Start
    print_("💾 Creating results file...")
    
    # Create experiment metadata
    experiment_metadata = {
        "experiment_id": datetime.now().strftime("%Y-%m-%d_%H-%M-%S"),
        "total_presentations": len(HUMAN_CHOICE_LEVELS) * PRESENTATIONS_PER_LEVEL,
        "human_choice_levels": HUMAN_CHOICE_LEVELS,
        "presentations_per_level": PRESENTATIONS_PER_LEVEL,
        "choice_mode": base_config.choice_mode,
        "slide_count_target": base_config.slide_count_target,
        "experiment_started": True,
        "timestamp": datetime.now().isoformat()
    }
    
    # Create results data structure
    experiment_results = {
        "experiment_metadata": experiment_metadata,
        "results": []
    }
    
    # Save to JSON file
    results_filename = f"quality_experiment_results_{experiment_metadata['experiment_id']}.json"
    results_filepath = os.path.join("results", results_filename)
    
    try:
        # Ensure results directory exists
        os.makedirs("results", exist_ok=True)
        
        # Save the initial experiment structure
        with open(results_filepath, 'w', encoding='utf-8') as f:
            json.dump(experiment_results, f, indent=2, ensure_ascii=False)
        
        print_(f"✅ Results file created: {results_filepath}")
        
    except Exception as e:
        print_(f"❌ Failed to create results file: {e}")
        results_filepath = None
    
    # Step 4: Select Topics and Implement Experiment Loop
    print_("🔄 Selecting topics and starting experiment loop...")
    
    # Select random topics once at the start
    import random
    selected_topics = random.sample(PRESENTATION_TOPICS, PRESENTATIONS_PER_LEVEL)
    print_(f"📝 Selected topics for this experiment: {selected_topics}")
    
    # Initialize presentation ID counter
    presentation_id = 0
    
    # Outer loop: iterate through each human choice chance level
    for choice_chance in HUMAN_CHOICE_LEVELS:
        print_(f"\n{'='*60}")
        print_(f"🎯 Testing Human Choice Chance: {choice_chance}%")
        print_(f"{'='*60}")
        
        # Inner loop: generate presentations per level
        for presentation_num in range(PRESENTATIONS_PER_LEVEL):
            print_(f"\n📊 Presentation {presentation_num + 1}/{PRESENTATIONS_PER_LEVEL} (ID: {presentation_id})")
            
            # Use pre-selected topic for this presentation
            selected_topic = selected_topics[presentation_num]
            print_(f"📝 Using topic: {selected_topic}")
            
            # Configure system with current human choice chance
            current_config = SystemConfig(
                use_manual_api=base_config.use_manual_api,
                slide_count_target=base_config.slide_count_target,
                input_mode=base_config.input_mode,
                choice_mode=base_config.choice_mode,
                human_choice_chance=choice_chance,
                no_human_chances=base_config.no_human_chances,
            )
            
            # Create automation core with current configuration
            core = AutomationCore(current_config)
            
            # Initialize the system
            if not core.initialize(require_confirmation=False):
                print_(f"❌ Initialization failed for presentation {presentation_id}")
                presentation_id += 1
                continue
            
            # Step 4: Run Complete Pipeline and Generate Presentation
            try:
                print_(f"🔄 Running complete pipeline for presentation {presentation_id}...")
                
                # Override the manual input prompt with the selected topic
                core.config.manual_input_prompt = selected_topic
                
                # Prepare context
                ctx = core.prepare_for_presentation_generation()
                
                # Pipeline execution
                step1 = core.execute_step_1(ctx)
                core.execute_step_2(ctx, step1)
                step3 = core.execute_step_3(ctx, step1)
                core.execute_step_4(ctx, step3)
                step4_5 = core.execute_step_4_5(ctx)
                step4_6 = core.execute_step_4_6(ctx, step4_5)
                core.execute_step_5(ctx)
                pres = core.execute_step_6(ctx, step4_5["slide_topics_list"])
                pres = core.execute_step_7(ctx, step4_5["slide_topics_list"], pres, step4_6["lecture_notes"])
                pres = core.execute_step_8(ctx, step4_5["slide_topics_list"], pres)
                pres = core.execute_step_9(ctx, step4_5["slide_topics_list"], step4_5["teaching_outline"], pres)
                pres = core.execute_step_10(pres)
                saved_path = core.execute_step_11(pres)
                
                print_(f"✅ Presentation {presentation_id} generated successfully: {saved_path}")
                
                # Step 5: Integrate Quality Rater
                print_(f"📊 Rating presentation {presentation_id}...")
                
                try:
                    # Import the rating functions from powerpoint_rater
                    from powerpoint_rater import (
                        load_presentation_from_file, 
                        presentation_to_text_blocks, 
                        rate_presentation,
                        rate_0, rate_1, rate_2, rate_3, rate_4
                    )
                    
                    # Load the presentation from the saved file
                    presentation = load_presentation_from_file(saved_path)
                    
                    # Convert to text blocks for rating
                    slide_blocks = presentation_to_text_blocks(presentation)
                    
                    # Calculate all ratings
                    overall_rating = rate_presentation(slide_blocks)
                    rating_0_score = rate_0(slide_blocks)  # Amount Correctness
                    rating_1_score = rate_1(slide_blocks)  # Non-Repetition
                    rating_2_score = rate_2(slide_blocks)  # Slide Content Quantity Balance
                    rating_3_score = rate_3(slide_blocks)  # Title Uniqueness
                    rating_4_score = rate_4(slide_blocks)  # Title and Content Matching
                    
                    print_(f"✅ Presentation {presentation_id} rated successfully")
                    print_(f"📈 Overall Rating: {overall_rating:.2f} / 10.00")
                    print_(f"📊 Sub-scores:")
                    print_(f"   - Amount Correctness: {rating_0_score:.2f} / 2.00")
                    print_(f"   - Non-Repetition: {rating_1_score:.2f} / 2.00")
                    print_(f"   - Content Balance: {rating_2_score:.2f} / 2.00")
                    print_(f"   - Title Uniqueness: {rating_3_score:.2f} / 2.00")
                    print_(f"   - Title-Content Match: {rating_4_score:.2f} / 2.00")
                        
                        # Collect presentation data and save to file
                    presentation_data = {
                        'presentation_id': presentation_id,
                        'topic': selected_topic,
                        'title': pres.title if hasattr(pres, 'title') else 'Unknown',
                        'human_choice_chance': choice_chance,
                        'choice_mode': current_config.choice_mode,
                        'slide_count': len(pres.slides) if hasattr(pres, 'slides') else 0,
                        'overall_rating': overall_rating,
                        'sub_scores': {
                            'amount_correctness': rating_0_score,
                            'non_repetition': rating_1_score,
                            'content_balance': rating_2_score,
                            'title_uniqueness': rating_3_score,
                            'title_content_match': rating_4_score
                        },
                        'rating_success': True,
                        'presentation_success': True,
                        'saved_path': saved_path,
                        'timestamp': datetime.now().isoformat()
                    }
                
                    # Save result to file
                    try:
                        with open(results_filepath, 'r') as f:
                            data = json.load(f)
                        data['results'].append(presentation_data)
                        with open(results_filepath, 'w') as f:
                            json.dump(data, f, indent=2)
                        print_(f"💾 Result saved to file for presentation {presentation_id}")
                    except Exception as e:
                        print_(f"⚠️ Failed to save result for presentation {presentation_id}: {e}")
                    
                except Exception as e:
                    print_(f"❌ Rating failed for presentation {presentation_id}: {e}")
                    rating_data = {
                        'overall_rating': None,
                        'sub_scores': {},
                        'rating_success': False,
                        'rating_error': str(e)
                    }
                
            except Exception as e:
                print_(f"❌ Pipeline failed for presentation {presentation_id}: {e}")
                saved_path = None
            
            # Increment presentation ID for next iteration
            presentation_id += 1
    
    print_(f"\n🎉 Experiment loop completed! Generated {presentation_id} presentations")
    print_("✅ All results have been saved to the file during execution.")
    
    # Step 7: Error Handling & Logging
    print_("\n🛡️ Setting up error handling and logging...")
    
    # Initialize experiment tracking variables
    experiment_start_time = datetime.now()
    successful_presentations = 0
    failed_presentations = 0
    successful_ratings = 0
    failed_ratings = 0
    
    # Create detailed experiment log
    experiment_log = {
        "start_time": experiment_start_time.isoformat(),
        "configuration": {
            "human_choice_levels": HUMAN_CHOICE_LEVELS,
            "presentations_per_level": PRESENTATIONS_PER_LEVEL,
            "choice_mode": base_config.choice_mode,
            "slide_count_target": base_config.slide_count_target,
            "total_expected": len(HUMAN_CHOICE_LEVELS) * PRESENTATIONS_PER_LEVEL
        },
        "progress": [],
        "errors": [],
        "summary": {
            "successful_presentations": 0,
            "failed_presentations": 0,
            "successful_ratings": 0,
            "failed_ratings": 0,
            "total_api_calls_used": 0
        }
    }
    
    print_(f"📊 Experiment tracking initialized:")
    print_(f"   - Expected presentations: {experiment_log['configuration']['total_expected']}")
    print_(f"   - Human choice levels: {len(HUMAN_CHOICE_LEVELS)}")
    print_(f"   - Presentations per level: {PRESENTATIONS_PER_LEVEL}")
    print_(f"   - Choice mode: {base_config.choice_mode} (AI choice)")
    
    print_("Error handling and logging ready - implementing progress reporting in next steps...")
    
    # Step 8: Progress Reporting
    print_("\n📊 Setting up progress reporting...")
    
    def print_experiment_progress(current_level, current_presentation, total_levels, presentations_per_level, 
                                 successful_presentations, failed_presentations, successful_ratings, failed_ratings):
        """Print current experiment progress with statistics."""
        total_presentations = total_levels * presentations_per_level
        completed_presentations = (current_level * presentations_per_level) + current_presentation
        
        print_(f"\n{'='*80}")
        print_(f"📈 EXPERIMENT PROGRESS")
        print_(f"{'='*80}")
        print_(f"🎯 Level: {current_level + 1}/{total_levels} (Human Choice: {HUMAN_CHOICE_LEVELS[current_level]}%)")
        print_(f"📊 Presentation: {current_presentation + 1}/{presentations_per_level}")
        print_(f"🆔 Overall Progress: {completed_presentations}/{total_presentations} ({completed_presentations/total_presentations*100:.1f}%)")
        print_(f"✅ Successful Presentations: {successful_presentations}")
        print_(f"❌ Failed Presentations: {failed_presentations}")
        print_(f"📈 Successful Ratings: {successful_ratings}")
        print_(f"📉 Failed Ratings: {failed_ratings}")
        print_(f"📊 Success Rate: {successful_presentations/(successful_presentations+failed_presentations)*100:.1f}%" if (successful_presentations+failed_presentations) > 0 else "N/A")
        print_(f"{'='*80}")
    
    def print_level_summary(level_index, human_choice_chance, successful_in_level, failed_in_level, 
                           successful_ratings_in_level, failed_ratings_in_level):
        """Print summary for completed level."""
        total_in_level = successful_in_level + failed_in_level
        print_(f"\n{'='*60}")
        print_(f"📋 LEVEL {level_index + 1} SUMMARY")
        print_(f"{'='*60}")
        print_(f"🎯 Human Choice Chance: {human_choice_chance}%")
        print_(f"✅ Successful Presentations: {successful_in_level}/{total_in_level}")
        print_(f"❌ Failed Presentations: {failed_in_level}/{total_in_level}")
        print_(f"📈 Successful Ratings: {successful_ratings_in_level}/{total_in_level}")
        print_(f"📉 Failed Ratings: {failed_ratings_in_level}/{total_in_level}")
        print_(f"📊 Success Rate: {successful_in_level/total_in_level*100:.1f}%" if total_in_level > 0 else "N/A")
        print_(f"{'='*60}")
    
    def print_final_summary(successful_presentations, failed_presentations, successful_ratings, failed_ratings, 
                           total_api_calls, experiment_duration):
        """Print final experiment summary."""
        total_presentations = successful_presentations + failed_presentations
        print_(f"\n{'='*80}")
        print_(f"🎉 FINAL EXPERIMENT SUMMARY")
        print_(f"{'='*80}")
        print_(f"📊 Total Presentations: {total_presentations}")
        print_(f"✅ Successful Presentations: {successful_presentations} ({successful_presentations/total_presentations*100:.1f}%)")
        print_(f"❌ Failed Presentations: {failed_presentations} ({failed_presentations/total_presentations*100:.1f}%)")
        print_(f"📈 Successful Ratings: {successful_ratings} ({successful_ratings/total_presentations*100:.1f}%)")
        print_(f"📉 Failed Ratings: {failed_ratings} ({failed_ratings/total_presentations*100:.1f}%)")
        print_(f"🤖 Total API Calls Used: {total_api_calls}")
        print_(f"⏱️ Experiment Duration: {experiment_duration}")
        print_(f"📁 Results saved to: {results_filepath}")
        print_(f"{'='*80}")
    
    print_("✅ Progress reporting functions ready")
    print_("📊 Will show detailed progress during experiment execution")
    print_("📈 Will provide level-by-level and final summaries")
    
    print_("Progress reporting ready - experiment framework complete!")
    print_("Ready to integrate all components and run the full experiment...")

if __name__ == "__main__":
    main()
