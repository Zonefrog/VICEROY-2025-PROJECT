"""
automation_core_patched.py

Drop-in patch module to normalize return types and signatures so the
run_* scripts and tests agree. It does **not** replace your original
AutomationCore file; it overrides a few methods and keeps everything
else intact.

Usage options:

Option A: Replace the class at import time
------------------------------------------
from automation_core import AutomationCore as _OrigAutomationCore
from automation_core_patched import make_patched_core_class
AutomationCore = make_patched_core_class(_OrigAutomationCore)

Option B: Monkey-patch an existing instance
-------------------------------------------
from automation_core_patched import patch_core_instance
core = AutomationCore(...)
patch_core_instance(core)

Either way only Steps 1–5 are overridden; other steps remain unchanged.
"""

from __future__ import annotations

import ast
from typing import Any, Dict, Optional, List


# -------- Result wrappers (behave like both a dict and a list) --------

class _TopicsResult(dict):
    """
    Acts like: {'initial_topics': [...]} AND like a list for len()/iteration.
    """
    def __init__(self, topics: List[str]):
        super().__init__({"initial_topics": topics})
        self._topics = topics

    def __len__(self):  # so len(result) prints the topic count in run_simple_pipeline.py
        return len(self._topics)

    def __iter__(self):
        return iter(self._topics)


class _AdditionalTopicsResult(dict):
    """
    Acts like: {'additional_topics': [...]} AND like a list for len()/iteration.
    """
    def __init__(self, topics: List[str]):
        super().__init__({"additional_topics": topics})
        self._topics = topics

    def __len__(self):
        return len(self._topics)

    def __iter__(self):
        return iter(self._topics)


# --------- Patch helpers ---------

def _patch_execute_step_1(cls):
    def execute_step_1(self, generation_context: Dict[str, Any]) -> _TopicsResult:
        if not getattr(self, "is_initialized", True):
            raise RuntimeError("System must be initialized before executing Step 1")

        print_("Step 1 begun.")

        step_1_prompt = self.create_step_1_prompt(generation_context)
        raw_step_1_response = self.api_manager.make_call(step_1_prompt)
        print_("Raw AI topic response: " + str(raw_step_1_response))

        if raw_step_1_response is None:
            raise RuntimeError("No AI response given for Step 1")

        split_topics = [t.strip(" \t\n.,[]{}()0123456789") for t in raw_step_1_response.split(",")]
        initial_topic_count = generation_context["initial_topic_count"]

        if len(split_topics) < initial_topic_count:
            raise RuntimeError(
                f"{len(split_topics)} topics provided. {initial_topic_count} expected. Got: {split_topics}"
            )
        if len(split_topics) > initial_topic_count:
            split_topics = split_topics[:initial_topic_count]

        print_("Selected topics: " + str(split_topics))
        print_("Step 1 Complete.")

        return _TopicsResult(split_topics)
    cls.execute_step_1 = execute_step_1


