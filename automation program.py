import os
from openai import OpenAI
import ai_database
import test_funcs
from datetime import datetime
import presentation_class
import slide_class
import source_class
from logging_funcs import print_, print_2
import logging_funcs
import ast
import time

# ========== CONFIGURABLE CONSTANT ==========
MAX_CALLS = 1000  # User should configure this value
TOPIC_PROMPT = "Describe the topic you'd like to explore." 

KNOWLEDGE_DB_NAME = "Knowledge Database"
KNOWLEDGE_DB_MAX_SIZE = 80

INPUT_MODE = 2
REWRITE_PROMPT = False
MANUAL_INPUT_PROMPT = "Module 2. LLM-Content\nTopic 2. LLM content generation and detection (2 weeks, 2 labs)\n2.1. LLM-content benchmarking datasets\n2.2. LLM-content detection\n2.3. Evading LLM detectors\n2.4. Watermarking LLM content"

SLIDE_COUNT_TARGET = 50
AI_ROLE_PROMPT = "You are assisting with the creation of a detailed teaching plan, then later slides to be used to teach a topic. Aim for the detail level of a teaching plan with high specificity. Do NOT assume you know anything for sure, as the first thing you will now do is a research phase."

logging_funcs.SUPPRESS_LOGS = False
logging_funcs.SUPPRESS_PRINTS = False

# ========== GLOBAL VARIABLES ==========
API_KEY = None
API_KEY_PATH = None
RESULTS_PATH = None
logging_funcs.LOGS_PATH = None
TEST_OUTPUT_PATH = None
PROMPT_FILE_PATH = None
calls_remaining = 0
client = None
knowledge_db = None
RUN_NAME = None

# ========== SETUP FUNCTIONS ==========

def setup_paths_and_key():
    global API_KEY, API_KEY_PATH, RESULTS_PATH, TEST_OUTPUT_PATH, RUN_NAME, PROMPT_FILE_PATH

    # Get current directory of this file
    current_dir = os.path.dirname(os.path.abspath(__file__))

    # Set paths
    API_KEY_PATH = os.path.join(current_dir, 'key.txt')
    RESULTS_PATH = os.path.join(current_dir, 'results')
    logging_funcs.LOGS_PATH = os.path.join(current_dir, 'logs')
    TEST_OUTPUT_PATH = os.path.join(current_dir, 'test_output')
    PROMPT_FILE_PATH = os.path.join(current_dir, 'input_prompt.txt')

    RUN_NAME = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    # Read API key
    try:
        with open(API_KEY_PATH, 'r') as f:
            API_KEY = f.read().strip()
    except FileNotFoundError:
        print_(f"Error: API key file not found at {API_KEY_PATH}")
        exit(1)

def initialize_call_limit(confirm=True):
    global calls_remaining
    if MAX_CALLS == 0:
        print_("Error: MAX_CALLS is set to 0. No API calls allowed.")
        exit(1)

    calls_remaining = MAX_CALLS
    print_(f"Allowed calls initialized to {calls_remaining}.")
    if confirm:
        input("Press Enter to continue...")

def initialize_openai():
    global client
    if not API_KEY:
        print_("Error: API key is not loaded.")
        exit(1)
    client = OpenAI(api_key=API_KEY)

# ========== API CALL HANDLER ==========

def call_ai_model(message: str) -> str:
    global client
    """Low-level call to the AI model. Returns raw string content."""
    if not client:
        print_("Error: OpenAI client is not initialized.")
        return None

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": message}],
            temperature=0.6
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print_(f"API call failed: {e}")
        return None

def safe_call_api(message: str):
    global calls_remaining

    if calls_remaining <= 0:
        user_input = input("No calls remaining. Reset? (Y to continue): ").strip().lower()
        if user_input == 'y':
            initialize_call_limit()
        else:
            print("Exiting program.")
            exit(0)

    calls_remaining -= 1
    tenth = MAX_CALLS / 10
    if int(tenth) == 0 or (MAX_CALLS > 0 and calls_remaining % int(tenth) == 0):
        print_(f"{calls_remaining}/{MAX_CALLS} Calls remaining.")

    return call_ai_model(message)

def setup_knowledge_database():
    global knowledge_db
    knowledge_db = ai_database.AIDatabase(
        name=KNOWLEDGE_DB_NAME,
        max_size=KNOWLEDGE_DB_MAX_SIZE
    )
    print_(f"Knowledge database '{KNOWLEDGE_DB_NAME}' initialized with max size {KNOWLEDGE_DB_MAX_SIZE}.")

def get_initial_prompt(input_mode: int, rewrite: bool) -> str:
    prompt = None

    if input_mode == 0:
        print_("Error: Invalid input mode selected.")
        exit(1)

    elif input_mode == 1:
        prompt = input("Enter your prompt: ").strip()

    elif input_mode == 2:
        prompt = MANUAL_INPUT_PROMPT

    elif input_mode == 3:
        if not os.path.isfile(PROMPT_FILE_PATH):
            print_(f"Error: Prompt file not found at {PROMPT_FILE_PATH}")
            exit(1)
        with open(PROMPT_FILE_PATH, 'r', encoding='utf-8') as f:
            prompt = f.read().strip()
            if not prompt:
                print_("Error: Prompt file is empty.")
                exit(1)
    else:
        print_(f"Error: Unknown input mode '{input_mode}'")
        exit(1)

    if rewrite:
        print_("Rewriting prompt using AI...")
        rewritten = safe_call_api(f"Rewrite this prompt to be more usable, clear, and professional:\n\n{prompt}")
        if rewritten:
            prompt = rewritten.strip()
            print_("Rewritten Prompt:\n", prompt)
        else:
            print_("Warning: Failed to rewrite prompt. Using original.")

    return prompt

