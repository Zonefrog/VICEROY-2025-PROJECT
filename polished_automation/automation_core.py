"""
VICEROY-2025-PROJECT: Polished Automation Core
Clean implementation of the setup and initialization phase for AI-powered presentation generation.
"""

import os
import sys
import ast
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any
from dataclasses import dataclass
from openai import OpenAI

# Import project modules
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import ai_database
from logging_funcs import print_, print_2


@dataclass
class SystemConfig:
    """Centralized configuration for the automation system."""
    
    # API Configuration
    max_api_calls: int = 1000
    openai_model: str = "gpt-3.5-turbo"
    temperature: float = 0.6
    use_manual_api: bool = False  # If True, prompts user to copy/paste responses
    
    # Human Choice Configuration
    human_choice_chance: float = 0.0  # Range 0-100, probability of triggering choice scenario
    no_human_chances: bool = False  # If True, disables human choice chance entirely
    choice_mode: int = 1  # 0=error, 1=disabled, 2=first, 3=second, 4=random, 5=AI choice, 6=human choice
    
    # Database Configuration
    knowledge_db_name: str = "Knowledge Database"
    knowledge_db_max_size: int = 20
    
    # Presentation Configuration
    slide_count_target: int = 50
    ai_role_prompt: str = (
        "You are assisting with the creation of a detailed teaching plan, "
        "then later slides to be used to teach a topic. Aim for the detail "
        "level of a teaching plan with high specificity. Do NOT assume you "
        "know anything for sure, as the first thing you will now do is a research phase."
    )
    
    # Input Configuration
    input_mode: int = 2  # 1=manual, 2=hardcoded, 3=file
    rewrite_prompt: bool = False
    manual_input_prompt: str = (
        "Module 2. LLM-Content\n"
        "Topic 2. LLM content generation and detection (2 weeks, 2 labs)\n"
        "2.1. LLM-content benchmarking datasets\n"
        "2.2. LLM-content detection\n"
        "2.3. Evading LLM detectors\n"
        "2.4. Watermarking LLM content"
    )
    
    # Logging Configuration
    suppress_logs: bool = False
    suppress_prints: bool = False


class PathManager:
    """Manages all file and directory paths for the automation system."""
    
    def __init__(self, base_dir: Optional[str] = None):
        # Look one level up from the polished_automation directory
        if base_dir:
            self.base_dir = Path(base_dir)
        else:
            # Get the parent of the polished_automation directory
            current_file_dir = Path(__file__).parent
            self.base_dir = current_file_dir.parent
        
        self._setup_paths()
    
    def _setup_paths(self):
        """Initialize all required paths."""
        self.api_key_path = self.base_dir / "key.txt"
        self.results_path = self.base_dir / "results"
        self.logs_path = self.base_dir / "logs"
        self.test_output_path = self.base_dir / "test_output"
        self.prompt_file_path = self.base_dir / "input_prompt.txt"
        
        # Create directories if they don't exist
        self._ensure_directories()
    
    def _ensure_directories(self):
        """Create necessary directories if they don't exist."""
        directories = [
            self.results_path,
            self.logs_path,
            self.test_output_path
        ]
        
        for directory in directories:
            directory.mkdir(exist_ok=True)
    
    def get_log_file_path(self, run_name: str) -> Path:
        """Get the full path for the log file."""
        return self.logs_path / f"log_{run_name}.txt"