def _patch_execute_step_2(cls):
    def execute_step_2(self, generation_context: Dict[str, Any], topics: List[str]) -> Dict[str, Any]:
        if not getattr(self, "is_initialized", True):
            raise RuntimeError("System must be initialized before executing Step 2")

        print_("Step 2 begun.")

        prompt = generation_context["prompt"]
        database_entries_per_topic = generation_context["database_entries_per_topic"]
        knowledge_db = generation_context["knowledge_db"]

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

        added_entries = []
        existing_entry_titles = []

        for topic in topics:
            print_(f"Researching topic: {topic}")
            for i in range(database_entries_per_topic):
                import time; time.sleep(0.05)

                specific_research_prompt = (
                    f"Initial Prompt: ({prompt}) "
                    f"AI Role: ({RESEARCH_PROMPT}) "
                    f"Specific Instructions: ({STRUCTURE_PROMPT_STEP_2})"
                )
                specific_research_prompt = specific_research_prompt.replace("#1", str(existing_entry_titles or "(None)"))
                specific_research_prompt = specific_research_prompt.replace("#3", str(i + 1))
                specific_research_prompt = specific_research_prompt.replace("#2", topic.upper())

                print_("Prompt:\n" + specific_research_prompt + "\nTo be sent to the AI.")
                raw_step_2_response = self.api_manager.make_call(specific_research_prompt)
                print_("Raw AI response to this: " + str(raw_step_2_response))

                if raw_step_2_response is None:
                    print_("Error: During research, AI failed to respond.")
                    continue

                try:
                    step_2_dictionary = ast.literal_eval(raw_step_2_response)
                except Exception:
                    print_("Error: Incorrect format during step 2 research.")
                    continue

                if type(step_2_dictionary) != dict:
                    print_("Error: Response not a dictionary.")
                    continue

                needed_keys = ["title", "keywords", "text", "link"]
                needed_types = [str, list, str, str]
                for k, t in zip(needed_keys, needed_types):
                    if k not in step_2_dictionary or type(step_2_dictionary[k]) is not t:
                        print_(f"Error: {k} missing or wrong type in step 2 research dictionary.")
                        break
                else:
                    if knowledge_db.add_entry(
                        step_2_dictionary["title"],
                        step_2_dictionary["keywords"],
                        step_2_dictionary["text"],
                        step_2_dictionary["link"]
                    ):
                        existing_entry_titles.append(step_2_dictionary["title"])
                        added_entries.append(step_2_dictionary)
                        print_("Added Entry to database. Displaying.")
                        print_(str(knowledge_db.entries[-1]))
                    else:
                        print_("Error: Knowledge Database out of space.")

        print_("Step 2 Complete.")
        return {"research_entries": added_entries}
    cls.execute_step_2 = execute_step_2


def _patch_execute_step_3(cls):
    def execute_step_3(self, generation_context: Dict[str, Any], topics_step_1: List[str], step_2_result: Optional[Dict[str, Any]] = None) -> _AdditionalTopicsResult:
        if not getattr(self, "is_initialized", True):
            raise RuntimeError("System must be initialized before executing Step 3")

        print_("Step 3 begun.")
        step_3_prompt = self.create_step_3_prompt(generation_context, topics_step_1)
        print_("Following Prompt sent to AI:\n" + step_3_prompt + "\n.")
        raw_step_3_response = self.api_manager.make_call(step_3_prompt)

        print_("Raw AI topic response: " + str(raw_step_3_response))
        if raw_step_3_response is None:
            raise RuntimeError("No AI response given for Step 3")

        split_topics_2 = [t.strip(" \t\n.,[]{}()0123456789") for t in raw_step_3_response.split(",")]

        expected_count = generation_context["second_research_round_topic_count"]
        if len(split_topics_2) < expected_count:
            raise RuntimeError(
                f"{len(split_topics_2)} topics provided. {expected_count} expected. Got: {split_topics_2}"
            )
        if len(split_topics_2) > expected_count:
            split_topics_2 = split_topics_2[:expected_count]

        print_("Selected topics: " + str(split_topics_2))
        print_("Step 3 Complete.")
        return _AdditionalTopicsResult(split_topics_2)
    cls.execute_step_3 = execute_step_3


