#!/usr/bin/env python3
"""
Run the presentation generation pipeline with basic default settings.
"""

from automation_core import AutomationCore, SystemConfig
from logging_funcs import print_

def main():
    config = SystemConfig(
        use_manual_api=False,
        slide_count_target=5,
        input_mode=2,  # use built-in manual_input_prompt from config
        
        # Human Choice Configuration Examples:
        human_choice_chance=100.0,  # 0% chance of choice scenarios (default)
        # human_choice_chance=10.0,  # 10% chance of choice scenarios
        # human_choice_chance=25.0,  # 25% chance of choice scenarios
        no_human_chances=False,  # Enable/disable the entire choice system
        choice_mode=5,  # 1=disabled, 2=first, 3=second, 4=random, 5=AI choice, 6=human choice
    )

    core = AutomationCore(config)

    if not core.initialize(require_confirmation=False):
        print_("❌ Initialization failed.")
        return False

    # Prepare context
    ctx = core.prepare_for_presentation_generation()

    # Pipeline execution
    step1 = core.execute_step_1(ctx)
    core.execute_step_2(ctx, step1)
    step3 = core.execute_step_3(ctx, step1)
    core.execute_step_4(ctx, step3)
    step4_5 = core.execute_step_4_5(ctx)
    step4_6 = core.execute_step_4_6(ctx, step4_5)  # New step for lecture notes
    core.execute_step_5(ctx)
    pres = core.execute_step_6(ctx, step4_5["slide_topics_list"])
    pres = core.execute_step_7(ctx, step4_5["slide_topics_list"], pres, step4_6["lecture_notes"])
    pres = core.execute_step_8(ctx, step4_5["slide_topics_list"], pres)
    pres = core.execute_step_9(ctx, step4_5["slide_topics_list"], step4_5["teaching_outline"], pres)
    pres = core.execute_step_10(pres)
    saved_path = core.execute_step_11(pres)

    print_(f"🎉 Presentation saved: {saved_path}")
    return True

if __name__ == "__main__":
    main()