class APIManager:
    """Manages OpenAI API client and call tracking."""
    
    def __init__(self, api_key: str, config: SystemConfig):
        self.api_key = api_key
        self.config = config
        self.client: Optional[OpenAI] = None
        self.calls_remaining: int = 0
        self._initialize_client()
        self._initialize_call_limit()
    
    def _initialize_client(self):
        """Initialize the OpenAI client."""
        if not self.config.use_manual_api:
            if not self.api_key:
                raise ValueError("API key is required but not provided")
            
            try:
                self.client = OpenAI(api_key=self.api_key)
                print_(f"OpenAI client initialized successfully")
            except Exception as e:
                raise RuntimeError(f"Failed to initialize OpenAI client: {e}")
        else:
            print_(f"Manual API mode enabled - user will provide responses")
    
    def _initialize_call_limit(self):
        """Initialize the API call limit counter."""
        if self.config.max_api_calls <= 0:
            raise ValueError("MAX_CALLS must be greater than 0")
        
        self.calls_remaining = self.config.max_api_calls
        print_(f"API call limit initialized: {self.calls_remaining} calls remaining")
    
    def can_make_call(self) -> bool:
        """Check if an API call can be made."""
        return self.calls_remaining > 0
    
    def make_call(self, message: str, no_chance: bool = False) -> Optional[str]:
        """Make an API call with proper error handling and call tracking."""
        if not self.can_make_call():
            print_(f"No API calls remaining. Limit: {self.config.max_api_calls}")
            return None
        
        # Check if human choice chance should be disabled
        if no_chance or self.config.no_human_chances:
            # Normal API call without choice scenario
            if self.config.use_manual_api:
                return self._manual_api_call(message)
            else:
                return self._automatic_api_call(message)
        
        # Check if choice scenario should be triggered
        import random
        chance_roll = random.uniform(0, 100)
        
        if chance_roll <= self.config.human_choice_chance:
            print_(f"🎲 Choice scenario triggered! (Rolled {chance_roll:.1f} <= {self.config.human_choice_chance})")
            return self._handle_choice_scenario(message)
        else:
            # Normal API call without choice scenario
            if self.config.use_manual_api:
                return self._manual_api_call(message)
            else:
                return self._automatic_api_call(message)
    
    def _manual_api_call(self, message: str) -> Optional[str]:
        """Handle manual API calls where user provides the response."""
        while True:
            print_("\n" + "="*80)
            print_("🤖 MANUAL API MODE - PROMPT TO SEND:")
            print_("="*80)
            print_(message)
            print_("="*80)
            print_("📋 Please copy the above prompt, send it to your AI service,")
            print_("   then paste the response below (or 'v'/'V' to retry):")
            
            response = input("\n📝 AI Response: ").strip()
            
            # Check for empty or accidental inputs
            if not response:
                print_("⚠️ Empty response received. Please try again.")
                continue
            
            if response.lower() in ['v', 'V']:
                print_("🔄 Retrying...")
                continue
            
            # Valid response received
            self.calls_remaining -= 1
            print_(f"✅ Response accepted. API calls remaining: {self.calls_remaining}")
            return response
    
    def _automatic_api_call(self, message: str) -> Optional[str]:
        """Handle automatic API calls using OpenAI client."""
        if not self.client:
            print_("Error: OpenAI client is not initialized")
            return None
        
        # Add delay to prevent calling too quickly
        import time
        time.sleep(0.1)
        
        try:
            response = self.client.chat.completions.create(
                model=self.config.openai_model,
                messages=[{"role": "user", "content": message}],
                temperature=self.config.temperature
            )
            
            self.calls_remaining -= 1
            
            # Log remaining calls at intervals
            if self.calls_remaining % (self.config.max_api_calls // 10) == 0:
                print_(f"API calls remaining: {self.calls_remaining}/{self.config.max_api_calls}")
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            print_(f"API call failed: {e}")
            return None
    
    def _handle_choice_scenario(self, message: str) -> Optional[str]:
        """Handle the choice scenario by making 2 API calls and selecting based on choice_mode."""
        print_(f"🎯 Choice scenario: Mode {self.config.choice_mode}")
        
        # Validate choice mode
        if self.config.choice_mode == 0:
            raise ValueError("Choice mode 0 is invalid - this should not be reached")
        elif self.config.choice_mode == 1:
            raise ValueError("Choice mode 1 should disable choice scenarios - this should not be reached")
        
        # Make 2 API calls with no_chance=True to prevent infinite recursion
        print_("🔄 Making first choice API call...")
        response1 = self._automatic_api_call(message) if not self.config.use_manual_api else self._manual_api_call(message)
        
        print_("🔄 Making second choice API call...")
        response2 = self._automatic_api_call(message) if not self.config.use_manual_api else self._manual_api_call(message)
        
        if not response1 or not response2:
            print_("⚠️ One or both choice API calls failed, using first available response")
            return response1 if response1 else response2
        
        # Handle choice selection based on mode
        if self.config.choice_mode == 2:
            print_("✅ Choice mode 2: Selecting first response")
            return response1
        elif self.config.choice_mode == 3:
            print_("✅ Choice mode 3: Selecting second response")
            return response2
        elif self.config.choice_mode == 4:
            import random
            choice = random.choice([response1, response2])
            print_(f"✅ Choice mode 4: Randomly selected {'first' if choice == response1 else 'second'} response")
            return choice
        elif self.config.choice_mode == 5:
            return self._make_ai_choice(message, response1, response2)
        elif self.config.choice_mode == 6:
            return self._get_user_choice(response1, response2)
        else:
            raise ValueError(f"Invalid choice mode: {self.config.choice_mode}")
    
    def _make_ai_choice(self, original_message: str, response1: str, response2: str) -> str:
        """Make an AI choice between two responses."""
        print_("🤖 AI choice mode: Asking AI to select between options...")
        
        choice_prompt = f"""You need to choose between two different responses to the same prompt.

Original prompt: {original_message}

Response 1: {response1}

Response 2: {response2}

Please choose which response is better by responding with ONLY "1" or "2". Do not include any other text or explanation."""
        
        try:
            # Make AI choice call with no_chance=True to prevent recursion
            choice_response = self._automatic_api_call(choice_prompt) if not self.config.use_manual_api else self._manual_api_call(choice_prompt)
            
            if not choice_response:
                print_("⚠️ AI choice call failed, selecting randomly")
                import random
                return random.choice([response1, response2])
            
            # Parse the choice
            choice_text = choice_response.strip().lower()
            if "1" in choice_text:
                print_("✅ AI chose response 1")
                return response1
            elif "2" in choice_text:
                print_("✅ AI chose response 2")
                return response2
            else:
                print_(f"⚠️ Unclear AI choice response: '{choice_response}', selecting randomly")
                import random
                return random.choice([response1, response2])
                
        except Exception as e:
            print_(f"⚠️ Error in AI choice: {e}, selecting randomly")
            import random
            return random.choice([response1, response2])
    
    def _get_user_choice(self, response1: str, response2: str) -> str:
        """Get user choice between two responses."""
        print_("\n" + "="*80)
        print_("👤 HUMAN CHOICE MODE")
        print_("="*80)
        print_("You need to choose between two different responses:")
        print_("\n" + "-"*40)
        print_("RESPONSE 1:")
        print_("-"*40)
        print_(response1)
        print_("\n" + "-"*40)
        print_("RESPONSE 2:")
        print_("-"*40)
        print_(response2)
        print_("\n" + "-"*40)
        
        while True:
            try:
                choice = input("Enter '1' for Response 1, '2' for Response 2: ").strip()
                
                if choice == "1":
                    print_("✅ You chose Response 1")
                    return response1
                elif choice == "2":
                    print_("✅ You chose Response 2")
                    return response2
                else:
                    print_("❌ Invalid choice. Please enter '1' or '2'.")
                    
            except KeyboardInterrupt:
                print_("\n⚠️ Interrupted by user, selecting Response 1")
                return response1
            except Exception as e:
                print_(f"⚠️ Error getting user input: {e}, selecting Response 1")
                return response1


class LoggingManager:
    """Manages logging configuration and initialization."""
    
    def __init__(self, config: SystemConfig, path_manager: PathManager):
        self.config = config
        self.path_manager = path_manager
        self.run_name = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        self._configure_logging()
    
    def _configure_logging(self):
        """Configure the logging system."""
        # Update global logging configuration
        import logging_funcs
        logging_funcs.SUPPRESS_LOGS = self.config.suppress_logs
        logging_funcs.SUPPRESS_PRINTS = self.config.suppress_prints
        logging_funcs.LOGS_PATH = str(self.path_manager.get_log_file_path(self.run_name))
        
        # Initialize log file
        self._initialize_log_file()
    
    def _initialize_log_file(self):
        """Create and initialize the log file."""
        log_file_path = self.path_manager.get_log_file_path(self.run_name)
        
        try:
            with open(log_file_path, 'w', encoding='utf-8') as log_file:
                log_file.write("=== VICEROY-2025-PROJECT LOG FILE START ===\n")
                log_file.write(f"Run started at: {datetime.now().isoformat()}\n")
                log_file.write(f"Configuration: max_calls={self.config.max_api_calls}, "
                             f"slide_target={self.config.slide_count_target}\n")
                
                if self.config.suppress_logs:
                    log_file.write("(Note: Console output suppressed)\n")
                if self.config.suppress_prints:
                    log_file.write("(Note: Console printing suppressed)\n")
                
                log_file.write("-" * 50 + "\n\n")
                
            print_(f"Log file initialized: {log_file_path}")
            
        except Exception as e:
            print_(f"Error initializing log file: {e}")
            raise


class DatabaseManager:
    """Manages the knowledge database initialization."""
    
    def __init__(self, config: SystemConfig):
        self.config = config
        self.database: Optional[ai_database.AIDatabase] = None
        self._initialize_database()
    
    def _initialize_database(self):
        """Initialize the knowledge database."""
        try:
            self.database = ai_database.AIDatabase(
                name=self.config.knowledge_db_name,
                max_size=self.config.knowledge_db_max_size
            )
            print_(f"Knowledge database '{self.config.knowledge_db_name}' "
                  f"initialized with max size {self.config.knowledge_db_max_size}")
        except Exception as e:
            raise RuntimeError(f"Failed to initialize knowledge database: {e}")


class PromptManager:
    """Manages prompt input and processing."""
    
    def __init__(self, config: SystemConfig, path_manager: PathManager, api_manager: APIManager):
        self.config = config
        self.path_manager = path_manager
        self.api_manager = api_manager
    
    def get_initial_prompt(self) -> str:
        """Get the initial prompt based on the configured input mode."""
        prompt = self._get_raw_prompt()
        
        if self.config.rewrite_prompt:
            prompt = self._rewrite_prompt(prompt)
        
        return prompt
    
    def _get_raw_prompt(self) -> str:
        """Get the raw prompt based on input mode."""
        if self.config.input_mode == 1:
            return input("Enter your prompt: ").strip()
        
        elif self.config.input_mode == 2:
            return self.config.manual_input_prompt
        
        elif self.config.input_mode == 3:
            return self._read_prompt_from_file()
        
        else:
            raise ValueError(f"Invalid input mode: {self.config.input_mode}")
    
    def _read_prompt_from_file(self) -> str:
        """Read prompt from the configured file."""
        if not self.path_manager.prompt_file_path.exists():
            raise FileNotFoundError(
                f"Prompt file not found at {self.path_manager.prompt_file_path}"
            )
        
        try:
            with open(self.path_manager.prompt_file_path, 'r', encoding='utf-8') as f:
                prompt = f.read().strip()
                
            if not prompt:
                raise ValueError("Prompt file is empty")
                
            return prompt
            
        except Exception as e:
            raise RuntimeError(f"Error reading prompt file: {e}")
    
    def _rewrite_prompt(self, original_prompt: str) -> str:
        """Use AI to rewrite the prompt for clarity and professionalism."""
        print_("Rewriting prompt using AI...")
        
        rewrite_message = (
            f"Rewrite this prompt to be more usable, clear, and professional:\n\n{original_prompt}"
        )
        
        rewritten = self.api_manager.make_call(rewrite_message)
        
        if rewritten:
            print_("Prompt rewritten successfully")
            return rewritten.strip()
        else:
            print_("Warning: Failed to rewrite prompt. Using original.")
            return original_prompt


class AutomationCore:
    """Main orchestrator for the automation system setup and initialization."""
    
    def __init__(self, config: Optional[SystemConfig] = None):
        self.config = config or SystemConfig()
        self.path_manager: Optional[PathManager] = None
        self.api_manager: Optional[APIManager] = None
        self.logging_manager: Optional[LoggingManager] = None
        self.database_manager: Optional[DatabaseManager] = None
        self.prompt_manager: Optional[PromptManager] = None
        
        # Runtime state
        self.is_initialized = False
        self.run_name: Optional[str] = None
    
    def initialize(self, require_confirmation: bool = True) -> bool:
        """
        Initialize the entire automation system.
        
        Args:
            require_confirmation: Whether to require user confirmation before proceeding
            
        Returns:
            True if initialization successful, False otherwise
        """
        try:
            print_("=== VICEROY-2025-PROJECT INITIALIZATION ===")
            
            # Step 1: Setup paths
            self._setup_paths()
            
            # Step 2: Load API key
            api_key = self._load_api_key()
            
            # Step 3: Initialize logging
            self._initialize_logging()
            
            # Step 4: Initialize API manager
            self._initialize_api_manager(api_key)
            
            # Step 5: Initialize database
            self._initialize_database()
            
            # Step 6: Initialize prompt manager
            self._initialize_prompt_manager()
            
            # Step 7: User confirmation
            if require_confirmation:
                self._get_user_confirmation()
            
            self.is_initialized = True
            print_("=== INITIALIZATION COMPLETE ===")
            return True
            
        except Exception as e:
            print_(f"Initialization failed: {e}")
            return False
    
    def _setup_paths(self):
        """Setup path management."""
        self.path_manager = PathManager()
        print_("Path management initialized")
    
    def _load_api_key(self) -> str:
        """Load the API key from file."""
        # If using manual API mode, we don't need an API key
        if self.config.use_manual_api:
            print_("Manual API mode enabled - no API key required")
            return "manual_mode"
        
        if not self.path_manager.api_key_path.exists():
            raise FileNotFoundError(
                f"API key file not found at {self.path_manager.api_key_path}"
            )
        
        try:
            with open(self.path_manager.api_key_path, 'r') as f:
                api_key = f.read().strip()
            
            if not api_key:
                raise ValueError("API key file is empty")
            
            print_("API key loaded successfully")
            return api_key
            
        except Exception as e:
            raise RuntimeError(f"Error loading API key: {e}")
    
    def _initialize_logging(self):
        """Initialize logging system."""
        self.logging_manager = LoggingManager(self.config, self.path_manager)
        self.run_name = self.logging_manager.run_name
        print_("Logging system initialized")
    
    def _initialize_api_manager(self, api_key: str):
        """Initialize API management."""
        self.api_manager = APIManager(api_key, self.config)
        print_("API manager initialized")
    
    def _initialize_database(self):
        """Initialize database management."""
        self.database_manager = DatabaseManager(self.config)
        print_("Database manager initialized")
    
    def _initialize_prompt_manager(self):
        """Initialize prompt management."""
        self.prompt_manager = PromptManager(self.config, self.path_manager, self.api_manager)
        print_("Prompt manager initialized")
    
    def _get_user_confirmation(self):
        """Get user confirmation to proceed."""
        print_(f"\nSystem ready with {self.api_manager.calls_remaining} API calls remaining")
        input("Press Enter to continue with presentation generation...")
    
    def get_initial_prompt(self) -> str:
        """Get the initial prompt for presentation generation."""
        if not self.is_initialized:
            raise RuntimeError("System must be initialized before getting prompts")
        
        return self.prompt_manager.get_initial_prompt()
    
    def prepare_for_presentation_generation(self) -> Dict[str, Any]:
        """
        Prepare the system for presentation generation.
        This includes getting the initial prompt and setting up the generation context.
        This is the final step before Step 1 of the presentation generation process.
        
        Returns:
            Dictionary containing all the prepared data needed for generation
        """
        if not self.is_initialized:
            raise RuntimeError("System must be initialized before preparing for generation")
        
        print_("=== PREPARING FOR PRESENTATION GENERATION ===")
        
        # Get the initial prompt
        prompt = self.get_initial_prompt()
        print_("\nFinal Prompt:")
        print_(prompt)
        
        # Calculate initial topic count based on slide target
        initial_topic_count = max(2, int(self.config.slide_count_target / 12))
        
        # Calculate research parameters
        second_research_round_topic_count = max(3, initial_topic_count * 3)
        database_entries_per_topic = int(self.config.knowledge_db_max_size / 
                                       (initial_topic_count + second_research_round_topic_count))
        
        if database_entries_per_topic < 1:
            raise ValueError("Not enough database size to research these topics at all.")
        
        print_(f"📊 Generation Parameters:")
        print_(f"   - Initial topic count: {initial_topic_count}")
        print_(f"   - Second research round topics: {second_research_round_topic_count}")
        print_(f"   - Database entries per topic: {database_entries_per_topic}")
        print_(f"   - Total slide target: {self.config.slide_count_target}")
        
        # Prepare the generation context
        generation_context = {
            "prompt": prompt,
            "initial_topic_count": initial_topic_count,
            "second_research_round_topic_count": second_research_round_topic_count,
            "database_entries_per_topic": database_entries_per_topic,
            "slide_count_target": self.config.slide_count_target,
            "ai_role_prompt": self.config.ai_role_prompt,
            "knowledge_db": self.database_manager.database,
            "api_manager": self.api_manager,
            "run_name": self.run_name
        }
        
        print_("✅ Preparation complete. Ready for Step 1.")
        return generation_context
    
    def create_step_1_prompt(self, generation_context: Dict[str, Any]) -> str:
        """
        Create the Step 1 prompt for generating initial research topics.
        This is the first AI call in the presentation generation process.
        
        Args:
            generation_context: The context prepared by prepare_for_presentation_generation()
            
        Returns:
            The formatted prompt string for Step 1
        """
        prompt = generation_context["prompt"]
        ai_role_prompt = generation_context["ai_role_prompt"]
        initial_topic_count = generation_context["initial_topic_count"]
        
        # Build the instructions for Step 1
        built_in_instructions = (
            "You will generate a preliminary research topic list based upon what you think "
            "you may know on the topic. Based on the results you will do more research later. "
            "Answer ONLY with a **COMMA-SEPERATED** list of exactly # topics and nothing else. "
            "(**COMMA-SEPERATED**!!)"
        ).replace("#", str(initial_topic_count))
        
        # Create the full Step 1 prompt (matching original format exactly)
        full_step_1_prompt = (
            f"Topic Prompt: ({prompt}) "
            f"AI Role: ({ai_role_prompt}) "
            f"Specific Instructions: ({built_in_instructions})"
        )
        
        return full_step_1_prompt
    
    def execute_step_1(self, generation_context: Dict[str, Any]) -> list[str]:
        """
        Execute Step 1: Generate initial research topics.
        This makes the first AI call to get a comma-separated list of research topics.
        
        Args:
            generation_context: The context prepared by prepare_for_presentation_generation()
            
        Returns:
            List of research topics
        """
        if not self.is_initialized:
            raise RuntimeError("System must be initialized before executing Step 1")
        
        print_("Step 1 begun.")
        
        # Create Step 1 prompt
        step_1_prompt = self.create_step_1_prompt(generation_context)
        
        # Make the API call
        raw_step_1_response = self.api_manager.make_call(step_1_prompt)
        
        print_("Raw AI topic response: " + str(raw_step_1_response))
        
        if raw_step_1_response is None:
            raise RuntimeError("No AI response given for Step 1")
        
        # Parse the comma-separated response
        split_topics = raw_step_1_response.split(",")
        for i in range(len(split_topics)):
            split_topics[i] = split_topics[i].strip(" \t\n.,[]{}()0123456789")
        
        initial_topic_count = generation_context["initial_topic_count"]
        
        if len(split_topics) < initial_topic_count:
            raise RuntimeError(
                f"{len(split_topics)} topics provided. {initial_topic_count} expected. "
                f"Got: {split_topics}"
            )
        
        if len(split_topics) > initial_topic_count:
            split_topics = split_topics[:initial_topic_count]
        
        print_("Selected topics: " + str(split_topics))
        print_("Step 1 Complete.")
        
        return split_topics
    
    def execute_step_2(self, generation_context: Dict[str, Any], topics: list[str]) -> None:
        """
        Execute Step 2: Research the initial topics and populate the knowledge database.
        This performs research on each topic and adds entries to the database.
        
        Args:
            generation_context: The context prepared by prepare_for_presentation_generation()
            topics: List of topics from Step 1
        """
        if not self.is_initialized:
            raise RuntimeError("System must be initialized before executing Step 2")
        
        print_("Step 2 begun.")
        
        # Get parameters from generation context
        prompt = generation_context["prompt"]
        database_entries_per_topic = generation_context["database_entries_per_topic"]
        knowledge_db = generation_context["knowledge_db"]
        
        # Research prompts
        RESEARCH_PROMPT = (
            "You are to perform a web-search to research the topic given on the general category "
            "from the initial prompt. Avoid redoing research from titles previously used. These are: #1. "
            "Be specific and assume the user of this database has no background knowledge. "
            "You are focusing on the topic **#2** and this is entry #3 for this topic."
        )
        STRUCTURE_PROMPT_STEP_2 = (
            "Respond in a Python Dictionary style format. This dictionary needs to have fields "
            "title (str), keywords (list[str]), text (str), and link (str). "
            "Fill these out as you wish with researched information. Respond with nothing else. Be on-topic!"
        )
        
        existing_entry_titles = []
        
        for topic in topics:
            print_(f"Researching topic: {topic}")
            for i in range(database_entries_per_topic):
                # Small safety delay
                import time
                time.sleep(0.1)
                
                # Build the prompt for research
                specific_research_prompt = (
                    f"Initial Prompt: ({prompt}) "
                    f"AI Role: ({RESEARCH_PROMPT}) "
                    f"Specific Instructions: ({STRUCTURE_PROMPT_STEP_2})"
                )
                
                if existing_entry_titles == []:
                    specific_research_prompt = specific_research_prompt.replace("#1", "(None)")
                else:
                    specific_research_prompt = specific_research_prompt.replace("#1", str(existing_entry_titles))
                
                specific_research_prompt = specific_research_prompt.replace("#3", str(i + 1))
                specific_research_prompt = specific_research_prompt.replace("#2", topic.upper())
                
                # Make the API call
                print_("Prompt:\n" + specific_research_prompt + "\nTo be sent to the AI.")
                
                raw_step_2_response = self.api_manager.make_call(specific_research_prompt)
                
                print_("Raw AI response to this: " + str(raw_step_2_response))
                
                if raw_step_2_response is None:
                    print_("Error: During research, AI failed to respond.")
                    continue
                
                # Parse the response
                try:
                    import ast
                    step_2_dictionary = ast.literal_eval(raw_step_2_response)
                except:
                    print_("Error: Incorrect format during step 2 research.")
                    continue
                
                if type(step_2_dictionary) != dict:
                    print_("Error: Response not a dictionary.")
                    continue
                
                # Validate required fields
                needed_keys = ["title", "keywords", "text", "link"]
                needed_types = [str, list, str, str]
                no_missing_keys = True
                
                for j in range(len(needed_keys)):
                    needed_key = needed_keys[j]
                    needed_type = needed_types[j]
                    if not (needed_key in list(step_2_dictionary.keys())):
                        print_(f"Error: {needed_key} not given in step 2 research dictionary.")
                        no_missing_keys = False
                        break
                    
                    if type(step_2_dictionary[needed_key]) != needed_type:
                        print_(f"Error: {needed_key} does not contain data of type {needed_type}.")
                        no_missing_keys = False
                        break
                
                if not no_missing_keys:
                    continue
                
                # Add entry to database
                if knowledge_db.add_entry(
                    step_2_dictionary["title"],
                    step_2_dictionary["keywords"],
                    step_2_dictionary["text"],
                    step_2_dictionary["link"]
                ):
                    existing_entry_titles.append(step_2_dictionary["title"])
                    print_("Added Entry to database. Displaying.")
                    print_(str(knowledge_db.entries[-1]))
                else:
                    print_("Error: Knowledge Database out of space.")
                    continue
        
        print_("Step 2 Complete.")
    
    def create_step_3_prompt(self, generation_context: Dict[str, Any], topics_step_1: list[str]) -> str:
        """
        Create the Step 3 prompt to expand the topic list based on initial research.
        Uses the knowledge database text and the initial topics to request more topics.
        """
        prompt = generation_context["prompt"]
        ai_role_prompt = generation_context["ai_role_prompt"]
        second_research_round_topic_count = generation_context["second_research_round_topic_count"]
        knowledge_db = generation_context["knowledge_db"]

        # Assemble the mega-prompt
        STEP_3_STRUCTURE_PROMPT = (
            "You are continuing a research topic list based upon initial reserach. "
            "The inital topics were #1. The research these yeilded is: ({#2}). "
            "You need to give #3 more topics. Make them unique and full correspond to the intial prompt "
            "based upon your role, and be selected with the info you got from the research text. "
            "Ensure they do not rely on the context of previous topic names to be sensical. "
            "Respond in a comma-seperated list of topics with nothing else. Again, **COMMA-SEPERATED**!!"
        )

        final_prompt_step_3 = (
            f"Initial Prompt: ({prompt}) "
            f"Role Prompt: ({ai_role_prompt}) "
            f"Specific Instructions: ({STEP_3_STRUCTURE_PROMPT})"
        )

        research_text = knowledge_db.get_all_text()
        if len(research_text) > 1000:
            research_text = research_text[:1000] + " (Truncated for brevity.)"

        final_prompt_step_3 = final_prompt_step_3.replace("#1", str(topics_step_1))
        final_prompt_step_3 = final_prompt_step_3.replace("#3", str(second_research_round_topic_count))
        final_prompt_step_3 = final_prompt_step_3.replace("#2", research_text)

        return final_prompt_step_3

    def execute_step_3(self, generation_context: Dict[str, Any], topics_step_1: list[str]) -> list[str]:
        """
        Execute Step 3: Generate additional topics based on initial research and database content.
        Returns the new list of topics for the second research round.
        """
        if not self.is_initialized:
            raise RuntimeError("System must be initialized before executing Step 3")

        print_("Step 3 begun.")

        # Build and send the prompt
        step_3_prompt = self.create_step_3_prompt(generation_context, topics_step_1)
        print_("Following Prompt sent to AI:\n" + step_3_prompt + "\n.")
        raw_step_3_response = self.api_manager.make_call(step_3_prompt)

        # Validate response
        print_("Raw AI topic response: " + str(raw_step_3_response))

        if raw_step_3_response is None:
            raise RuntimeError("No AI response given for Step 3")

        split_topics_2 = raw_step_3_response.split(",")
        for i in range(len(split_topics_2)):
            split_topics_2[i] = split_topics_2[i].strip(" \t\n.,[]{}()0123456789")

        expected_count = generation_context["second_research_round_topic_count"]
        if len(split_topics_2) < expected_count:
            raise RuntimeError(
                f"{len(split_topics_2)} topics provided. {expected_count} expected. Got: {split_topics_2}"
            )
        if len(split_topics_2) > expected_count:
            split_topics_2 = split_topics_2[:expected_count]

        print_("Selected topics: " + str(split_topics_2))
        print_("Step 3 Complete.")
        return split_topics_2
    
    def execute_step_4(self, generation_context: Dict[str, Any], topics_step_3: list[str]) -> None:
        """
        Execute Step 4: Research the additional topics from Step 3 and populate the knowledge database.
        This is essentially the same as Step 2 but for the second round of topics.
        
        Args:
            generation_context: The context prepared by prepare_for_presentation_generation()
            topics_step_3: List of topics from Step 3
        """
        if not self.is_initialized:
            raise RuntimeError("System must be initialized before executing Step 4")
        
        print_("Step 4 begun.")
        
        # Get parameters from generation context
        prompt = generation_context["prompt"]
        database_entries_per_topic = generation_context["database_entries_per_topic"]
        knowledge_db = generation_context["knowledge_db"]
        
        # Research prompts (same as Step 2)
        RESEARCH_PROMPT_2 = (
            "You are to perform a web-search to research the topic given on the general category "
            "from the initial prompt. Avoid redoing research from titles previously used. These are: #1. "
            "Be specific and assume the user of this database has no background knowledge. "
            "You are focusing on the topic **#2** and this is entry #3 for this topic."
        )
        STRUCTURE_PROMPT_STEP_4 = (
            "Respond in a Python Dictionary style format. This dictionary needs to have fields "
            "title (str), keywords (list[str]), text (str), and link (str). "
            "Fill these out as you wish with researched information. Respond with nothing else. Be on-topic!"
        )
        
        # Get existing entry titles to avoid duplicates
        existing_entry_titles = [entry.title for entry in knowledge_db.entries]
        
        for topic in topics_step_3:
            print_(f"Researching topic: {topic}")
            for i in range(database_entries_per_topic):
                # Small safety delay
                import time
                time.sleep(0.1)
                
                # Build the prompt for research
                specific_research_prompt = (
                    f"Initial Prompt: ({prompt}) "
                    f"AI Role: ({RESEARCH_PROMPT_2}) "
                    f"Specific Instructions: ({STRUCTURE_PROMPT_STEP_4})"
                )
                
                if existing_entry_titles == []:
                    specific_research_prompt = specific_research_prompt.replace("#1", "(None)")
                else:
                    specific_research_prompt = specific_research_prompt.replace("#1", str(existing_entry_titles))
                
                specific_research_prompt = specific_research_prompt.replace("#3", str(i + 1))
                specific_research_prompt = specific_research_prompt.replace("#2", topic.upper())
                
                # Make the API call
                print_("Prompt:\n" + specific_research_prompt + "\nTo be sent to the AI.")
                
                raw_step_4_response = self.api_manager.make_call(specific_research_prompt)
                
                print_("Raw AI response to this: " + str(raw_step_4_response))
                
                if raw_step_4_response is None:
                    print_("Error: During research, AI failed to respond.")
                    continue
                
                # Parse the response
                try:
                    import ast
                    step_4_dictionary = ast.literal_eval(raw_step_4_response)
                except:
                    print_("Error: Incorrect format during step 4 research.")
                    continue
                
                if type(step_4_dictionary) != dict:
                    print_("Error: Response not a dictionary.")
                    continue
                
                # Validate required fields
                needed_keys = ["title", "keywords", "text", "link"]
                needed_types = [str, list, str, str]
                no_missing_keys = True
                
                for j in range(len(needed_keys)):
                    needed_key = needed_keys[j]
                    needed_type = needed_types[j]
                    if not (needed_key in list(step_4_dictionary.keys())):
                        print_(f"Error: {needed_key} not given in step 4 research dictionary.")
                        no_missing_keys = False
                        break
                    
                    if type(step_4_dictionary[needed_key]) != needed_type:
                        print_(f"Error: {needed_key} does not contain data of type {needed_type}.")
                        no_missing_keys = False
                        break
                
                if not no_missing_keys:
                    continue
                
                # Add entry to database
                if knowledge_db.add_entry(
                    step_4_dictionary["title"],
                    step_4_dictionary["keywords"],
                    step_4_dictionary["text"],
                    step_4_dictionary["link"]
                ):
                    existing_entry_titles.append(step_4_dictionary["title"])
                    print_("Added Entry to database. Displaying.")
                    print_(str(knowledge_db.entries[-1]))
                else:
                    print_("Error: Knowledge Database out of space.")
                    continue
        
        print_("Step 4 Complete.")
    
    def execute_step_4_5(self, generation_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute Step 4.5: Create detailed teaching outline and slide breakdown.
        This step determines the final presentation structure and creates a comprehensive teaching plan.
        
        Args:
            generation_context: The context prepared by prepare_for_presentation_generation()
            
        Returns:
            Dictionary containing the teaching outline and slide breakdown data
        """
        if not self.is_initialized:
            raise RuntimeError("System must be initialized before executing Step 4.5")
        
        print_("Step 4.5 begun.")
        
        # Get parameters from generation context
        prompt = generation_context["prompt"]
        ai_role_prompt = generation_context["ai_role_prompt"]
        slide_count_target = generation_context["slide_count_target"]
        knowledge_db = generation_context["knowledge_db"]
        
        # Step 4.5A: Determine final topic breakdown
        print_("Step 4.5A: Determining final topic breakdown...")
        
        STRUCTURE_PROMPT_STEP_4_5A = (
            "Given the previous information and the following comprehensive database text sample, "
            "you will decide how many main topics/sections will be in this presentation. "
            "Database sample: ({#1}). "
            "Carefully analyze the database content to determine the optimal number of topics "
            "that will comprehensively cover the subject matter. "
            "Respond only with a single number and nothing else. "
            "Ensure the number is reasonable for a teaching presentation. Soft max of 16."
        )
        
        # Get a more comprehensive database sample for better context
        summary_sample_database_text = knowledge_db.get_sample_text(max_entries=None, max_chars_per_entry=300)
        
        full_step_4_5A_prompt = (
            f"Initial Prompt: ({prompt}) "
            f"Role Prompt: ({ai_role_prompt}) "
            f"Specific Instructions: ({STRUCTURE_PROMPT_STEP_4_5A})"
        ).replace("#1", summary_sample_database_text)
        
        print_("Prompt to AI:\n" + full_step_4_5A_prompt + "\n.")
        raw_step_4_5A_response = self.api_manager.make_call(full_step_4_5A_prompt)
        print_("Raw response:\n" + str(raw_step_4_5A_response) + "\n.")
        
        if raw_step_4_5A_response is None:
            raise RuntimeError("No AI response given for Step 4.5A")
        
        # Validate that this is just a single numeral
        try:
            import ast
            total_topics_count = ast.literal_eval(raw_step_4_5A_response.strip())
            if type(total_topics_count) != int:
                raise RuntimeError("Non-number received for topic amount")
        except:
            raise RuntimeError("Invalid response format for topic count")
        
        if total_topics_count < 1:
            raise RuntimeError(f"Cannot have 0 topics or fewer. Had {total_topics_count}.")
        
        max_topics = 100
        if total_topics_count > max_topics:
            raise RuntimeError(f"Cannot have more than {max_topics} topics. Had {total_topics_count}.")
        
        print_(f"Topic count decided: {total_topics_count}")
        
        # Step 4.5B: Create detailed teaching outline
        print_("Step 4.5B: Creating detailed teaching outline...")
        
        STRUCTURE_PROMPT_STEP_4_5B = (
            "Given the previous information and the following comprehensive database text sample, "
            "you are going to create a detailed teaching outline for senior undergraduate students. "
            "Database sample: ({#1}). "
            "You are to come up with {#2} main topics/sections organized in a weekly module structure. "
            "Carefully analyze the database content to ensure your topics directly relate to and "
            "comprehensively cover the research material available. "
            "For each topic, create a detailed breakdown including: "
            "- Main topic title (based on database content) "
            "- 3-5 sub-topics that will be covered (derived from database research) "
            "- Brief explanation of what each sub-topic covers (with specific references to database content) "
            "- Learning objectives for this topic "
            "- Estimated number of slides needed for this topic "
            "- Lab activities or practical exercises for this topic "
            "- Real-world applications and examples "
            "Structure this as a comprehensive teaching plan suitable for 3 credit hours. "
            "Ensure progressive complexity from basic to advanced concepts. "
            "Make this comprehensive and suitable for a detailed teaching presentation "
            "that fully utilizes the available research database and serves as primary learning material."
        )
        
        full_step_4_5B_prompt = (
            f"Initial Prompt: ({prompt}) "
            f"Role Prompt: ({ai_role_prompt}) "
            f"Specific Instructions: ({STRUCTURE_PROMPT_STEP_4_5B})"
        ).replace("#1", summary_sample_database_text).replace("#2", str(total_topics_count))
        
        print_("Prompt to AI:\n" + full_step_4_5B_prompt + "\n.")
        raw_step_4_5B_response = self.api_manager.make_call(full_step_4_5B_prompt)
        print_("Raw response:\n" + str(raw_step_4_5B_response) + "\n.")
        
        if raw_step_4_5B_response is None:
            raise RuntimeError("No AI response given for Step 4.5B")
        
        teaching_outline = raw_step_4_5B_response.strip()
        print_("Teaching outline created successfully.")
        
        # Step 4.5C: Determine slide allocation per topic
        print_("Step 4.5C: Determining slide allocation per topic...")
        
        STRUCTURE_PROMPT_STEP_4_5C = (
            "Based on the teaching outline provided, determine how many slides each topic should have. "
            "Teaching outline: ({#1}). "
            "Total slides available: {#2}. "
            "Topics to allocate: {#3}. "
            "Respond as a python list of integers. These numbers match to the topic of matching index. "
            "Respond with nothing else at all. Follow output format exactly. PYTHON LIST!!! ENSURE []s are used!!!!"
        )
        
        full_step_4_5C_prompt = (
            f"Initial Prompt: ({prompt}) "
            f"Role Prompt: ({ai_role_prompt}) "
            f"Specific Instructions: ({STRUCTURE_PROMPT_STEP_4_5C})"
        ).replace("#1", teaching_outline).replace("#2", str(slide_count_target)).replace("#3", str(total_topics_count))
        
        print_("Prompt to AI:\n" + full_step_4_5C_prompt + "\n.")
        raw_step_4_5C_response = self.api_manager.make_call(full_step_4_5C_prompt)
        print_("Raw response:\n" + str(raw_step_4_5C_response) + "\n.")
        
        if raw_step_4_5C_response is None:
            raise RuntimeError("No AI response given for Step 4.5C")
        
        # Parse the slide allocation list
        try:
            # Extract the list from the response
            start_idx = raw_step_4_5C_response.find('[')
            end_idx = raw_step_4_5C_response.rfind(']') + 1
            if start_idx == -1 or end_idx == 0:
                print_("No Python list found in slide allocation response. Attempting to transform...")
                quantity_list = self._transform_response_to_list(raw_step_4_5C_response, total_topics_count, "integers")
            else:
                quantity_list = ast.literal_eval(raw_step_4_5C_response.strip())
            
            if type(quantity_list) != list:
                raise RuntimeError("Non-list received for slides per topic")
            
            if len(quantity_list) != total_topics_count:
                print_(f"Warning: Received {len(quantity_list)} allocations, expected {total_topics_count}")
                # Try to fix the list length
                quantity_list = self._fix_list_length(quantity_list, total_topics_count)
                total_topics_count = len(quantity_list)
            
        except Exception as e:
            print_(f"Error parsing slide allocation: {e}")
            print_("Attempting to transform slide allocation response...")
            quantity_list = self._transform_response_to_list(raw_step_4_5C_response, total_topics_count, "integers")
        
        # Ensure minimum 1 slide per topic and redistribute excess/deficit
        # Handle potential string values like "10 (continued)" by extracting just the number
        cleaned_quantity_list = []
        for q in quantity_list:
            if isinstance(q, str):
                # Extract the first number from the string
                import re
                numbers = re.findall(r'\d+', str(q))
                if numbers:
                    cleaned_quantity_list.append(int(numbers[0]))
                else:
                    cleaned_quantity_list.append(1)  # Default to 1 if no number found
            else:
                cleaned_quantity_list.append(int(q))
        
        quantity_list = [max(1, q) for q in cleaned_quantity_list]
        
        # Handle excess slides
        extra_slides = slide_count_target - sum(quantity_list)
        while extra_slides > 0:
            for i in range(total_topics_count):
                extra_slides -= 1
                quantity_list[i] += 1
                if extra_slides == 0:
                    break
        
        # Handle deficit slides
        while extra_slides < 0:
            if sum(quantity_list) == total_topics_count:
                break
            
            for i in range(total_topics_count):
                extra_slides += 1
                quantity_list[i] -= 1
                if quantity_list[i] < 1:
                    extra_slides += quantity_list[i] - 1
                    quantity_list[i] = 1
                if extra_slides == 0:
                    break
        
        print_(f"Slide allocation: {quantity_list}")
        
        # Step 4.5D: Create specific slide topics from outline
        print_("Step 4.5D: Creating specific slide topics from outline...")
        
        STRUCTURE_PROMPT_STEP_4_5D = (
            "Based on the teaching outline, slide allocation, and comprehensive database content, create specific topics for each slide. "
            "Teaching outline: ({#1}). "
            "Slide allocation per topic: {#2}. "
            "Database content for reference: ({#4}). "
            "Create a python list of strings, where each string is the specific topic/title for one slide. "
            "The list should have exactly {#3} items (total slides). "
            "Make each slide topic specific and actionable for teaching, ensuring they directly relate to "
            "the research content in the database. "
            "Respond with nothing else - just the list."
        )
        
        full_step_4_5D_prompt = (
            f"Initial Prompt: ({prompt}) "
            f"Role Prompt: ({ai_role_prompt}) "
            f"Specific Instructions: ({STRUCTURE_PROMPT_STEP_4_5D})"
        ).replace("#1", teaching_outline).replace("#2", str(quantity_list)).replace("#3", str(slide_count_target)).replace("#4", summary_sample_database_text)
        
        print_("Prompt to AI:\n" + full_step_4_5D_prompt + "\n.")
        raw_step_4_5D_response = self.api_manager.make_call(full_step_4_5D_prompt)
        print_("Raw response:\n" + str(raw_step_4_5D_response) + "\n.")
        
        if raw_step_4_5D_response is None:
            raise RuntimeError("No AI response given for Step 4.5D")
        
        # Parse the slide topics list
        try:
            # Extract the list from the response
            start_idx = raw_step_4_5D_response.find('[')
            end_idx = raw_step_4_5D_response.rfind(']') + 1
            if start_idx == -1 or end_idx == 0:
                # Try to transform the response into a proper Python list
                print_("No Python list found in response. Attempting to transform response...")
                slide_topics_list = self._transform_response_to_list(raw_step_4_5D_response, slide_count_target)
            else:
                list_str = raw_step_4_5D_response[start_idx:end_idx]
                slide_topics_list = ast.literal_eval(list_str.strip())
            
            if type(slide_topics_list) != list:
                raise RuntimeError("Non-list received for slide topics")
            
            if len(slide_topics_list) != slide_count_target:
                print_(f"Warning: Received {len(slide_topics_list)} slide topics, expected {slide_count_target}")
                # Try to fix the list length with context for generating more items
                slide_topics_list = self._fix_list_length(slide_topics_list, slide_count_target, "strings", teaching_outline)
            
        except Exception as e:
            print_(f"Error parsing slide topics: {e}")
            print_("Attempting to transform response to proper format...")
            slide_topics_list = self._transform_response_to_list(raw_step_4_5D_response, slide_count_target)
        
        print_(f"Slide topics created: {len(slide_topics_list)} topics")
        
        # Step 4.5E: Save teaching plan to file
        print_("Step 4.5E: Saving teaching plan to file...")
        
        # Save to file
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        
        # Create the teaching plan content
        teaching_plan_content = f"""VICEROY-2025-PROJECT: Detailed Teaching Plan
Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
Run: {self.run_name}

ORIGINAL PROMPT:
{prompt}

TEACHING OUTLINE:
{teaching_outline}

SLIDE ALLOCATION:
{quantity_list}

DETAILED SLIDE TOPICS:
"""
        
        for i, topic in enumerate(slide_topics_list):
            teaching_plan_content += f"{i+1:2d}. {topic}\n"
        
        filename = f"teaching_outline_{timestamp}.txt"
        filepath = self.path_manager.results_path / filename
        
        print_(f"Attempting to save teaching plan to: {filepath}")
        print_(f"Results path: {self.path_manager.results_path}")
        print_(f"File exists: {filepath.exists()}")
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(teaching_plan_content)
            print_(f"Teaching plan saved successfully to: {filepath}")
        except Exception as e:
            print_(f"Error saving teaching plan: {e}")
            raise
        
        # Prepare return data
        step_4_5_data = {
            "total_topics_count": total_topics_count,
            "teaching_outline": teaching_outline,
            "slide_allocation": quantity_list,
            "slide_topics_list": slide_topics_list,
            "teaching_plan_file": str(filepath)
        }
        
        print_("Step 4.5 Complete.")
        return step_4_5_data
    
    def execute_step_4_6(self, generation_context: Dict[str, Any], step_4_5_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute Step 4.6: Detailed Lecture Notes Generation"""
        print_("Step 4.6: Detailed Lecture Notes Generation")
        
        prompt = generation_context["prompt"]
        ai_role_prompt = generation_context["ai_role_prompt"]
        knowledge_db = generation_context["knowledge_db"]
        teaching_outline = step_4_5_data["teaching_outline"]
        slide_topics_list = step_4_5_data["slide_topics_list"]
        
        # Get comprehensive database sample for detailed content
        database_sample = knowledge_db.get_sample_text(max_entries=None, max_chars_per_entry=500)
        
        print_("Step 4.6A: Generating comprehensive lecture notes...")
        
        LECTURE_NOTES_PROMPT = (
            "Based on the teaching outline and slide topics, create comprehensive lecture notes "
            "for senior undergraduate students. This will serve as the primary learning material. "
            "Teaching outline: ({#1}). "
            "Slide topics: ({#2}). "
            "Database content: ({#3}). "
            "Create detailed, thorough lecture notes that include: "
            "- Comprehensive explanations of each concept "
            "- Real-world examples and applications "
            "- Figures, diagrams, and visual elements (described in text) "
            "- Practical exercises and case studies "
            "- Learning objectives and key takeaways "
            "- Assessment questions and discussion points "
            "Structure the notes to be self-contained and comprehensive enough "
            "for students to learn from without additional reading materials. "
            "Target 3 credit hours of content depth and complexity."
        )
        
        full_lecture_notes_prompt = (
            f"Initial Prompt: ({prompt}) "
            f"Role Prompt: ({ai_role_prompt}) "
            f"Specific Instructions: ({LECTURE_NOTES_PROMPT})"
        ).replace("#1", teaching_outline).replace("#2", str(slide_topics_list)).replace("#3", database_sample)
        
        print_("Generating comprehensive lecture notes...")
        lecture_notes_response = self.api_manager.make_call(full_lecture_notes_prompt)
        
        if not lecture_notes_response:
            raise RuntimeError("Failed to generate lecture notes")
        
        lecture_notes = lecture_notes_response.strip()
        
        # Save lecture notes to file
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"lecture_notes_{timestamp}.txt"
        filepath = self.path_manager.results_path / filename
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(f"""VICEROY-2025-PROJECT: Comprehensive Lecture Notes
Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
Run: {self.run_name}

ORIGINAL PROMPT:
{prompt}

TEACHING OUTLINE:
{teaching_outline}

COMPREHENSIVE LECTURE NOTES:
{lecture_notes}
""")
            print_(f"Lecture notes saved successfully to: {filepath}")
        except Exception as e:
            print_(f"Error saving lecture notes: {e}")
            raise
        
        # Validate content depth and comprehensiveness
        print_("Step 4.6B: Validating content depth and comprehensiveness...")
        
        validation_prompt = (
            f"Review the following lecture notes for comprehensiveness and depth: "
            f"{lecture_notes[:2000]}... "
            f"Assess if this content is suitable for 3 credit hours of senior undergraduate study. "
            f"Check for: "
            f"- Sufficient depth and detail "
            f"- Real-world examples and applications "
            f"- Progressive complexity from basic to advanced "
            f"- Self-contained learning material "
            f"Respond with 'VALID' if suitable, or specific improvement suggestions if not."
        )
        
        validation_response = self.api_manager.make_call(validation_prompt)
        
        if validation_response and "VALID" in validation_response.upper():
            print_("✅ Content validation passed - suitable for 3 credit hours")
        else:
            print_(f"⚠️ Content validation suggestions: {validation_response}")
        
        step_4_6_data = {
            "lecture_notes": lecture_notes,
            "lecture_notes_file": str(filepath),
            "content_validation": validation_response if validation_response else "Validation failed"
        }
        
        print_("Step 4.6 Complete.")
        return step_4_6_data
    
    def execute_step_5(self, generation_context: Dict[str, Any], slide_topics_list: Optional[list] = None) -> Dict[str, Any]:
        """Execute Step 5: Educational Structure Validation"""
        print_("Step 5: Educational Structure Validation")
        
        prompt = generation_context["prompt"]
        slide_count_target = generation_context["slide_count_target"]
        
        print_(f"Step 5: Validating educational structure for {slide_count_target} slides")
        print_(f"Topic: {prompt}")
        
        if slide_topics_list:
            print_(f"Step 5: Validating {len(slide_topics_list)} slide topics from step 4.5")
        
        # Validate educational structure
        print_("Step 5A: Validating credit hour alignment...")
        expected_slides_per_credit = 15  # Rough estimate: 15 slides per credit hour
        expected_slides = 3 * expected_slides_per_credit  # 3 credit hours
        
        if slide_count_target >= expected_slides * 0.8 and slide_count_target <= expected_slides * 1.2:
            print_(f"✅ Slide count ({slide_count_target}) aligns with 3 credit hours (expected ~{expected_slides})")
        else:
            print_(f"⚠️ Slide count ({slide_count_target}) may not align with 3 credit hours (expected ~{expected_slides})")
        
        # Validate content progression
        print_("Step 5B: Validating content progression...")
        if slide_topics_list and len(slide_topics_list) > 5:
            # Check for progressive complexity in topic titles
            basic_keywords = ["introduction", "overview", "basics", "fundamentals"]
            advanced_keywords = ["advanced", "complex", "sophisticated", "optimization", "analysis"]
            
            basic_count = sum(1 for topic in slide_topics_list[:len(slide_topics_list)//3] 
                            if any(keyword in topic.lower() for keyword in basic_keywords))
            advanced_count = sum(1 for topic in slide_topics_list[-len(slide_topics_list)//3:] 
                               if any(keyword in topic.lower() for keyword in advanced_keywords))
            
            if basic_count > 0 and advanced_count > 0:
                print_("✅ Content progression from basic to advanced concepts detected")
            else:
                print_("⚠️ Content progression may need review")
        
        # Return validation results
        return {
            "status": "completed",
            "message": "Educational structure validation completed",
            "slide_count_target": slide_count_target,
            "slide_topics_list": slide_topics_list if slide_topics_list else [],
            "credit_hour_alignment": "valid" if (slide_count_target >= expected_slides * 0.8 and slide_count_target <= expected_slides * 1.2) else "needs_review",
            "content_progression": "valid" if (slide_topics_list and len(slide_topics_list) > 5 and basic_count > 0 and advanced_count > 0) else "needs_review"
        }

    def execute_step_6(self, generation_context: Dict[str, Any], slide_topics_list: list) -> Any:
        """Execute Step 6: Presentation Object Creation"""
        print_("Step 6: Presentation Object Creation")
        
        # Import presentation classes
        from presentation_class import PresentationBuilder
        from slide_class import SlideData
        
        # Create the Presentation structure
        presentation = PresentationBuilder()
        
        # Create slides using the specific slide topics from Step 4.5
        for i, slide_topic in enumerate(slide_topics_list):
            # Create a new slide with the specific topic as title
            slide_title = slide_topic
            new_slide = SlideData(title=slide_title, content="", sources=[])
            
            # Add it to the actual presentation structure
            presentation.slides.append(new_slide)
        
        print_(f"Step 6: Created presentation with {len(presentation.slides)} slides")
        print_("Slide layout created and presentation initialized.")
        
        return presentation

    def execute_step_7(self, generation_context: Dict[str, Any], slide_topics_list: list, presentation: Any, lecture_notes: str = "") -> None:
        """Execute Step 7: Slide Content Generation (Enhanced with Lecture Notes)"""
        print_("Step 7: Slide Content Generation (Enhanced with Lecture Notes)")
        
        prompt = generation_context["prompt"]
        knowledge_db = generation_context["knowledge_db"]
        
        # Step 7 prompt template - enhanced with lecture notes
        structure_prompt_step_7 = (
            "You are creating ACTUAL SLIDE CONTENT for a PowerPoint presentation, NOT an outline or summary. "
            "You are currently on slide #1 with the specific topic: #2. "
            "Previous themes within this presentation are #3. "
            "Information from the research database that may be relevant is: ({#4}). "
            "Comprehensive lecture notes for reference: ({#5}). "
            "IMPORTANT: Generate the actual content that would appear ON THE SLIDE, not a description of what should be on the slide. "
            "Create slide content that is: "
            "- Concise bullet points (3-4 key points maximum) "
            "- Content that students would actually see on the slide "
            "- Focused on explaining the specific topic "
            "- Includes practical examples or applications "
            "- Academic but accessible for senior undergraduate students "
            "CRITICAL: Do NOT include ANY section headers, labels, or outline formatting. "
            "Do NOT include: "
            "- 'Key Concepts and Definitions:' "
            "- 'Real-World Examples and Applications:' "
            "- 'Visual Elements and Figures:' "
            "- 'Practical Insights and Takeaways:' "
            "- 'Learning Objectives:' "
            "- 'Lab Activities:' "
            "- Slide numbers or metadata "
            "- Long paragraphs "
            "- Ellipsis (...) "
            "- Outline-style formatting "
            "Respond with ONLY the actual slide content in bullet point format. "
            "Example of what to generate: "
            "• Large Language Models (LLMs) use transformer architecture with attention mechanisms "
            "• Pre-training on massive datasets enables understanding of language patterns "
            "• Fine-tuning adapts models for specific tasks like text generation "
            "• Applications include chatbots, content creation, and language translation"
        )
        
        all_previous_themes = []
        
        for i in range(len(presentation.slides)):
            # Small safety delay
            import time
            time.sleep(0.1)
            
            # Get the specific slide topic
            slide_topic = slide_topics_list[i]
            
            # Build search term from the slide topic
            search_term = slide_topic
            
            # Search knowledge database for relevant research
            section_research_results_raw = knowledge_db.search(search_term)
            
            section_research_results = ""
            for section_research_result_raw in section_research_results_raw:
                section_research_results += str(section_research_result_raw) + "\n\n"
            
            # Build the specific prompt for this slide
            specific_step_7_prompt = (
                f"Initial Prompt: ({prompt}) "
                f"Role Prompt: ({self.config.ai_role_prompt}) "
                f"Specific Instructions: ({structure_prompt_step_7})"
            )
            
            # Replace placeholders
            specific_step_7_prompt = specific_step_7_prompt.replace("#1", str(i + 1))
            specific_step_7_prompt = specific_step_7_prompt.replace("#2", slide_topic)
            specific_step_7_prompt = specific_step_7_prompt.replace("#3", str(all_previous_themes))
            specific_step_7_prompt = specific_step_7_prompt.replace("#4", section_research_results)
            specific_step_7_prompt = specific_step_7_prompt.replace("#5", lecture_notes[:1000] if lecture_notes else "No lecture notes available")
            
            print_(f"Generating content for slide {i + 1} (Topic: {slide_topic})")
            
            # Make API call to generate content
            raw_step_7_response = self.api_manager.make_call(specific_step_7_prompt)
            
            if not raw_step_7_response:
                print_(f"Error: AI gave no response for slide {i + 1}. Skipping.")
                continue
            
            # Clean the generated content immediately
            cleaned_content = self._clean_slide_content(raw_step_7_response.strip())
            
            # Update slide content with cleaned version
            presentation.slides[i].content = cleaned_content
            
            # Debug: Print what was actually set
            print_(f"🔍 DEBUG: Slide {i+1} content set to: '{cleaned_content[:100]}...'")
            print_(f"🔍 DEBUG: Slide {i+1} content length: {len(cleaned_content)}")
            
            # Add to previous themes for the entire presentation (keep only recent ones to avoid token limits)
            all_previous_themes.append(cleaned_content)
            # Keep only the last 5 themes to prevent context length issues
            if len(all_previous_themes) > 5:
                all_previous_themes = all_previous_themes[-5:]
            
            print_(f"✅ Slide {i + 1} content: {raw_step_7_response.strip()}")
        
        print_(f"Step 7: Generated content for {len(presentation.slides)} slides")
        print_("Slide content generation complete.")
        
        return presentation
    
    def execute_step_8(self, generation_context: Dict[str, Any], slide_topics_list: list, presentation: Any) -> Any:
        """Execute Step 8: Slide Title Generation"""
        print_("Step 8: Slide Title Generation")
        
        prompt = generation_context["prompt"]
        knowledge_db = generation_context["knowledge_db"]
        
        # Step 8A: Generate specific slide titles
        structure_prompt_step_8 = (
            "You have been given previous information. You are on slide #1 with the specific topic: #2. "
            "Previous slide titles in this presentation are: ({#3}). "
            "Database information for this section is: ({#4}). "
            "It was previously given the content theme of #5. "
            "You are to make a concise, specific, engaging title for this slide. "
            "Keep the title brief and focused - maximum 8-10 words. "
            "Do NOT include metadata or formatting. "
            "Respond with the clean title only."
        )
        
        all_slide_titles = []
        
        for i in range(len(presentation.slides)):
            # Small safety delay
            import time
            time.sleep(0.1)
            
            # Get the specific slide topic
            slide_topic = slide_topics_list[i]
            
            # Build search term from the slide topic
            search_term = slide_topic
            
            # Search knowledge database for relevant research
            section_research_results_raw = knowledge_db.search(search_term)
            
            section_research_results = ""
            for section_research_result_raw in section_research_results_raw:
                section_research_results += str(section_research_result_raw) + "\n\n"
            
            # Build the specific prompt for this slide
            specific_step_8_prompt = (
                f"Initial Prompt: ({prompt}) "
                f"Role Prompt: ({self.config.ai_role_prompt}) "
                f"Specific Instructions: ({structure_prompt_step_8})"
            )
            
            # Replace placeholders
            specific_step_8_prompt = specific_step_8_prompt.replace("#1", str(i + 1))
            specific_step_8_prompt = specific_step_8_prompt.replace("#2", slide_topic)
            if all_slide_titles == []:
                specific_step_8_prompt = specific_step_8_prompt.replace("#3", "(None.)")
            else:
                specific_step_8_prompt = specific_step_8_prompt.replace("#3", str(all_slide_titles))
            specific_step_8_prompt = specific_step_8_prompt.replace("#5", str(presentation.slides[i].content))
            specific_step_8_prompt = specific_step_8_prompt.replace("#4", section_research_results)
            
            print_(f"Generating title for slide {i + 1} (Topic: {slide_topic})")
            
            # Make API call to generate title
            raw_step_8_response = self.api_manager.make_call(specific_step_8_prompt)
            
            if not raw_step_8_response:
                print_(f"Error: AI gave no response for slide {i + 1}. Skipping.")
                continue
            
            # Update slide title
            presentation.slides[i].title = raw_step_8_response.strip()
            
            # Add to all slide titles
            all_slide_titles.append(raw_step_8_response.strip())
            
            print_(f"✅ Slide {i + 1} title: {raw_step_8_response.strip()}")
        
        # Step 8B: Generate overall presentation title
        print_("Generating overall presentation title...")
        
        structure_prompt_step_8_2 = (
            "You are making a presentation with the previous ideas as context. "
            "These are all of the slide titles for the presentation: ({#1}). "
            "Based upon this, generate a title for the presentation overall. "
            "Respond with that title and nothing else."
        )
        
        specific_step_8_prompt_2 = (
            f"Initial Prompt: ({prompt}) "
            f"Role Prompt: ({self.config.ai_role_prompt}) "
            f"Specific Instructions: ({structure_prompt_step_8_2})"
        )
        
        specific_step_8_prompt_2 = specific_step_8_prompt_2.replace("#1", str(all_slide_titles))
        
        raw_step_8_response_2 = self.api_manager.make_call(specific_step_8_prompt_2)
        
        if not raw_step_8_response_2:
            print_("Error: Failure to generate presentation title.")
            return presentation
        
        presentation.title = str(raw_step_8_response_2.strip(" \"\'"))
        print_(f"✅ Overall presentation title: {presentation.title}")
        
        print_(f"Step 8: Generated titles for {len(presentation.slides)} slides and overall presentation")
        print_("Slide title generation complete.")
        
        return presentation
    
    def execute_step_9(self, generation_context: Dict[str, Any], slide_topics_list: list, teaching_outline: str, presentation: Any) -> Any:
        """Execute Step 9: Source Association and Content Enhancement"""
        print_("Step 9: Source Association and Content Enhancement")
        
        prompt = generation_context["prompt"]
        knowledge_db = generation_context["knowledge_db"]
        slide_count_target = generation_context["slide_count_target"]
        
        # Step 9A: Determine sources per slide
        print_("Step 9A: Determining source allocation...")
        
        # Calculate sources per slide based on database size and slide count
        uses_per_source_average = 1
        unused_sources_percent = 0.05
        sources_used_per_slide = max(1, int(len(knowledge_db.entries) / slide_count_target * uses_per_source_average * (1 - unused_sources_percent)))
        
        print_(f"Sources per slide: {sources_used_per_slide}")
        
        # Get all available keywords from database
        full_keywords_list = knowledge_db.get_all_keywords()
        
        # Track source associations to avoid duplicates
        sources_associations = {}
        
        # Step 9A: Associate sources with slides
        print_("Step 9A: Associating sources with slides...")
        
        structure_prompt_step_9a = (
            "Given the previous information and slide details, you will generate search keywords to find relevant sources. "
            "You are on slide #1 with title: #2 and content theme: #3. "
            "The slide topic from the teaching outline is: #4. "
            "The full list of available keywords in the database is: #5. "
            "Generate a list of search keywords that will find the most relevant sources for this slide. "
            "Make keywords specific but broad enough to find multiple relevant sources. "
            "Respond with a Python list of strings containing the search keywords."
        )
        
        for i in range(len(presentation.slides)):
            # Small safety delay
            import time
            time.sleep(0.1)
            
            # Get slide details
            slide_title = presentation.slides[i].title
            slide_content = presentation.slides[i].content
            slide_topic = slide_topics_list[i]
            
            # Build the specific prompt for this slide
            specific_step_9a_prompt = (
                f"Initial Prompt: ({prompt}) "
                f"Role Prompt: ({self.config.ai_role_prompt}) "
                f"Specific Instructions: ({structure_prompt_step_9a})"
            )
            
            # Replace placeholders
            specific_step_9a_prompt = specific_step_9a_prompt.replace("#1", str(i + 1))
            specific_step_9a_prompt = specific_step_9a_prompt.replace("#2", slide_title)
            specific_step_9a_prompt = specific_step_9a_prompt.replace("#3", slide_content)
            specific_step_9a_prompt = specific_step_9a_prompt.replace("#4", slide_topic)
            specific_step_9a_prompt = specific_step_9a_prompt.replace("#5", str(full_keywords_list))
            
            print_(f"Generating search keywords for slide {i + 1} (Topic: {slide_topic})")
            
            # Make API call to generate search keywords
            raw_step_9a_response = self.api_manager.make_call(specific_step_9a_prompt)
            
            if not raw_step_9a_response:
                print_(f"Error: AI gave no response for slide {i + 1}. Skipping.")
                continue
            
            # Parse the response as a Python list
            try:
                search_keywords = ast.literal_eval(raw_step_9a_response.strip())
            except (ValueError, SyntaxError) as e:
                print_(f"Error parsing search keywords for slide {i + 1}: {e}. Skipping.")
                continue
            
            if not isinstance(search_keywords, list):
                print_(f"Error: Non-list response for slide {i + 1}. Skipping.")
                continue
            
            # Combine keywords into search term
            search_term = " ".join(search_keywords)
            
            # Search knowledge database
            search_results = knowledge_db.search(search_term)
            search_results = search_results[:sources_used_per_slide]
            
            # Associate sources with slide
            for entry in search_results:
                # Increment use count
                entry.add_use()
                
                # Create or reuse source object
                if str(entry.id) in sources_associations:
                    source_obj = sources_associations[str(entry.id)]
                else:
                    from source_class import Source
                    source_obj = Source(entry.title, entry.link, entry)
                    sources_associations[str(entry.id)] = source_obj
                
                # Add source to slide
                presentation.slides[i].sources.append(source_obj)
            
            print_(f"✅ Slide {i + 1}: Associated {len(search_results)} sources")
        
        # Step 9B: Enhance slide content using associated sources
        print_("Step 9B: Enhancing slide content with sources...")
        
        structure_prompt_step_9b = (
            "You are enhancing existing slide content with research sources, NOT replacing it. "
            "Slide #1: {#2} "
            "Slide Title: {#3} "
            "EXISTING Content: {#4} "
            "Teaching Outline Context: {#5} "
            "Associated Research: ({#6}) "
            "Previous Slide Content: ({#7}) "
            "ENHANCE the existing content by: "
            "- Adding specific details from the research sources "
            "- Keeping the existing bullet point format "
            "- Maintaining the concise, presentation-friendly style "
            "- Adding 1-2 additional bullet points if relevant "
            "- Preserving the original content structure "
            "CRITICAL RULES: "
            "- Do NOT repeat any bullet points from the previous slide content "
            "- Do NOT add more than 2 new bullet points "
            "- Keep total bullet points to 4-6 maximum "
            "- Focus on NEW information specific to this slide's topic "
            "- If the existing content is already comprehensive, only add 1 new point "
            "IMPORTANT: Do NOT replace the content - only enhance it. "
            "CRITICAL OUTPUT FORMAT: "
            "- Return ONLY the bullet point content "
            "- Do NOT include any labels like 'Enhanced Content:', 'Content:', 'Slide Content:', etc. "
            "- Do NOT include any metadata, headers, or formatting instructions "
            "- Do NOT include any explanatory text "
            "- Start directly with the first bullet point "
            "- End with the last bullet point "
            "Respond with ONLY the enhanced bullet point content, nothing else."
        )
        
        for i in range(len(presentation.slides)):
            # Small safety delay
            time.sleep(0.1)
            
            # Get slide details
            slide_title = presentation.slides[i].title
            slide_content = presentation.slides[i].content
            slide_topic = slide_topics_list[i]
            
            # Get previous slide content for flow
            if i == 0:
                previous_content = "(None.)"
            else:
                previous_content = presentation.slides[i - 1].content
            
            # Get associated research text
            research_text = ""
            for source in presentation.slides[i].sources:
                research_text += " " + source.linked_entry.text
            
            research_text = research_text.strip()
            if not research_text:
                research_text = "(None.)"
            
            # Build the specific prompt for content enhancement
            specific_step_9b_prompt = (
                f"Initial Prompt: ({prompt}) "
                f"Role Prompt: ({self.config.ai_role_prompt}) "
                f"Specific Instructions: ({structure_prompt_step_9b})"
            )
            
            # Replace placeholders
            specific_step_9b_prompt = specific_step_9b_prompt.replace("#1", str(i + 1))
            specific_step_9b_prompt = specific_step_9b_prompt.replace("#2", slide_topic)
            specific_step_9b_prompt = specific_step_9b_prompt.replace("#3", slide_title)
            specific_step_9b_prompt = specific_step_9b_prompt.replace("#4", slide_content)
            specific_step_9b_prompt = specific_step_9b_prompt.replace("#5", teaching_outline)
            specific_step_9b_prompt = specific_step_9b_prompt.replace("#6", research_text)
            specific_step_9b_prompt = specific_step_9b_prompt.replace("#7", previous_content)
            
            print_(f"Enhancing content for slide {i + 1} (Topic: {slide_topic})")
            
            # Make API call to enhance content
            raw_step_9b_response = self.api_manager.make_call(specific_step_9b_prompt)
            
            if not raw_step_9b_response:
                print_(f"Error: AI gave no response for slide {i + 1} content enhancement. Skipping.")
                continue
            
            # Update slide content with length check
            enhanced_content = raw_step_9b_response.strip()
            
            # Check if content is getting too long (more than ~500 characters)
            if len(enhanced_content) > 500:
                print_(f"⚠️ Warning: Slide {i + 1} content is long ({len(enhanced_content)} chars) - consider reducing")
            
            presentation.slides[i].content = enhanced_content
            
            print_(f"✅ Slide {i + 1}: Enhanced content with {len(presentation.slides[i].sources)} sources")
        
        # Step 9C: Add source information to slide content after enhancement
        print_("Step 9C: Adding source information to slide content...")
        
        for i in range(len(presentation.slides)):
            if presentation.slides[i].sources:
                # Add source footer to content
                source_ids = [f"[{src.id}]" for src in presentation.slides[i].sources]
                source_footer = "\n\nSources: " + ", ".join(source_ids)
                
                # Add to enhanced content
                current_content = presentation.slides[i].content
                presentation.slides[i].content = current_content + source_footer
                
                print_(f"✅ Slide {i + 1}: Added source footer with {len(presentation.slides[i].sources)} sources")
        
        print_(f"Step 9: Associated sources and enhanced content for {len(presentation.slides)} slides")
        print_("Source association and content enhancement complete.")
        
        return presentation
    
    def execute_step_10(self, presentation: Any) -> Any:
        """Execute Step 10: Presentation Finalization"""
        print_("Step 10: Presentation Finalization")
        
        # Step 10A: Skip content cleaning - let presentation class handle text processing
        print_("Step 10A: Skipping content cleaning (presentation class handles text processing)")
        
        # Step 10B: Add title slide at the beginning
        print_("Step 10B: Adding title slide...")
        presentation.add_title_slide()
        print_("✅ Title slide added")
        
        # Step 10C: Add source slides at the end
        print_("Step 10C: Adding source slides...")
        presentation.add_sources_slides()
        print_("✅ Source slides added")
        
        print_(f"Step 10: Finalized presentation with {len(presentation.slides)} total slides")
        print_("Presentation finalization complete.")
        
        return presentation

    def execute_step_11(self, presentation: Any) -> str:
        """Execute Step 11: Save Presentation to File"""
        print_("Step 11: Save Presentation to File")
        
        # Get the results path from path manager
        results_path = self.path_manager.results_path
        print_(f"Saving to file: {results_path}")
        
        # Get the presentation title and clean it for filename
        save_title = presentation.title
        
        # Remove disallowed characters for filename
        disallowed_chars = ['<', '>', ':', '"', '/', '\\', '|', '?', '*']
        for disallowed_char in disallowed_chars:
            save_title = save_title.replace(disallowed_char, "")
        
        # Replace spaces with underscores
        save_title = save_title.replace(" ", "_")
        
        # Add timestamp to make filename unique
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        save_title += "_" + timestamp
        
        print_(f"Save title used: {save_title}")
        
        # Save the presentation to file
        try:
            presentation.save_to_file(results_path, save_title)
            print_("✅ Saved to file successfully")
            
            # Return the full path to the saved file
            saved_file_path = results_path / f"{save_title}.pptx"
            print_(f"📁 File saved at: {saved_file_path}")
            
            print_("Step 11: Presentation saved successfully")
            print_("🎉 Presentation generation complete!")
            
            return str(saved_file_path)
            
        except Exception as e:
            print_(f"❌ Error saving presentation: {e}")
            raise e
    
    def get_system_state(self) -> Dict[str, Any]:
        """Get the current state of the system for debugging or monitoring."""
        return {
            "is_initialized": self.is_initialized,
            "run_name": self.run_name,
            "api_calls_remaining": self.api_manager.calls_remaining if self.api_manager else None,
            "database_size": len(self.database_manager.database.entries) if self.database_manager else None,
            "config": {
                "max_api_calls": self.config.max_api_calls,
                "slide_count_target": self.config.slide_count_target,
                "input_mode": self.config.input_mode
            }
        }
    
    def _transform_response_to_list(self, response: str, expected_length: int, list_type: str = "strings") -> list:
        """
        Transform a malformed AI response into a proper Python list using an additional API call.
        
        Args:
            response: The malformed response from the AI
            expected_length: The expected length of the list
            list_type: Type of list - "strings" or "integers"
            
        Returns:
            A properly formatted Python list
        """
        print_(f"Making additional API call to transform response to proper {list_type} list format...")
        
        if list_type == "integers":
            transform_prompt = f"""The following response needs to be converted into a proper Python list of integers.

Original response:
{response}

Expected list length: {expected_length}

Please convert this into a valid Python list of integers. The response should be a single line containing only the Python list, with no additional text, numbering, or formatting.

Example format:
[3, 4, 3, 4, 3, ...]

Respond with ONLY the Python list, nothing else."""
        else:
            transform_prompt = f"""The following response needs to be converted into a proper Python list of strings.

Original response:
{response}

Expected list length: {expected_length}

Please convert this into a valid Python list of strings. The response should be a single line containing only the Python list, with no additional text, numbering, or formatting.

Example format:
["Item 1", "Item 2", "Item 3", ...]

Respond with ONLY the Python list, nothing else."""
        
        transformed_response = self.api_manager.make_call(transform_prompt)
        
        if not transformed_response:
            raise RuntimeError("Failed to transform response to proper format")
        
        # Try to parse the transformed response
        try:
            # Find the list in the response
            start_idx = transformed_response.find('[')
            end_idx = transformed_response.rfind(']') + 1
            
            if start_idx == -1 or end_idx == 0:
                raise ValueError("No list found in transformed response")
            
            list_str = transformed_response[start_idx:end_idx]
            result_list = ast.literal_eval(list_str.strip())
            
            if not isinstance(result_list, list):
                raise ValueError("Transformed response is not a list")
            
            # Convert to proper types if needed
            if list_type == "integers":
                try:
                    result_list = [int(item) for item in result_list]
                except (ValueError, TypeError):
                    print_("Warning: Could not convert all items to integers. Using fallback.")
                    return self._extract_items_manually(response, expected_length, list_type)
            
            # Fix the length if needed
            if len(result_list) != expected_length:
                result_list = self._fix_list_length(result_list, expected_length, list_type)
            
            return result_list
            
        except Exception as e:
            print_(f"Error parsing transformed response: {e}")
            # Fallback: try to extract items manually
            return self._extract_items_manually(response, expected_length, list_type)
    
    def _fix_list_length(self, items_list: list, target_length: int, list_type: str = "strings", context: str = "") -> list:
        """
        Fix the length of a list by either truncating or extending it.
        For string lists (slide topics), will make an API call to generate more items.
        
        Args:
            items_list: The list to fix
            target_length: The desired length
            list_type: Type of list - "strings" or "integers"
            context: Additional context for generating more items (e.g., teaching outline)
            
        Returns:
            A list with the correct length
        """
        if len(items_list) == target_length:
            return items_list
        
        if len(items_list) > target_length:
            # Truncate the list
            print_(f"Truncating list from {len(items_list)} to {target_length} items")
            return items_list[:target_length]
        else:
            # For string lists, try to generate more items via API
            if list_type == "strings" and context:
                print_(f"List too short ({len(items_list)} items, need {target_length}). Generating more items via API...")
                return self._generate_more_items(items_list, target_length, context)
            else:
                # Fallback: extend the list by duplicating the last item
                print_(f"Extending list from {len(items_list)} to {target_length} items")
                result = items_list.copy()
                while len(result) < target_length:
                    if len(items_list) > 0:
                        result.append(f"{items_list[-1]} (continued)")
                    else:
                        result.append("Additional slide topic")
                return result
    
    def _extract_items_manually(self, response: str, expected_length: int, list_type: str = "strings") -> list:
        """
        Manually extract items from a response when automatic parsing fails.
        
        Args:
            response: The response to extract items from
            expected_length: The expected number of items
            list_type: Type of list - "strings" or "integers"
            
        Returns:
            A list of extracted items
        """
        print_("Manually extracting items from response...")
        
        if list_type == "integers":
            # For integers, try to extract numbers
            import re
            numbers = re.findall(r'\d+', response)
            items = [int(num) for num in numbers if num.isdigit()]
            
            # If we don't have enough numbers, fill with default values
            while len(items) < expected_length:
                items.append(3)  # Default to 3 slides per topic
            
            # Ensure all items are integers
            items = [int(item) for item in items]
            
            return self._fix_list_length(items, expected_length, list_type)
        else:
            # Split by lines and extract numbered items
            lines = response.strip().split('\n')
            items = []
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                # Remove numbering patterns like "1.", "2.", etc.
                import re
                line = re.sub(r'^\d+\.\s*', '', line)
                
                # Remove other common prefixes
                line = re.sub(r'^[-*]\s*', '', line)
                
                if line:
                    items.append(line)
            
            # Fix the length
            return self._fix_list_length(items, expected_length, list_type)
    
    def _clean_slide_content(self, content: str) -> str:
        """
        Clean up slide content by removing artifacts, metadata, and formatting issues.
        
        Args:
            content: The raw slide content to clean
            
        Returns:
            Cleaned and properly formatted content
        """
        if not content:
            return content
        
        # Remove common artifacts and metadata
        import re
        
        # Remove metadata patterns like "slide content:", "slide amount:", etc.
        content = re.sub(r'slide\s+content\s*:', '', content, flags=re.IGNORECASE)
        content = re.sub(r'slide\s+amount\s*:', '', content, flags=re.IGNORECASE)
        content = re.sub(r'slide\s+title\s*:', '', content, flags=re.IGNORECASE)
        content = re.sub(r'slide\s+number\s*:', '', content, flags=re.IGNORECASE)
        content = re.sub(r'topic\s*:', '', content, flags=re.IGNORECASE)
        content = re.sub(r'content\s*:', '', content, flags=re.IGNORECASE)
        content = re.sub(r'title\s*:', '', content, flags=re.IGNORECASE)
        
        # Remove slide numbers at the beginning (e.g., "Slide 1:", "1.", etc.)
        content = re.sub(r'^slide\s+\d+\s*:', '', content, flags=re.IGNORECASE | re.MULTILINE)
        content = re.sub(r'^\d+\.\s*', '', content, flags=re.MULTILINE)
        
        # Remove ellipsis at the end
        content = re.sub(r'\.{3,}$', '', content, flags=re.MULTILINE)
        content = re.sub(r'\.{2,}\s*$', '', content)
        
        # Remove numbered lists that are artifacts (like "1.", "2.", etc.)
        content = re.sub(r'^\d+\.\s*', '', content, flags=re.MULTILINE)
        
        # Remove bullet points that are artifacts
        content = re.sub(r'^[-*]\s*', '', content, flags=re.MULTILINE)
        
        # Remove excessive whitespace and normalize line breaks
        content = re.sub(r'\n\s*\n\s*\n+', '\n\n', content)  # Multiple blank lines to double
        content = re.sub(r' +', ' ', content)  # Multiple spaces to single
        
        # Remove leading/trailing whitespace from each line
        lines = content.split('\n')
        cleaned_lines = []
        for line in lines:
            line = line.strip()
            if line:  # Only add non-empty lines
                cleaned_lines.append(line)
        
        # Rejoin with proper spacing
        content = '\n'.join(cleaned_lines)
        
        # Remove any remaining artifacts like "Response:", "Answer:", etc.
        content = re.sub(r'^(Response|Answer|Output|Result)\s*:', '', content, flags=re.IGNORECASE)
        
        # Remove section headers that are common in verbose content
        content = re.sub(r'-?\s*Key\s+Concepts\s+and\s+Definitions\s*:', '', content, flags=re.IGNORECASE)
        content = re.sub(r'-?\s*Real-World\s+Examples\s+and\s+Applications\s*:', '', content, flags=re.IGNORECASE)
        content = re.sub(r'-?\s*Visual\s+Elements\s+and\s+Figures\s*:', '', content, flags=re.IGNORECASE)
        content = re.sub(r'-?\s*Practical\s+Insights\s+and\s+Takeaways\s*:', '', content, flags=re.IGNORECASE)
        content = re.sub(r'-?\s*Learning\s+Objectives\s*:', '', content, flags=re.IGNORECASE)
        content = re.sub(r'-?\s*Lab\s+Activities\s*:', '', content, flags=re.IGNORECASE)
        
        # Remove any remaining metadata patterns
        content = re.sub(r'\[.*?\]', '', content)  # Remove bracketed metadata
        content = re.sub(r'\{.*?\}', '', content)  # Remove curly brace metadata
        
        # Final cleanup of excessive whitespace
        content = re.sub(r'\s+', ' ', content).strip()
        
        # Limit content length to reasonable size for slides (max ~500 characters)
        if len(content) > 500:
            # Try to truncate at a sentence boundary
            sentences = re.split(r'[.!?]', content)
            truncated_content = ""
            for sentence in sentences:
                if len(truncated_content + sentence) < 450:  # Leave some room for "..."
                    truncated_content += sentence + "."
                else:
                    break
            if truncated_content:
                content = truncated_content + ".."
            else:
                # If no good sentence boundary, just truncate
                content = content[:450] + "..."
        
        return content
    
    def _generate_more_items(self, existing_items: list, target_length: int, context: str) -> list:
        """
        Generate additional items to reach the target length using an API call.
        
        Args:
            existing_items: The current list of items
            target_length: The desired total length
            context: Additional context (e.g., teaching outline)
            
        Returns:
            A list with the target length
        """
        print_(f"Generating {target_length - len(existing_items)} more items via API...")
        
        # Create a prompt to generate more items
        generate_prompt = f"""You need to generate {target_length - len(existing_items)} more slide topics to complete a presentation.

Current slide topics:
{chr(10).join(f"{i+1}. {item}" for i, item in enumerate(existing_items))}

Teaching outline context:
{context}

Please generate {target_length - len(existing_items)} additional slide topics that:
1. Are specific and actionable for teaching
2. Follow the same style and detail level as the existing topics
3. Cover different aspects of the subject matter
4. Are numbered starting from {len(existing_items) + 1}

Respond with ONLY the additional topics, one per line, starting with the number and a period (e.g., "51. Topic Title").
Do not include any other text or formatting."""
        
        additional_response = self.api_manager.make_call(generate_prompt)
        
        if not additional_response:
            print_("Failed to generate additional items via API. Falling back to duplication.")
            return self._fallback_extend_list(existing_items, target_length)
        
        # Parse the additional items
        try:
            additional_items = []
            lines = additional_response.strip().split('\n')
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                # Remove numbering patterns like "51.", "52.", etc.
                import re
                line = re.sub(r'^\d+\.\s*', '', line)
                
                if line:
                    additional_items.append(line)
            
            # Combine existing and new items
            result = existing_items + additional_items
            
            # If we still don't have enough, fall back to duplication
            if len(result) < target_length:
                print_(f"Generated {len(additional_items)} items, but need {target_length - len(existing_items)}. Falling back to duplication.")
                return self._fallback_extend_list(result, target_length)
            
            # If we have too many, truncate
            if len(result) > target_length:
                print_(f"Generated {len(additional_items)} items, but only need {target_length - len(existing_items)}. Truncating.")
                return result[:target_length]
            
            return result
            
        except Exception as e:
            print_(f"Error parsing additional items: {e}. Falling back to duplication.")
            return self._fallback_extend_list(existing_items, target_length)
    
    def _fallback_extend_list(self, items_list: list, target_length: int) -> list:
        """
        Fallback method to extend a list by generating new items instead of duplicating.
        
        Args:
            items_list: The list to extend
            target_length: The desired length
            
        Returns:
            An extended list
        """
        print_(f"Fallback: Extending list from {len(items_list)} to {target_length} items")
        result = items_list.copy()
        while len(result) < target_length:
            if len(items_list) > 0:
                # Generate a new related topic instead of duplicating
                base_topic = items_list[-1]
                # Create a variation of the last topic
                if "introduction" in base_topic.lower():
                    result.append(f"Advanced {base_topic.replace('Introduction', '').strip()}")
                elif "basics" in base_topic.lower():
                    result.append(f"Advanced {base_topic.replace('Basics', '').strip()}")
                elif "overview" in base_topic.lower():
                    result.append(f"Detailed {base_topic.replace('Overview', '').strip()}")
                else:
                    result.append(f"Advanced Applications of {base_topic}")
            else:
                result.append("Additional slide topic")
        return result


def main():
    """Main entry point for testing the automation core."""
    try:
        # Create and initialize the automation core
        core = AutomationCore()
        
        if core.initialize():
            print_("Automation core initialized successfully!")
            
            # Get system state
            state = core.get_system_state()
            print_(f"System state: {state}")
            
            # Test prompt retrieval
            try:
                prompt = core.get_initial_prompt()
                print_(f"Retrieved prompt: {prompt[:100]}...")
            except Exception as e:
                print_(f"Error getting prompt: {e}")
            
            # Test preparation for presentation generation
            try:
                print_("\n" + "="*60)
                print_("🧪 Testing Complete Setup Flow (Up to Step 1)")
                print_("="*60)
                
                # Prepare for generation
                generation_context = core.prepare_for_presentation_generation()
                
                # Create Step 1 prompt
                step_1_prompt = core.create_step_1_prompt(generation_context)
                print_(f"\n📝 Step 1 Prompt Preview (first 200 chars):")
                print_(f"{step_1_prompt[:200]}...")
                
                print_("\n✅ Complete setup flow successful! Ready for Step 1 execution.")
                
                # Test Step 1 execution (optional - uncomment to test)
                # print_("\n" + "="*60)
                # print_("🧪 Testing Step 1 Execution")
                # print_("="*60)
                # topics = core.execute_step_1(generation_context)
                # print_(f"Step 1 completed with {len(topics)} topics: {topics}")
                
                # Test Step 2 execution (optional - uncomment to test)
                # print_("\n" + "="*60)
                # print_("🧪 Testing Step 2 Execution")
                # print_("="*60)
                # core.execute_step_2(generation_context, topics)
                # print_(f"Step 2 completed. Database now has {len(generation_context['knowledge_db'].entries)} entries.")
                
            except Exception as e:
                print_(f"Error in preparation flow: {e}")
        
        else:
            print_("Failed to initialize automation core")
            return 1
            
    except Exception as e:
        print_(f"Unexpected error: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