def _patch_execute_step_4(cls):
    def execute_step_4(self, generation_context: Dict[str, Any], topics_step_3: List[str]) -> Dict[str, Any]:
        if not getattr(self, "is_initialized", True):
            raise RuntimeError("System must be initialized before executing Step 4")

        print_("Step 4 begun.")

        prompt = generation_context["prompt"]
        database_entries_per_topic = generation_context["database_entries_per_topic"]
        knowledge_db = generation_context["knowledge_db"]

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

        added_entries = []
        existing_entry_titles = [entry.title for entry in knowledge_db.entries]

        for topic in topics_step_3:
            print_(f"Researching topic: {topic}")
            for i in range(database_entries_per_topic):
                import time; time.sleep(0.05)

                specific_research_prompt = (
                    f"Initial Prompt: ({prompt}) "
                    f"AI Role: ({RESEARCH_PROMPT_2}) "
                    f"Specific Instructions: ({STRUCTURE_PROMPT_STEP_4})"
                )
                specific_research_prompt = specific_research_prompt.replace("#1", str(existing_entry_titles or "(None)"))
                specific_research_prompt = specific_research_prompt.replace("#3", str(i + 1))
                specific_research_prompt = specific_research_prompt.replace("#2", topic.upper())

                print_("Prompt:\n" + specific_research_prompt + "\nTo be sent to the AI.")
                raw_step_4_response = self.api_manager.make_call(specific_research_prompt)
                print_("Raw AI response to this: " + str(raw_step_4_response))

                if raw_step_4_response is None:
                    print_("Error: During research, AI failed to respond.")
                    continue

                try:
                    step_4_dictionary = ast.literal_eval(raw_step_4_response)
                except Exception:
                    print_("Error: Incorrect format during step 4 research.")
                    continue

                if type(step_4_dictionary) != dict:
                    print_("Error: Response not a dictionary.")
                    continue

                needed_keys = ["title", "keywords", "text", "link"]
                needed_types = [str, list, str, str]
                for k, t in zip(needed_keys, needed_types):
                    if k not in step_4_dictionary or type(step_4_dictionary[k]) is not t:
                        print_(f"Error: {k} missing or wrong type in step 4 research dictionary.")
                        break
                else:
                    if knowledge_db.add_entry(
                        step_4_dictionary["title"],
                        step_4_dictionary["keywords"],
                        step_4_dictionary["text"],
                        step_4_dictionary["link"]
                    ):
                        existing_entry_titles.append(step_4_dictionary["title"])
                        added_entries.append(step_4_dictionary)
                        print_("Added Entry to database. Displaying.")
                        print_(str(knowledge_db.entries[-1]))
                    else:
                        print_("Error: Knowledge Database out of space.")

        print_("Step 4 Complete.")
        return {"research_entries": added_entries}
    cls.execute_step_4 = execute_step_4


def _patch_execute_step_4_5(cls):
    def execute_step_4_5(self, generation_context: Dict[str, Any], *legacy_args) -> Dict[str, Any]:
        # Keep existing body if any; this is a compatibility-only shim.
        # If the original method exists, call it with just (generation_context).
        orig = getattr(super(cls, self), "execute_step_4_5", None)
        if callable(orig):
            return orig(generation_context)
        # Otherwise, do nothing but return a benign payload.
        return {"status": "ok"}
    cls.execute_step_4_5 = execute_step_4_5


def _patch_execute_step_5(cls):
    def execute_step_5(self, generation_context: Dict[str, Any], slide_topics_list: Optional[list] = None) -> Dict[str, Any]:
        print_("Step 5: Presentation Structure Planning")

        prompt = generation_context["prompt"]
        slide_count_target = generation_context["slide_count_target"]

        # Read a sample from the actual database object
        # Support both database_manager.database.get_sample_text(...) and
        # database_manager.get_sample_text(...) depending on implementation.
        db = getattr(self.database_manager, "database", self.database_manager)
        if hasattr(db, "get_sample_text"):
            database_sample = db.get_sample_text(max_entries=None, max_chars_per_entry=1000)
        else:
            database_sample = ""

        step_5a_prompt = f\"\"\"Based on the research database and the initial prompt, determine how many main topics should be in the presentation.

Initial Prompt: {prompt}
Database Sample: {database_sample}

Respond with only a single integer representing the number of main topics for the presentation.\"\"\"
        raw_step_5a_response = self.api_manager.make_call(step_5a_prompt)
        if not raw_step_5a_response:
            raise Exception("Failed to get topic count in Step 5A")

        total_topics_count = int(str(raw_step_5a_response).strip())
        print_(f"Step 5A: Determined {total_topics_count} topics for presentation")

        step_5b_prompt = f\"\"\"Create a detailed outline of the main topics for the presentation.

Initial Prompt: {prompt}
Number of Topics: {total_topics_count}
Database Sample: {database_sample}

Create a list of dictionaries, each with:
- title: The topic title
- keywords: List of relevant keywords
- text: Brief description of what this topic covers

