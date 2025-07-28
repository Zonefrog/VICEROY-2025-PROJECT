from logging_funcs import print_, print_2

class AIEntry:
    def __init__(self, entry_id: str, title: str, keywords: list[str], text: str, link: str):
        self.id = entry_id
        self.title = title
        self.keywords = keywords
        self.text = text
        self.uses = 0
        self.link = link

    def add_use(self):
        """Increments the use counter by one."""
        self.uses += 1

    def __str__(self):
        return (
            f"ID: {self.id}\n"
            f"Title: {self.title}\n"
            f"Keywords: {', '.join(self.keywords)}\n"
            f"Uses: {self.uses}\n"
            f"Text: {self.text}"
            f"Link: {self.link}"
        )

    def print_entry(self):
        print_(self.__str__())