import ai_entry  # This module will be defined separately
from logging_funcs import print_, print_2
import random

class AIDatabase:
    def __init__(self, name: str, max_size: int):
        self.name = name
        self.max_size = max_size
        self.entries = []
        self.current_id = 0

    def search(self, query: str) -> list:
        """
        Searches entries for partial keyword matches.
        Returns entries sorted by:
          1. Number of partial keyword matches (descending)
          2. Uses (ascending)
          3. Random tie-breaker
        """
        query_words = query.lower().split()

        results = []
        for entry in self.entries:
            match_count = 0
            for kw in entry.keywords:
                kw_lower = kw.lower()
                if any(q in kw_lower or kw_lower in q for q in query_words):
                    match_count += 1

            if match_count > 0:
                results.append((entry, match_count))

        # Randomize tie-breaker before sorting
        random.shuffle(results)

        results.sort(key=lambda x: (x[0].uses, -x[1]))

        return [entry for entry, _ in results]

    def add_entry(self, title: str, keywords: list[str], text: str, link: str):
        """Adds a new entry if max size not exceeded."""
        if len(self.entries) >= self.max_size:
            print_("Database is full. Cannot add new entry.")
            return False

        entry_id = str(self.current_id)
        new_entry = ai_entry.AIEntry(entry_id, title, keywords, text, link)
        self.entries.append(new_entry)
        self.current_id += 1
        return True

    def delete_entry(self, index: int):
        """Deletes the entry at the specified index."""
        if 0 <= index < len(self.entries):
            del self.entries[index]
            return True
        else:
            print_2(f"Invalid index: {index}")
            return False

    def at(self, index: int):
        """Returns the entry at the specified index, or None if invalid."""
        if 0 <= index < len(self.entries):
            return self.entries[index]
        else:
            print_2(f"Index out of bounds: {index}")
            return None
        
    def __str__(self):
        if not self.entries:
            return f"Database '{self.name}' is empty."
        return f"Database '{self.name}' with {len(self.entries)} entries:\n" + \
           "\n\n".join([f"[{i}] {str(entry)}" for i, entry in enumerate(self.entries)])

    def print_database(self):
        print_(self.__str__())

    def get_all_text(self) -> str:
        return "\n\n".join(entry.text for entry in self.entries)
    
    def get_sample_text(self, max_entries: int = 10, max_chars_per_entry: int = 300) -> str:
        """
        Returns a joined sample of text from across the database entries.
        Each sample is capped in length and distributed across the DB.
        """
        if not self.entries:
            return ""

        if max_entries == None:
            step = 1
        else:
            step = max(1, len(self.entries) // max_entries)
        sampled_texts = []

        for i in range(0, len(self.entries), step):
            text = self.entries[i].text.strip().replace("\n", " ")
            truncated = text[:max_chars_per_entry]
            if len(text) > max_chars_per_entry:
                truncated += "..."
            sampled_texts.append(truncated)

            if max_entries != None:
                if len(sampled_texts) >= max_entries:
                    break

        return "\n\n".join(sampled_texts)
    
    def get_entry_by_id(self, entry_id: int):
        """Returns the KnowledgeEntry with the matching ID, or None if not found."""
        for entry in self.entries:
            if entry.id == entry_id:
                return entry
        return None
    
    def get_all_keywords(self) -> list[str]:
        """Returns a sorted list of all unique keywords across the entire database."""
        keyword_set = set()
        for entry in self.entries:
            keyword_set.update(entry.keywords)
        return sorted(keyword_set)
    