Respond with a Python list of dictionaries in this format:
[
    {{"title": "Topic 1", "keywords": ["keyword1", "keyword2"], "text": "Description"}},
    {{"title": "Topic 2", "keywords": ["keyword3", "keyword4"], "text": "Description"}}
]\"\"\"
        raw_step_5b_response = self.api_manager.make_call(step_5b_prompt)
        if not raw_step_5b_response:
            raise Exception("Failed to create topic outline in Step 5B")

        try:
            topics_list = ast.literal_eval(str(raw_step_5b_response).strip())
        except (ValueError, SyntaxError) as e:
            raise Exception(f"Failed to parse topics list in Step 5B: {e}")

        if not isinstance(topics_list, list):
            raise Exception("Topics list is not a list in Step 5B")
        for topic in topics_list:
            if not isinstance(topic, dict):
                raise Exception("Topic is not a dictionary in Step 5B")
            for key in ["title", "keywords", "text"]:
                if key not in topic:
                    raise Exception(f"Topic missing required key '{key}' in Step 5B")

        print_(f"Step 5B: Created outline with {len(topics_list)} topics")

        step_5c_prompt = f\"\"\"Allocate slides to each topic for the presentation.

Topics: {topics_list}
Total Slides Target: {slide_count_target}

Respond with a list of integers representing the number of slides for each topic.
The sum should equal {slide_count_target} and each topic should have at least 1 slide.

Respond with only a Python list of integers like: [2, 3, 1, 4, ...]\"\"\"
        raw_step_5c_response = self.api_manager.make_call(step_5c_prompt)
        if not raw_step_5c_response:
            raise Exception("Failed to allocate slides in Step 5C")

        try:
            quantity_list = ast.literal_eval(str(raw_step_5c_response).strip())
        except (ValueError, SyntaxError) as e:
            raise Exception(f"Failed to parse quantity list in Step 5C: {e}")

        if not isinstance(quantity_list, list):
            raise Exception("Quantity list is not a list in Step 5C")
        if len(quantity_list) != len(topics_list):
            raise Exception("Quantity list length doesn't match topics list in Step 5C")

        # Ensure >= 1 per topic
        quantity_list = [max(1, int(q)) for q in quantity_list]

        # Normalize to target
        current_total = sum(quantity_list)
        while current_total != slide_count_target:
            if current_total > slide_count_target:
                i = quantity_list.index(max(quantity_list))
                if quantity_list[i] > 1:
                    quantity_list[i] -= 1
                    current_total -= 1
                else:
                    break
            else:
                i = quantity_list.index(min(quantity_list))
                quantity_list[i] += 1
                current_total += 1

        presentation_topics_list = []
        for i, topic in enumerate(topics_list):
            topic = dict(topic)  # shallow copy
            topic["slides_amount_goal"] = quantity_list[i]
            topic["current_slides_amount"] = quantity_list[i]
            presentation_topics_list.append(topic)

        print_(f"Step 5C: Allocated {sum(quantity_list)} slides across {len(topics_list)} topics")

        return {
            "total_topics_count": total_topics_count,
            "presentation_topics_list": presentation_topics_list,
            "slide_allocation": quantity_list,
            "total_slides_allocated": sum(quantity_list),
            "slides_amount_goal": sum(quantity_list),
            "current_slides_amount": sum(quantity_list),
        }
    cls.execute_step_5 = execute_step_5


def make_patched_core_class(BaseAutomationCore):
    """
    Return a subclass of your existing AutomationCore with patched methods.
    """
    class PatchedAutomationCore(BaseAutomationCore):  # type: ignore[misc]
        pass

    _patch_execute_step_1(PatchedAutomationCore)
    _patch_execute_step_2(PatchedAutomationCore)
    _patch_execute_step_3(PatchedAutomationCore)
    _patch_execute_step_4(PatchedAutomationCore)
    _patch_execute_step_4_5(PatchedAutomationCore)
    _patch_execute_step_5(PatchedAutomationCore)

    return PatchedAutomationCore


def patch_core_instance(core_instance: Any) -> Any:
    """
    Monkey-patch methods on an existing AutomationCore instance.
    Returns the same instance for convenience.
    """
    cls = core_instance.__class__
    _patch_execute_step_1(cls)
    _patch_execute_step_2(cls)
    _patch_execute_step_3(cls)
    _patch_execute_step_4(cls)
    _patch_execute_step_4_5(cls)
    _patch_execute_step_5(cls)
    return core_instance


# tiny compatibility print shim (keeps your run scripts' print_ calls working)
def print_(*args, **kwargs):
    print(*args, **kwargs)
