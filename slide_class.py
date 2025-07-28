from source_class import Source

class SlideData:
    def __init__(self, title: str, content: str, sources: list[Source] = None):
        self.title = title
        self.content = content
        self.sources = sources if sources is not None else []

    def add_source(self, source: Source):
        self.sources.append(source)

    def __str__(self):
        sources_str = "\n".join([str(source) for source in self.sources])
        return (
            f"Title: {self.title}\n"
            f"Content:\n{self.content}\n"
            f"Sources:\n{sources_str if sources_str else 'None'}"
        )
    
    def get_source_footer(self, max_sources: int = 5) -> str:
        """Returns compact source footer like: 'Sources: [1], [2], etc.'"""
        if not self.sources:
            return ""

        ids = [f"[{src.id}]" for src in self.sources]
        if len(ids) > max_sources:
            ids = ids[:max_sources]
            ids.append("etc.")

        return "Sources: " + ", ".join(ids)

    def get_combined_text(self, max_sources: int = 5) -> str:
        """Returns full slide content including content + source footer."""
        lines = [self.content.strip()]

        footer = self.get_source_footer(max_sources)
        if footer:
            lines.append("")  # blank line
            lines.append(footer)

        return "\n".join(lines)