def initialize_logging():
    global RUN_NAME

    logging_funcs.LOGS_PATH = os.path.join(logging_funcs.LOGS_PATH, f"log_{RUN_NAME}.txt")

    try:
        with open(logging_funcs.LOGS_PATH, 'w', encoding='utf-8') as log_file:
            log_file.write("=== LOG FILE START ===\n")
            if logging_funcs.SUPPRESS_LOGS:
                log_file.write("(Note: Console output suppressed)\n")
            log_file.write("\n")
    except Exception as e:
        print(f"Error initializing log file: {e}")

# generation function(s) =========================

def generate_presentation_setup():
    #run setup functions
    setup_paths_and_key()
    initialize_logging()
    initialize_openai()
    initialize_call_limit()
    setup_knowledge_database()


def generate_presentation(run_setup=True, input_mode=None, rewrite_prompt=None):
    #ensure needed variables are configured
    needed_vars = ["input_mode", "rewrite_prompt"]
    for var_ in needed_vars:
        if eval(var_) == None:
            print_("Error: " + var_ + " cannot be None.")
            return None
        
    #do setup
    if run_setup:
        generate_presentation_setup()

    #prompt formation stuff now
    prompt = get_initial_prompt(input_mode, rewrite_prompt)
    print_("\nFinal Prompt:")
    print_(prompt)

    #Part 1 Goes here ===========
    print_("Step 1 begun.")
    
    built_in_instructions = "You will generate a preliminary research topic list based upon what you think you may know on the topic. Based on the results you will do more research later. Answer ONLY with a **COMMA-SEPERATED** list of exactly # topics and nothing else. (**COMMA-SEPERATED**!!)"
    initial_topic_count = max(2, int(SLIDE_COUNT_TARGET / 12))

    built_in_instructions = built_in_instructions.replace("#", str(initial_topic_count))

    full_step_1_prompt = "Topic Prompt: ({ " + prompt + " }) AI Role: ({ " + AI_ROLE_PROMPT + "}) Specific Instructions: ({" + built_in_instructions + "})"

    raw_step_1_response = safe_call_api(full_step_1_prompt)

    print_("Raw AI topic response: " + str(raw_step_1_response))

    if raw_step_1_response == None:
        print_("Error: No AI response given.")
        return -1
    
    else:
        #split out the response.
        split_topics = raw_step_1_response.split(",")
        for i in range(len(split_topics)):
            split_topics[i] = split_topics[i].strip(" \t\n.,[]{}()0123456789")

        if len(split_topics) < initial_topic_count:
            print_("Error: " + str(len(split_topics)) + " topics provided. " + str(initial_topic_count) + " expected.")
            print_("Got: " + str(split_topics))
            return -1
        
        if len(split_topics) > initial_topic_count:
            split_topics = split_topics[:initial_topic_count]
        
        print_("Selected topics: " + str(split_topics))

    print_("Step 1 Complete.")

    #Part 2 Goes here ==========
    print_("Step 2 begun.")

    #crunch some numbers to determine database entries per topic
    second_research_round_topic_count = max(3, initial_topic_count * 3)
    database_entries_per_topic = int(KNOWLEDGE_DB_MAX_SIZE / (initial_topic_count + second_research_round_topic_count))

    if database_entries_per_topic < 1:
        print_("Error: Not enough database size to research these topics at all.")
        return -1

    print_(str(database_entries_per_topic) + " database entries per topic.")

    #the research loop
    RESEARCH_PROMPT = "You are to perform a web-search to research the topic given on the general category from the inital prompt. Avoid redoing research from titles previously used. These are: #1. Be specific and assume the user of this database has no background knowledge. You are focusing on the topic **#2** and this is entry #3 for this topic."
    STRUCTURE_PROMPT_STEP_2 = "Respond in a Python Dictionary style format. This dictionary needs to have feilds title (str), keywords (list[str]), text (str), and link (str). Fill these out as you wish with researched information. Respond with nothing else. Be on-topic!"
    existing_entry_titles = []

    for topic in split_topics:
        print_(f"Researching topic: {topic}")
        for i in range(database_entries_per_topic):
            #small safety delay
            time.sleep(0.1)

            #build the prompt for research
            specific_research_prompt = "Initial Prompt: ({ " + prompt + " }) AI Role: ({ " + RESEARCH_PROMPT + " }) Specific Instructions: ({ " + STRUCTURE_PROMPT_STEP_2 + " })"

            if existing_entry_titles == []:
                specific_research_prompt = specific_research_prompt.replace("#1", "(None)")

            else:
                specific_research_prompt = specific_research_prompt.replace("#1", str(existing_entry_titles))

            specific_research_prompt = specific_research_prompt.replace("#3", str(i + 1))
            specific_research_prompt = specific_research_prompt.replace("#2", topic.upper())

            #make the api call now that the prompt is built
            print_("Prompt:\n" + specific_research_prompt + "\nTo sent to the AI.")

            raw_step_2_response = safe_call_api(specific_research_prompt)

            print_("Raw AI response to this: " + str(raw_step_2_response))

            if raw_step_2_response == None:
                print_("Error: During research, AI failed to respond.")
                continue

            else:
                #try and break out response into needed parts.
                try:
                    step_2_dictionary = ast.literal_eval(raw_step_2_response)
                
                except:
                    print_("Error: Incorrect format during step 2 research.")
                    continue

                if type(step_2_dictionary) != dict:
                    print_("Error: Response not a dictionary.")
                    continue

                needed_keys = ["title", "keywords", "text", "link"]
                needed_types = [str, list, str, str]
                no_missing_keys = True
                for j in range(len(needed_keys)):
                    needed_key = needed_keys[j]
                    needed_type = needed_types[j]
                    if not (needed_key in list(step_2_dictionary.keys())):
                        print_("Error: " + str(needed_key) + " not given in step 2 research dictionary.")
                        no_missing_keys = False
                        break

                    if type(step_2_dictionary[needed_key]) != needed_type:
                        print_("Error: " + str(needed_key) + " does not contain data of type " + str(needed_type) + ".")
                        no_missing_keys = False
                        break
                
                if not no_missing_keys:
                    continue

                if knowledge_db.add_entry(step_2_dictionary["title"], step_2_dictionary["keywords"], step_2_dictionary["text"], step_2_dictionary["link"]):
                    existing_entry_titles.append(step_2_dictionary["title"])
                    print_("Added Entry to database. Displaying.")
                    print_(str(knowledge_db.entries[-1]))

                else:
                    print_("Error: Knowledge Database out of space.")
                    continue

    print_("Step 2 Complete.")

    #Part 3 Goes here ==========
    print_("Step 3 begun.")

    #assemble the megaprompt.
    STEP_3_STRUCTURE_PROMPT = "You are continuing a research topic list based upon initial reserach. The inital topics were #1. The research these yeilded is: ({#2}). You need to give #3 more topics. Make them unique and full correspond to the intial prompt based upon your role, and be selected with the info you got from the research text. Ensure they do not rely on the context of previous topic names to be sensical. Respond in a comma-seperated list of topics with nothing else. Again, **COMMA-SEPERATED**!!"
    final_prompt_step_3 = "Initial Prompt: ({ " + prompt + " }) Role Prompt: ({ " + AI_ROLE_PROMPT + " }) Specific Instructions: ({ " + STEP_3_STRUCTURE_PROMPT + " })"

    research_text = knowledge_db.get_all_text()
    if len(research_text) > 1000:
        research_text = research_text[:1000] + " (Truncated for brevity.)"

    final_prompt_step_3 = final_prompt_step_3.replace("#1", str(split_topics))
    final_prompt_step_3 = final_prompt_step_3.replace("#3", str(second_research_round_topic_count))
    final_prompt_step_3 = final_prompt_step_3.replace("#2", research_text)

    print_("Following Prompt sent to AI:\n" + final_prompt_step_3 + "\n.")
    raw_step_3_response = safe_call_api(final_prompt_step_3)

    #check for valid response.
    print_("Raw AI topic response: " + str(raw_step_3_response))

    if raw_step_3_response == None:
        print_("Error: No AI response given.")
        return -1
    
    else:
        #split out the response.
        split_topics_2 = raw_step_3_response.split(",")
        for i in range(len(split_topics_2)):
            split_topics_2[i] = split_topics_2[i].strip(" \t\n.,[]{}()0123456789")

        if len(split_topics_2) < second_research_round_topic_count:
            print_("Error: " + str(len(split_topics_2)) + " topics provided. " + str(second_research_round_topic_count) + " expected.")
            print_("Got: " + str(split_topics_2))
            return -1
        
        if len(split_topics_2) > second_research_round_topic_count:
            split_topics_2 = split_topics_2[:second_research_round_topic_count]
        
        print_("Selected topics: " + str(split_topics_2))

    print_("Step 3 Complete.")

    #Part 4 Goes here ==========
    print_("Step 4 begun.")

    print_(str(database_entries_per_topic) + " database entries per topic.")

    #prepare the prompt for research
    RESEARCH_PROMPT_2 = "You are to perform a web-search to research the topic given on the general category from the inital prompt. Avoid redoing research from titles previously used. These are: #1. Be specific and assume the user of this database has no background knowledge. You are focusing on the topic **#2** and this is entry #3 for this topic."
    STRUCTURE_PROMPT_STEP_4 = "Respond in a Python Dictionary style format. This dictionary needs to have feilds title (str), keywords (list[str]), text (str), and link (str). Fill these out as you wish with researched information. Respond with nothing else. Be on-topic!"

    for topic in split_topics_2:
        print_(f"Researching topic: {topic}")
        for i in range(database_entries_per_topic):
            #small safety delay
            time.sleep(0.1)

            #build the prompt for research
            specific_research_prompt = "Initial Prompt: ({ " + prompt + " }) AI Role: ({ " + RESEARCH_PROMPT_2 + " }) Specific Instructions: ({ " + STRUCTURE_PROMPT_STEP_4 + " })"

            if existing_entry_titles == []:
                specific_research_prompt = specific_research_prompt.replace("#1", "(None)")

            else:
                specific_research_prompt = specific_research_prompt.replace("#1", str(existing_entry_titles))

            specific_research_prompt = specific_research_prompt.replace("#3", str(i + 1))
            specific_research_prompt = specific_research_prompt.replace("#2", topic.upper())

            #make the api call now that the prompt is built
            print_("Prompt:\n" + specific_research_prompt + "\nTo sent to the AI.")

            raw_step_4_response = safe_call_api(specific_research_prompt)

            print_("Raw AI response to this: " + str(raw_step_4_response))

            if raw_step_4_response == None:
                print_("Error: During research, AI failed to respond.")
                continue

            else:
                #try and break out response into needed parts.
                try:
                    step_4_dictionary = ast.literal_eval(raw_step_4_response)
                
                except:
                    print_("Error: Incorrect format during step 4 research.")
                    continue

                if type(step_4_dictionary) != dict:
                    print_("Error: Response not a dictionary.")
                    continue

                needed_keys = ["title", "keywords", "text", "link"]
                needed_types = [str, list, str, str]
                no_missing_keys = True
                for j in range(len(needed_keys)):
                    needed_key = needed_keys[j]
                    needed_type = needed_types[j]
                    if not (needed_key in list(step_4_dictionary.keys())):
                        print_("Error: " + str(needed_key) + " not given in step 4 research dictionary.")
                        no_missing_keys = False
                        break

                    if type(step_4_dictionary[needed_key]) != needed_type:
                        print_("Error: " + str(needed_key) + " does not contain data of type " + str(needed_type) + ".")
                        no_missing_keys = False
                        break
                
                if not no_missing_keys:
                    continue

                if knowledge_db.add_entry(step_4_dictionary["title"], step_4_dictionary["keywords"], step_4_dictionary["text"], step_4_dictionary["link"]):
                    existing_entry_titles.append(step_4_dictionary["title"])
                    print_("Added Entry to database. Displaying.")
                    print_(str(knowledge_db.entries[-1]))

                else:
                    print_("Error: Knowledge Database out of space.")
                    continue

    print_("Step 4 Complete.")

    #Part 5 Goes here ==========
    print_("Step 5 begun.")

    #first, determine the number of sections that we want with an API call.
    STRUCTURE_PROMPT_STEP_5_PART_A = "Given the previous information, you will decide how many topics will be in this presentation. Also take into account: #1. This is a sample of the databse gotten via research. Respond only with a single number and nothing else. Ensure the number is reasonable. Soft max of 16."
    full_step_5_prompt_part_A = "Initial Prompt: ({ " + prompt + " }) Role Prompt: ({ " + AI_ROLE_PROMPT + " }) Specific Instructions: ({ " + STRUCTURE_PROMPT_STEP_5_PART_A + " })"

    summary_sample_database_text = knowledge_db.get_sample_text(max_entries=None, max_chars_per_entry=100)

    full_step_5_prompt_part_A = full_step_5_prompt_part_A.replace("#1", summary_sample_database_text)

    print_("Prompt to AI:\n" + full_step_5_prompt_part_A + "\n.")
    raw_step_1_part_A_response = safe_call_api(full_step_5_prompt_part_A)
    print_("Raw response:\n" + str(raw_step_1_part_A_response) + "\n.")

    if raw_step_1_part_A_response == None:
        print_("No response from AI.")
        return -1

    #validate that this is just a single numeral.
    if type(ast.literal_eval(raw_step_1_part_A_response.strip())) != int:
        print_("Error: Non-number received for topic amount.")
        return -1

    #save this important number. Also display
    Total_topics_count = ast.literal_eval(raw_step_1_part_A_response.strip())

    if Total_topics_count < 1:
        print_("Error: Cannot have 0 topics or fewer. Had " + str(Total_topics_count) + ".")
        return -1
    
    max_topics = 100
    if Total_topics_count > max_topics:
        print_("Error: Cannot have more than " + str(max_topics) + " topics. Had " + str(Total_topics_count) + ".")
        return -1

    print_("Topic count decided: " + str(Total_topics_count))

    #next, get information on each of them with another API call and save that information.
    STRUCTURE_PROMPT_STEP_5_PART_B = "Given the previous information and the following database text sample, you are going to make a topic outline. Database sample: ({#1}). You are to come up with #2 topics. Respond in the form of a python list of dictionaries, where each dictionary is a topic, and has three fields. They are title(str), keywords(list[str]), and text(str). Text briefly explains the section. Fill them out, obviously. Respond with nothing else. Follow the format exactly."
    full_step_5_prompt_part_B = "Initial Prompt: ({ " + prompt + " }) Role Prompt: ({ " + AI_ROLE_PROMPT + " }) Specific Instructions: ({ " + STRUCTURE_PROMPT_STEP_5_PART_B + " })"

    full_step_5_prompt_part_B = full_step_5_prompt_part_B.replace("#2", str(Total_topics_count))
    full_step_5_prompt_part_B = full_step_5_prompt_part_B.replace("#1", summary_sample_database_text)

    print_("Prompt to AI:\n" + full_step_5_prompt_part_B + "\n.")
    raw_step_1_part_B_response = safe_call_api(full_step_5_prompt_part_B)
    print_("Raw response:\n" + str(raw_step_1_part_B_response) + "\n.")

    if raw_step_1_part_B_response == None:
        print_("No response from AI.")
        return -1

    #validate correct list of dicts structure.
    raw_step_1_part_B_response = raw_step_1_part_B_response[raw_step_1_part_B_response.index("["):raw_step_1_part_B_response.rindex("]") + 1]
    topics_list = ast.literal_eval(raw_step_1_part_B_response.strip())

    if type(topics_list) != list:
        print_("Error: Non-list received in topics outline.")
        return -1
    
    if len(topics_list) < Total_topics_count:
        print_("Error: Received " + str(len(topics_list)) + " quantities for slide amounts, expected " + str(Total_topics_count) + ".")
        return -1
    
    if len(topics_list) > Total_topics_count:
        topics_list = topics_list[:Total_topics_count]
    
    for i in range(Total_topics_count):
        if type(topics_list[i]) != dict:
            print_("Error: Topics list contains non-dictionary.")
            return -1
        
    needed_keys = ["title", "keywords", "text"]
    needed_types = [str, list, str]
    for i in range(Total_topics_count):
        for j in range(len(needed_keys)):
            if not (needed_keys[j] in list(topics_list[i].keys())):
                print_("Error: Topics list contains dictionary missing needed item: " + str(needed_keys[j]))
                return -1
            
            if type(topics_list[i][needed_keys[j]]) != needed_types[j]:
                print_("Error: Component of item of topics list of type " + str(type(topics_list[i][needed_keys[j]])) + " instead of " + str(needed_types[j]) + ".")
                return -1
    
    #save them for use in later steps, display data also
    Presentation_topics_list = topics_list

    print_("Topics list:\n" + str(Presentation_topics_list) + "\n.")

    #finally, given the total amount of slides and other background info, do a call to get the number of slides to use per topic.
    #failsafe: Divide unused slides evenly between the topics, so not 100% accuracy is required.
    #Similarly, remove slides evenly if too many assigned. Cannot remove last slide from a topic, though.
    STRUCTURE_PROMPT_STEP_5_PART_C = "Given the previous text and the following database text sample, you will do a task. Sample: ({#1}). You came up with a list of #2 topics for a presentation. They are: #3. This will be for a presentation with #4 total slides in it. You are to come up with a number of slides per topic. Respond as a python list of integers. These numbers match to the topic of matching index in the topics list. Respond with nothing else at all. Follow output format exactly."
    full_step_5_prompt_part_C = "Initial Prompt: ({ " + prompt + " }) Role Prompt: ({ " + AI_ROLE_PROMPT + " }) Specific Instructions: ({ " + STRUCTURE_PROMPT_STEP_5_PART_C + " })"

    full_step_5_prompt_part_C = full_step_5_prompt_part_C.replace("#2", str(Total_topics_count))
    full_step_5_prompt_part_C = full_step_5_prompt_part_C.replace("#3", str(topics_list))
    full_step_5_prompt_part_C = full_step_5_prompt_part_C.replace("#4", str(SLIDE_COUNT_TARGET))
    full_step_5_prompt_part_C = full_step_5_prompt_part_C.replace("#1", summary_sample_database_text)

    print_("Prompt to AI:\n" + full_step_5_prompt_part_C + "\n.")
    raw_step_1_part_C_response = safe_call_api(full_step_5_prompt_part_C)
    print_("Raw response:\n" + str(raw_step_1_part_C_response) + "\n.")

    if raw_step_1_part_C_response == None:
        print_("No response from AI.")
        return -1

    #validate list of numbers structure.
    raw_step_1_part_C_response = raw_step_1_part_C_response[raw_step_1_part_C_response.index("["):raw_step_1_part_C_response.rindex("]") + 1]
    quantity_list = ast.literal_eval(raw_step_1_part_C_response.strip())

    if type(quantity_list) != list:
        print_("Error: Non-list received for slides per topic.")
        return -1
    
    if len(quantity_list) != Total_topics_count:
        print_("Error: Received " + str(len(quantity_list)) + " quantities for slide amounts, expected " + str(Total_topics_count) + ".")
        return -1

    quantity_list = [max(1, q) for q in quantity_list]

    #split out additional slides as needed.
    extra_slides = SLIDE_COUNT_TARGET - sum(quantity_list)

    while extra_slides > 0:
        for i in range(Total_topics_count):
            extra_slides -= 1
            quantity_list[i] += 1
            if extra_slides == 0:
                break

    #remove slides as needed.
    while extra_slides < 0:
        if sum(quantity_list) == Total_topics_count:
            break

        for i in range(Total_topics_count):
            extra_slides += 1
            quantity_list[i] -= 1
            if quantity_list[i] < 1:
                extra_slides += quantity_list[i] - 1
                quantity_list[i] = 1
            if extra_slides == 0:
                break

    #save the tweaked numbers into the dictionary, display data also
    for i in range(Total_topics_count):
        Presentation_topics_list[i]["slides_amount_goal"] = quantity_list[i]
        Presentation_topics_list[i]["current_slides_amount"] = 0

    print_("New appended slide data:\n" + str(Presentation_topics_list) + "\n.")

    print_("Step 5 Complete.")

    #Part 6 Goes here ==========
    print_("Step 6 begun.")

    # Create the Presentation structure
    presentation = presentation_class.PresentationBuilder()

    # Go through each topic to assign and create slides
    for topic_info in Presentation_topics_list:
        topic_title = topic_info["title"]
        slide_count = topic_info["slides_amount_goal"]

        for i in range(slide_count):
            # Create a new slide with placeholder title (can be adjusted later)
            slide_title = f"{topic_title} - Slide {i + 1}"
            new_slide = slide_class.SlideData(title=slide_title, content="", sources=[])

            # Add it to the actual presentation structure
            presentation.slides.append(new_slide)

        # Update count of current slides assigned
        topic_info["current_slides_amount"] = slide_count

    print_("Slide layout created and presentation initialized.")

    print_("Step 6 Complete.")

    #Part 7 Goes here ==========
    print_("Step 7 begun.")

    STRUCTURE_PROMPT_STEP_7 = "You are giving general topics to each slide in the presentation. You are currently on slide #1. It is for the topic #2. Previous themes within this section of the presentation are #3. Information from the research database that may be relevant is: ({#4}). You are to give a general theme for this slide for later iteration. Respond with the topic and nothing else."

    current_topic_previous_themes = []
    current_theme = None
    section_research_results = None

    for i in range(len(presentation.slides)):
        #small safety delay
        time.sleep(0.1)

        temp_i = i + 1
        j = 0
        while temp_i > Presentation_topics_list[j]["slides_amount_goal"]:
            temp_i -= Presentation_topics_list[j]["slides_amount_goal"]
            j += 1

        if current_theme != Presentation_topics_list[j]["title"]:
            current_theme = Presentation_topics_list[j]["title"]
            current_topic_previous_themes = []
            
            search_term = ""
            for keyword in Presentation_topics_list[j]["keywords"]:
                search_term += " " + str(keyword)

            section_research_results_raw = knowledge_db.search(search_term)

            section_research_results = ""

            for section_research_result_raw in section_research_results_raw:
                section_research_results += str(section_research_result_raw) + "\n\n"

        specific_step_7_prompt = "Initial Prompt: ({ " + prompt + " }) Role Prompt: ({ " + AI_ROLE_PROMPT + " }) Specific Instructions: ({ " + STRUCTURE_PROMPT_STEP_7 + " })"

        specific_step_7_prompt = specific_step_7_prompt.replace("#1", str(i + 1))
        specific_step_7_prompt = specific_step_7_prompt.replace("#2", current_theme)
        specific_step_7_prompt = specific_step_7_prompt.replace("#3", str(current_topic_previous_themes))
        specific_step_7_prompt = specific_step_7_prompt.replace("#4", section_research_results)

        print_("The following is about to be sent to the AI: \n" + str(specific_step_7_prompt) + "\n.")

        raw_step_7_response = safe_call_api(specific_step_7_prompt)

        print_("Raw step 7 response: " + str(raw_step_7_response))

        if raw_step_7_response == None:
            print_(f"Error: AI gave no response for slide {i + 1}. Skipping.")
            continue

        presentation.slides[i].content = raw_step_7_response.strip()
        
        current_topic_previous_themes.append(raw_step_7_response.strip())

    print_("Full current content of presentation slides: " + presentation.summarize_contents())

    print_("Step 7 Complete.")

    #Part 8 Goes here ==========
    print_("Step 8 begun.")

    STRUCTURE_PROMPT_STEP_8 = "You have been given previous information. You are on slide #1. It is within the #2 section. Previous slide titles in this presentation are: ({#3}). Database information for this section is: ({#4}). It was previously given the topic of #5. You are to make a title for this slide based upon all of that. Respond with the slide title and nothing else."
    all_slide_titles = []
    current_theme = None
    section_research_results = None

    for i in range(len(presentation.slides)):
        #small safety delay
        time.sleep(0.1)

        temp_i = i + 1
        j = 0
        while temp_i > Presentation_topics_list[j]["slides_amount_goal"]:
            temp_i -= Presentation_topics_list[j]["slides_amount_goal"]
            j += 1

        if current_theme != Presentation_topics_list[j]["title"]:
            current_theme = Presentation_topics_list[j]["title"]
            
            search_term = ""
            for keyword in Presentation_topics_list[j]["keywords"]:
                search_term += " " + str(keyword)

            section_research_results_raw = knowledge_db.search(search_term)

            section_research_results = ""

            for section_research_result_raw in section_research_results_raw:
                section_research_results += str(section_research_result_raw) + "\n\n"

        specific_step_8_prompt = "Initial Prompt: ({ " + prompt + " }) Role Prompt: ({ " + AI_ROLE_PROMPT + " }) Specific Instructions: ({ " + STRUCTURE_PROMPT_STEP_8 + " })"

        specific_step_8_prompt = specific_step_8_prompt.replace("#1", str(i + 1))
        specific_step_8_prompt = specific_step_8_prompt.replace("#2", current_theme)
        if all_slide_titles == []:
            specific_step_8_prompt = specific_step_8_prompt.replace("#3", "(None.)")
        else:
            specific_step_8_prompt = specific_step_8_prompt.replace("#3", str(all_slide_titles))
        specific_step_8_prompt = specific_step_8_prompt.replace("#5", str(presentation.slides[i].content))
        specific_step_8_prompt = specific_step_8_prompt.replace("#4", section_research_results)

        print_("About to be sent to the AI: \n" + specific_step_8_prompt + "\n.")

        raw_step_8_response = safe_call_api(specific_step_8_prompt)

        print_("Raw step 8 response: " + str(raw_step_8_response))

        if raw_step_8_response == None:
            print_(f"Error: AI gave no response for slide {i + 1}. Skipping.")
            continue

        presentation.slides[i].title = raw_step_8_response.strip()
        
        all_slide_titles.append(raw_step_8_response.strip())

    print_("Full current content of presentation slides: " + presentation.summarize_contents())

    #now get the overall presentation title
    STRUCTURE_PROMPT_STEP_8_2 = "You are making a presention with the previous ideas as context. These are all of the slide titles for the presentation: ({#1}). Based upon this, generate a title for the presentation overall. Respond with that title and nothing else."
    specific_step_8_prompt = "Initial Prompt: ({ " + prompt + " }) Role Prompt: ({ " + AI_ROLE_PROMPT + " }) Specific Instructions: ({ " + STRUCTURE_PROMPT_STEP_8_2 + " })"

    print_("About to be sent to the AI: \n" + specific_step_8_prompt + "\n.")

    raw_step_8_response = safe_call_api(specific_step_8_prompt)

    print_("Raw step 8 response: " + str(raw_step_8_response))

    if raw_step_8_response == None:
        print_("Error: Failure to generate presention title.")
        return -1
    
    presentation.title = str(raw_step_8_response.strip(" \"\'"))
    print_("Presentation title: " + str(raw_step_8_response.strip(" \"\'")))

    print_("Step 8 Complete.")

    #Part 9 Goes here ==========
    print_("Step 9 begun.")

    #Part 9A
    #determine sources per slide
    USES_PER_SOURCE_AVERAGE = 1
    UNUSED_SOURCES_PERCENT = 0.05
    SOURCES_USED_PER_SLIDE = max(1, int(len(knowledge_db.entries) / SLIDE_COUNT_TARGET * USES_PER_SOURCE_AVERAGE * (1 - UNUSED_SOURCES_PERCENT)))

    print_("Sources per slide: " + str(SOURCES_USED_PER_SLIDE))

    STRUCTURE_PROMPT_STEP_9_PART_A = "Given the previous information and some following information, you will give a list of keywords to search the database with to source the slide. You are on slide #1. The title of this slide is #2. The theme/topic of this slide is #3. It is for the section #4. The full list of keywords generally associated with this category are: #5. The full list of keywords is #6. Again, respond with keywords to search the database with, and nothing else. Ensure you respond in the form of a list of keywords that are the ones referenced. Make the keywords very generic/generously allocated to have many possible sources. Remember to respond in the form of a python list of strings to do this."

    full_keywords_list = knowledge_db.get_all_keywords()

    Sources_associations = {}

    for i in range(len(presentation.slides)):
        #small safety delay
        time.sleep(0.1)

        temp_i = i + 1
        j = 0
        while temp_i > Presentation_topics_list[j]["slides_amount_goal"]:
            temp_i -= Presentation_topics_list[j]["slides_amount_goal"]
            j += 1

        specific_step_9_prompt = "Initial Prompt: ({ " + prompt + " }) Role Prompt: ({ " + AI_ROLE_PROMPT + " }) Specific Instructions: ({ " + STRUCTURE_PROMPT_STEP_9_PART_A + " })"

        specific_step_9_prompt = specific_step_9_prompt.replace("#1", str(i +1))
        specific_step_9_prompt = specific_step_9_prompt.replace("#2", str(presentation.slides[i].title))
        specific_step_9_prompt = specific_step_9_prompt.replace("#3", str(presentation.slides[i].content))
        specific_step_9_prompt = specific_step_9_prompt.replace("#4", str(Presentation_topics_list[j]["title"]))
        specific_step_9_prompt = specific_step_9_prompt.replace("#5", str(Presentation_topics_list[j]["keywords"]))
        specific_step_9_prompt = specific_step_9_prompt.replace("#6", str(full_keywords_list))

        print_("About to be sent to the AI: \n" + str(specific_step_9_prompt) + "\n.")

        raw_step_9_response = safe_call_api(specific_step_9_prompt)

        print_("Raw step 9 response: " + str(raw_step_9_response))

        if raw_step_9_response == None:
            print_("Error: Got no response on part 9A.")
            continue

        filtered_part_9_response = ast.literal_eval(raw_step_9_response)

        if type(filtered_part_9_response) != list:
            print_("Error: Got non-list response in part 9.")
            continue

        filtered_part_9_response_pt_2 = ""
        for temp_j in filtered_part_9_response:
            filtered_part_9_response_pt_2 += " " + str(temp_j)

        filtered_part_9_response_pt_2 = filtered_part_9_response_pt_2.strip()

        raw_step_9_search_results = knowledge_db.search(filtered_part_9_response_pt_2)

        raw_step_9_search_results = raw_step_9_search_results[:SOURCES_USED_PER_SLIDE]

        for k in range(len(raw_step_9_search_results)):
            #first, increment uses
            raw_step_9_search_results[k].add_use()

            #then, check if the entry is already associated with a source. If not, generate one.
            if str(raw_step_9_search_results[k].id) in list(Sources_associations.keys()):
                used_source_obj = Sources_associations[str(raw_step_9_search_results[k].id)]

            else:
                used_source_obj = source_class.Source(raw_step_9_search_results[k].title, raw_step_9_search_results[k].link, raw_step_9_search_results[k])
                Sources_associations[str(raw_step_9_search_results[k].id)] = used_source_obj

            #then take the source and add it to the slide.
            presentation.slides[i].sources.append(used_source_obj)

    print_("Done associating sources with slides.")

    #Part 9B
    STRUCTURE_PROMPT_STEP_9_PART_B = "Based on the previous information and some future information, you are filling out the contents of a powerpoint slide. It is slide number #1. The topic of the slide is #2. The title of the slide is #3. The section theme it is within is #4. It has information associated with it that was researched, to be used: ({#5}). The following text was used in the previous slide: ({#6}). Use that to enhance flow and ensure non-repetition. Respond only with the things that should occupy the body of the slide, and nothing else. Respond in a way fitting of this format. Ensure a proper quantity of text is output, as well. Focus on specific details that would belong in a precise teaching plan. Use source info. Avoid generalities. For the information from the sources, almost just copy it into the slides with themeing/formatting."

    for i in range(len(presentation.slides)):
        #small safety delay
        time.sleep(0.1)

        #now, add proper content to each of the slides using an api call each

        specific_step_9_prompt = "Initial Prompt: ({ " + prompt + " }) Role Prompt: ({ " + AI_ROLE_PROMPT + " }) Specific Instructions: ({ " + STRUCTURE_PROMPT_STEP_9_PART_B + " })"

        specific_step_9_prompt = specific_step_9_prompt.replace("#1", str(i + 1))
        specific_step_9_prompt = specific_step_9_prompt.replace("#2", presentation.slides[i].content)
        specific_step_9_prompt = specific_step_9_prompt.replace("#3", presentation.slides[i].title)
        if i == 0:
            specific_step_9_prompt = specific_step_9_prompt.replace("#6", "(None.)")

        else:
            specific_step_9_prompt = specific_step_9_prompt.replace("#6", str(presentation.slides[i - 1].content))

        specific_step_9_prompt = specific_step_9_prompt.replace("#4", Presentation_topics_list[j]["title"])

        #get the data from the database to give to the AI
        full_researched_text = ""

        for source_id in presentation.slides[i].sources:
            full_researched_text += " " + source_id.linked_entry.text

        full_researched_text = full_researched_text.strip()

        if full_researched_text != "":
            specific_step_9_prompt = specific_step_9_prompt.replace("#5", full_researched_text)
        else:
            specific_step_9_prompt = specific_step_9_prompt.replace("#5", "(None.)")

        print_("Prompt sent to the AI: \n" + specific_step_9_prompt + "\n.")

        raw_step_9_response = safe_call_api(specific_step_9_prompt)

        print_("Raw response for step 9: " + str(raw_step_9_response))

        if raw_step_9_response == None:
            print_("Error: Got empty response while filling out slide contents.")
            return -1
        
        #add content to the slide
        presentation.slides[i].content = raw_step_9_response.strip()

    print_("Presentation Currently: " + str(presentation.summarize_contents()))

    print_("Step 9 Complete.")

    #Part 10 Goes here ==========
    print_("Step 10 begun.")

    # Add title slide at the beginning
    presentation.add_title_slide()

    print_("Title slide added.")

    # Add source slides at the end
    presentation.add_sources_slides()
    print_("Sources slides added.")

    print_("Step 10 Complete.")

    #Part 11 Goes here ==========
    print_("Step 11 begun.")

    print_("Saving to file: " + str(RESULTS_PATH))

    save_title = presentation.title

    disallowed_chars = ['<', '>', ':', '"', '/', '\\', '|', '?', '*']
    for disallowed_char in disallowed_chars:
        save_title = save_title.replace(disallowed_char, "")

    save_title = save_title.replace(" ", "_")

    save_title += "_" + RUN_NAME

    print_("Save title used: " + save_title)

    presentation.save_to_file(RESULTS_PATH, save_title)

    print_("Saved to file.")

    print_("Step 11 Complete.")

    print_("Presentation generation complete.")

# ========== MAIN FUNCTION ==========

def main():
    #setup needs run first
    generate_presentation_setup()

    #run tests at this location as needed. Control with the int.
    run_tests = 0
    if run_tests:
        test_funcs.test_slide_utilities(TEST_OUTPUT_PATH, RUN_NAME)

    #A stopper to use if you only want to run tests.
    if run_tests:
        print_("Ended program early due to test flag being set.")
        return

    #tests over
    #now generate the presentation. No need to rerun the setup
    generate_presentation(run_setup=False, rewrite_prompt=REWRITE_PROMPT, input_mode=INPUT_MODE)

if __name__ == "__main__":
    main()