"""
automation_core_patched.py

Drop-in patch module to normalize return types and signatures so the
run_* scripts and tests agree. It does **not** replace your original
AutomationCore file; it overrides a few methods and keeps everything
else intact.

Usage options:

Option A: Replace the class at import time
------------------------------------------
from automation_core import AutomationCore as _OrigAutomationCore
from automation_core_patched import make_patched_core_class
AutomationCore = make_patched_core_class(_OrigAutomationCore)

Option B: Monkey-patch an existing instance
-------------------------------------------
from automation_core_patched import patch_core_instance
core = AutomationCore(...)
patch_core_instance(core)

Either way only Steps 1–5 are overridden; other steps remain unchanged.
"""

from __future__ import annotations

import ast
from typing import Any, Dict, Optional, List


# -------- Result wrappers (behave like both a dict and a list) --------

class _TopicsResult(dict):
    """
    Acts like: {'initial_topics': [...]} AND like a list for len()/iteration.
    """
    def __init__(self, topics: List[str]):
        super().__init__({"initial_topics": topics})
        self._topics = topics

    def __len__(self):  # so len(result) prints the topic count in run_simple_pipeline.py
        return len(self._topics)

    def __iter__(self):
        return iter(self._topics)


class _AdditionalTopicsResult(dict):
    """
    Acts like: {'additional_topics': [...]} AND like a list for len()/iteration.
    """
    def __init__(self, topics: List[str]):
        super().__init__({"additional_topics": topics})
        self._topics = topics

    def __len__(self):
        return len(self._topics)

    def __iter__(self):
        return iter(self._topics)


# --------- Patch helpers ---------

def _patch_execute_step_1(cls):
    def execute_step_1(self, generation_context: Dict[str, Any]) -> _TopicsResult:
        if not getattr(self, "is_initialized", True):
            raise RuntimeError("System must be initialized before executing Step 1")

        print_("Step 1 begun.")

        step_1_prompt = self.create_step_1_prompt(generation_context)
        raw_step_1_response = self.api_manager.make_call(step_1_prompt)
        print_("Raw AI topic response: " + str(raw_step_1_response))

        if raw_step_1_response is None:
            raise RuntimeError("No AI response given for Step 1")

        split_topics = [t.strip(" \t\n.,[]{}()0123456789") for t in raw_step_1_response.split(",")]
        initial_topic_count = generation_context["initial_topic_count"]

        if len(split_topics) < initial_topic_count:
            raise RuntimeError(
                f"{len(split_topics)} topics provided. {initial_topic_count} expected. Got: {split_topics}"
            )
        if len(split_topics) > initial_topic_count:
            split_topics = split_topics[:initial_topic_count]

        print_("Selected topics: " + str(split_topics))
        print_("Step 1 Complete.")

        return _TopicsResult(split_topics)
    cls.execute_step_1 = execute_step_1


