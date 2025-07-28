# Global counter for unique source IDs
_next_source_id = 0

def _get_next_source_id():
    global _next_source_id
    source_id = _next_source_id
    _next_source_id += 1
    return source_id

class Source:
    def __init__(self, title: str, link: str, linked_entry=None):
        self.id = _get_next_source_id()
        self.title = title
        self.link = link
        self.linked_entry = linked_entry  # Expected to be an AIEntry instance or None

    def __str__(self):
        entry_info = f" (linked to entry ID: {self.linked_entry.id})" if self.linked_entry else ""
        return f"[{self.id}] {self.title} - {self.link}{entry_info}"