def _patch_execute_step_2(cls):
    def execute_step_2(self, generation_context: Dict[str, Any], topics: List[str]) -> Dict[str, Any]:
        if not getattr(self, "is_initialized", True):
            raise RuntimeError("System must be initialized before executing Step 2")

        print_("Step 2 begun.")

        prompt = generation_context["prompt"]
        database_entries_per_topic = generation_context["database_entries_per_topic"]
        knowledge_db = generation_context["knowledge_db"]

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

        added_entries = []
        existing_entry_titles = []

        for topic in topics:
            print_(f"Researching topic: {topic}")
            for i in range(database_entries_per_topic):
                import time; time.sleep(0.05)

                specific_research_prompt = (
                    f"Initial Prompt: ({prompt}) "
                    f"AI Role: ({RESEARCH_PROMPT}) "
                    f"Specific Instructions: ({STRUCTURE_PROMPT_STEP_2})"
                )
                specific_research_prompt = specific_research_prompt.replace("#1", str(existing_entry_titles or "(None)"))
                specific_research_prompt = specific_research_prompt.replace("#3", str(i + 1))
                specific_research_prompt = specific_research_prompt.replace("#2", topic.upper())

                print_("Prompt:\n" + specific_research_prompt + "\nTo be sent to the AI.")
                raw_step_2_response = self.api_manager.make_call(specific_research_prompt)
                print_("Raw AI response to this: " + str(raw_step_2_response))

                if raw_step_2_response is None:
                    print_("Error: During research, AI failed to respond.")
                    continue

                try:
                    step_2_dictionary = ast.literal_eval(raw_step_2_response)
                except Exception:
                    print_("Error: Incorrect format during step 2 research.")
                    continue

                if type(step_2_dictionary) != dict:
                    print_("Error: Response not a dictionary.")
                    continue

                needed_keys = ["title", "keywords", "text", "link"]
                needed_types = [str, list, str, str]
                for k, t in zip(needed_keys, needed_types):
                    if k not in step_2_dictionary or type(step_2_dictionary[k]) is not t:
                        print_(f"Error: {k} missing or wrong type in step 2 research dictionary.")
                        break
                else:
                    if knowledge_db.add_entry(
                        step_2_dictionary["title"],
                        step_2_dictionary["keywords"],
                        step_2_dictionary["text"],
                        step_2_dictionary["link"]
                    ):
                        existing_entry_titles.append(step_2_dictionary["title"])
                        added_entries.append(step_2_dictionary)
                        print_("Added Entry to database. Displaying.")
                        print_(str(knowledge_db.entries[-1]))
                    else:
                        print_("Error: Knowledge Database out of space.")

        print_("Step 2 Complete.")
        return {"research_entries": added_entries}
    cls.execute_step_2 = execute_step_2


def _patch_execute_step_3(cls):
    def execute_step_3(self, generation_context: Dict[str, Any], topics_step_1: List[str], step_2_result: Optional[Dict[str, Any]] = None) -> _AdditionalTopicsResult:
        if not getattr(self, "is_initialized", True):
            raise RuntimeError("System must be initialized before executing Step 3")

        print_("Step 3 begun.")
        step_3_prompt = self.create_step_3_prompt(generation_context, topics_step_1)
        print_("Following Prompt sent to AI:\n" + step_3_prompt + "\n.")
        raw_step_3_response = self.api_manager.make_call(step_3_prompt)

        print_("Raw AI topic response: " + str(raw_step_3_response))
        if raw_step_3_response is None:
            raise RuntimeError("No AI response given for Step 3")

        split_topics_2 = [t.strip(" \t\n.,[]{}()0123456789") for t in raw_step_3_response.split(",")]

        expected_count = generation_context["second_research_round_topic_count"]
        if len(split_topics_2) < expected_count:
            raise RuntimeError(
                f"{len(split_topics_2)} topics provided. {expected_count} expected. Got: {split_topics_2}"
            )
        if len(split_topics_2) > expected_count:
            split_topics_2 = split_topics_2[:expected_count]

        print_("Selected topics: " + str(split_topics_2))
        print_("Step 3 Complete.")
        return _AdditionalTopicsResult(split_topics_2)
    cls.execute_step_3 = execute_step_3


def _patch_execute_step_4(cls):
    def execute_step_4(self, generation_context: Dict[str, Any], topics_step_3: List[str]) -> Dict[str, Any]:
        if not getattr(self, "is_initialized", True):
            raise RuntimeError("System must be initialized before executing Step 4")

        print_("Step 4 begun.")

        prompt = generation_context["prompt"]
        database_entries_per_topic = generation_context["database_entries_per_topic"]
        knowledge_db = generation_context["knowledge_db"]

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

        added_entries = []
        existing_entry_titles = [entry.title for entry in knowledge_db.entries]

        for topic in topics_step_3:
            print_(f"Researching topic: {topic}")
            for i in range(database_entries_per_topic):
                import time; time.sleep(0.05)

                specific_research_prompt = (
                    f"Initial Prompt: ({prompt}) "
                    f"AI Role: ({RESEARCH_PROMPT_2}) "
                    f"Specific Instructions: ({STRUCTURE_PROMPT_STEP_4})"
                )
                specific_research_prompt = specific_research_prompt.replace("#1", str(existing_entry_titles or "(None)"))
                specific_research_prompt = specific_research_prompt.replace("#3", str(i + 1))
                specific_research_prompt = specific_research_prompt.replace("#2", topic.upper())

                print_("Prompt:\n" + specific_research_prompt + "\nTo be sent to the AI.")
                raw_step_4_response = self.api_manager.make_call(specific_research_prompt)
                print_("Raw AI response to this: " + str(raw_step_4_response))

                if raw_step_4_response is None:
                    print_("Error: During research, AI failed to respond.")
                    continue

                try:
                    step_4_dictionary = ast.literal_eval(raw_step_4_response)
                except Exception:
                    print_("Error: Incorrect format during step 4 research.")
                    continue

                if type(step_4_dictionary) != dict:
                    print_("Error: Response not a dictionary.")
                    continue

                needed_keys = ["title", "keywords", "text", "link"]
                needed_types = [str, list, str, str]
                for k, t in zip(needed_keys, needed_types):
                    if k not in step_4_dictionary or type(step_4_dictionary[k]) is not t:
                        print_(f"Error: {k} missing or wrong type in step 4 research dictionary.")
                        break
                else:
                    if knowledge_db.add_entry(
                        step_4_dictionary["title"],
                        step_4_dictionary["keywords"],
                        step_4_dictionary["text"],
                        step_4_dictionary["link"]
                    ):
                        existing_entry_titles.append(step_4_dictionary["title"])
                        added_entries.append(step_4_dictionary)
                        print_("Added Entry to database. Displaying.")
                        print_(str(knowledge_db.entries[-1]))
                    else:
                        print_("Error: Knowledge Database out of space.")

        print_("Step 4 Complete.")
        return {"research_entries": added_entries}
    cls.execute_step_4 = execute_step_4


def _patch_execute_step_4_5(cls):
    def execute_step_4_5(self, generation_context: Dict[str, Any], *legacy_args) -> Dict[str, Any]:
        # Keep existing body if any; this is a compatibility-only shim.
        # If the original method exists, call it with just (generation_context).
        orig = getattr(super(cls, self), "execute_step_4_5", None)
        if callable(orig):
            return orig(generation_context)
        # Otherwise, do nothing but return a benign payload.
        return {"status": "ok"}
    cls.execute_step_4_5 = execute_step_4_5


def _patch_execute_step_5(cls):
    def execute_step_5(self, generation_context: Dict[str, Any], slide_topics_list: Optional[list] = None) -> Dict[str, Any]:
        print_("Step 5: Presentation Structure Planning")

        prompt = generation_context["prompt"]
        slide_count_target = generation_context["slide_count_target"]

        # Read a sample from the actual database object
        # Support both database_manager.database.get_sample_text(...) and
        # database_manager.get_sample_text(...) depending on implementation.
        db = getattr(self.database_manager, "database", self.database_manager)
        if hasattr(db, "get_sample_text"):
            database_sample = db.get_sample_text(max_entries=None, max_chars_per_entry=1000)
        else:
            database_sample = ""

        step_5a_prompt = f\"\"\"Based on the research database and the initial prompt, determine how many main topics should be in the presentation.

Initial Prompt: {prompt}
Database Sample: {database_sample}

Respond with only a single integer representing the number of main topics for the presentation.\"\"\"
        raw_step_5a_response = self.api_manager.make_call(step_5a_prompt)
        if not raw_step_5a_response:
            raise Exception("Failed to get topic count in Step 5A")

        total_topics_count = int(str(raw_step_5a_response).strip())
        print_(f"Step 5A: Determined {total_topics_count} topics for presentation")

        step_5b_prompt = f\"\"\"Create a detailed outline of the main topics for the presentation.

Initial Prompt: {prompt}
Number of Topics: {total_topics_count}
Database Sample: {database_sample}

Create a list of dictionaries, each with:
- title: The topic title
- keywords: List of relevant keywords
- text: Brief description of what this topic covers

Respond with a Python list of dictionaries in this format:
[
    {{"title": "Topic 1", "keywords": ["keyword1", "keyword2"], "text": "Description"}},
    {{"title": "Topic 2", "keywords": ["keyword3", "keyword4"], "text": "Description"}}
]\"\"\"
        raw_step_5b_response = self.api_manager.make_call(step_5b_prompt)
        if not raw_step_5b_response:
            raise Exception("Failed to create topic outline in Step 5B")

        try:
            topics_list = ast.literal_eval(str(raw_step_5b_response).strip())
        except (ValueError, SyntaxError) as e:
            raise Exception(f"Failed to parse topics list in Step 5B: {e}")

        if not isinstance(topics_list, list):
            raise Exception("Topics list is not a list in Step 5B")
        for topic in topics_list:
            if not isinstance(topic, dict):
                raise Exception("Topic is not a dictionary in Step 5B")
            for key in ["title", "keywords", "text"]:
                if key not in topic:
                    raise Exception(f"Topic missing required key '{key}' in Step 5B")

        print_(f"Step 5B: Created outline with {len(topics_list)} topics")

        step_5c_prompt = f\"\"\"Allocate slides to each topic for the presentation.

Topics: {topics_list}
Total Slides Target: {slide_count_target}

Respond with a list of integers representing the number of slides for each topic.
The sum should equal {slide_count_target} and each topic should have at least 1 slide.

Respond with only a Python list of integers like: [2, 3, 1, 4, ...]\"\"\"
        raw_step_5c_response = self.api_manager.make_call(step_5c_prompt)
        if not raw_step_5c_response:
            raise Exception("Failed to allocate slides in Step 5C")

        try:
            quantity_list = ast.literal_eval(str(raw_step_5c_response).strip())
        except (ValueError, SyntaxError) as e:
            raise Exception(f"Failed to parse quantity list in Step 5C: {e}")

        if not isinstance(quantity_list, list):
            raise Exception("Quantity list is not a list in Step 5C")
        if len(quantity_list) != len(topics_list):
            raise Exception("Quantity list length doesn't match topics list in Step 5C")

        # Ensure >= 1 per topic
        quantity_list = [max(1, int(q)) for q in quantity_list]

        # Normalize to target
        current_total = sum(quantity_list)
        while current_total != slide_count_target:
            if current_total > slide_count_target:
                i = quantity_list.index(max(quantity_list))
                if quantity_list[i] > 1:
                    quantity_list[i] -= 1
                    current_total -= 1
                else:
                    break
            else:
                i = quantity_list.index(min(quantity_list))
                quantity_list[i] += 1
                current_total += 1

        presentation_topics_list = []
        for i, topic in enumerate(topics_list):
            topic = dict(topic)  # shallow copy
            topic["slides_amount_goal"] = quantity_list[i]
            topic["current_slides_amount"] = quantity_list[i]
            presentation_topics_list.append(topic)

        print_(f"Step 5C: Allocated {sum(quantity_list)} slides across {len(topics_list)} topics")

        return {
            "total_topics_count": total_topics_count,
            "presentation_topics_list": presentation_topics_list,
            "slide_allocation": quantity_list,
            "total_slides_allocated": sum(quantity_list),
            "slides_amount_goal": sum(quantity_list),
            "current_slides_amount": sum(quantity_list),
        }
    cls.execute_step_5 = execute_step_5


def make_patched_core_class(BaseAutomationCore):
    """
    Return a subclass of your existing AutomationCore with patched methods.
    """
    class PatchedAutomationCore(BaseAutomationCore):  # type: ignore[misc]
        pass

    _patch_execute_step_1(PatchedAutomationCore)
    _patch_execute_step_2(PatchedAutomationCore)
    _patch_execute_step_3(PatchedAutomationCore)
    _patch_execute_step_4(PatchedAutomationCore)
    _patch_execute_step_4_5(PatchedAutomationCore)
    _patch_execute_step_5(PatchedAutomationCore)

    return PatchedAutomationCore


def patch_core_instance(core_instance: Any) -> Any:
    """
    Monkey-patch methods on an existing AutomationCore instance.
    Returns the same instance for convenience.
    """
    cls = core_instance.__class__
    _patch_execute_step_1(cls)
    _patch_execute_step_2(cls)
    _patch_execute_step_3(cls)
    _patch_execute_step_4(cls)
    _patch_execute_step_4_5(cls)
    _patch_execute_step_5(cls)
    return core_instance


# tiny compatibility print shim (keeps your run scripts' print_ calls working)
def print_(*args, **kwargs):
    print(*args, **kwargs)
