import ai_entry
import ai_database

import presentation_class
import slide_class
import source_class

def run_all_tests(safe_call_api, test_output_path, run_name):
    print("\n===== Running All Tests =====\n")

    print("--- test_source ---")
    test_source()

    print("\n--- test_source_with_entry ---")
    test_source_with_entry()

    print("\n--- test_entry ---")
    test_entry()

    print("\n--- test_database ---")
    test_database()

    print("\n--- test_slide ---")
    test_slide()

    print("\n--- test_presentation_structure ---")
    test_presentation_structure()

    print("\n--- test presentation save ---")
    test_presentation_save(test_output_path, run_name)

    print("\n--- test presentation utils ---")
    test_slide_utilities(test_output_path, run_name)

    print("\n--- test_api ---")
    test_api(safe_call_api)

    print("\n--- test_database_search ---")
    test_database_search()

    print("\n--- Running test: test_unique_sources ---")
    test_unique_sources()

    print("\n===== All Tests Completed =====")

def test_database():
    """Tests basic AIDatabase functionality."""
    db = ai_database.AIDatabase(name="TestDB", max_size=3)

    # Add entries
    db.add_entry("First", ["alpha", "start"], "This is the first entry.")
    db.add_entry("Second", ["beta", "middle"], "This is the second entry.")
    db.add_entry("Third", ["gamma", "end"], "This is the third entry.")

    print("\nDatabase after adding entries:")
    db.print_database()

    # Try to add a fourth entry (should fail due to max_size)
    success = db.add_entry("Fourth", ["overflow"], "This should not be added.")
    print(f"\nAttempt to add fourth entry: {'Success' if success else 'Failed as expected'}")

    # Access and print an entry
    entry = db.at(1)
    print("\nEntry at index 1:")
    if entry:
        entry.print_entry()

    # Delete an entry
    db.delete_entry(1)
    print("\nDatabase after deleting entry at index 1:")
    db.print_database()

def test_entry():
    """Creates an AIEntry and prints its data to verify functionality."""
    entry = ai_entry.AIEntry(
        entry_id="001",
        title="Test Entry",
        keywords=["test", "entry", "sample"],
        text="This is a sample text for testing the AIEntry class."
    )

    print("Created Entry:")
    print(entry)

    # Test incrementing uses
    entry.add_use()
    entry.add_use()
    print("\nAfter incrementing uses twice:")
    print(f"Uses: {entry.uses}")

def test_api(safe_call_api):
    """Tests the API call with a basic arithmetic prompt."""
    response = safe_call_api("What is 1+2&6=?")
    if response:
        text = response
        print("API Response:", text)
    else:
        print("API call failed or returned no response.")

def test_source():
    """Creates and prints a Source object without a linked database entry."""
    source = source_class.Source(
        title="OpenAI Blog",
        link="https://openai.com/blog/"
    )
    
    print("Created Source:")
    print(source)

def test_source_with_entry():
    """Creates a Source linked to a real database entry and prints both."""
    
    # Set up a temporary database
    db = ai_database.AIDatabase(name="TempTestDB", max_size=5)
    
    # Add a dummy entry to the database
    db.add_entry(
        title="Example Entry",
        keywords=["example", "source", "link"],
        text="This entry is just for testing source linking."
    )
    
    # Link source to the first entry
    entry = db.at(0)
    source = source_class.Source(
        title="Test Source with Entry Link",
        link="https://example.com/source-info",
        linked_entry=entry
    )
    
    print("Created Source linked to database entry:")
    print(source)
    print("\nLinked entry:")
    entry.print_entry()

def test_slide():
    """Creates a SlideData object with one source and prints it."""
    
    # Create a slide
    slide = slide_class.SlideData(
        title="Test Slide",
        content="• Point one\n• Point two\n• Point three"
    )

    # Create and add a source
    source = source_class.Source(
        title="Wikipedia",
        link="https://en.wikipedia.org/wiki/Test"
    )
    slide.add_source(source)

    print("Created Slide with Source:")
    print(slide)

def test_presentation_structure():
    """Creates a PresentationBuilder, adds slides, and prints their contents (no file saving)."""
    
    presentation = presentation_class.PresentationBuilder(title="Test Presentation")

    # Slide 1 — no sources
    slide1 = slide_class.SlideData(
        title="Intro Slide",
        content="Welcome\nOverview"
    )
    presentation.add_slide(slide1)

    # Slide 2 — with a source
    slide2 = slide_class.SlideData(
        title="Topic Slide",
        content="Point A\nPoint B"
    )
    source = source_class.Source(
        title="Example Source",
        link="https://example.com/info"
    )
    slide2.add_source(source)
    presentation.add_slide(slide2)

    # Print out each slide
    print(f"Presentation: {presentation.title}")
    for i, slide in enumerate(presentation.slides):
        print(f"\n--- Slide {i + 1} ---")
        print(slide)

def test_presentation_save(test_output_path, run_name):
    """Creates a sample presentation and saves it to a file."""

    # Build presentation
    presentation = presentation_class.PresentationBuilder(title="Save Test Presentation")

    # Slide 1: No sources
    slide1 = slide_class.SlideData(
        title="Slide One",
        content="Hello\nThis is a test slide"
    )
    presentation.add_slide(slide1)

    # Slide 2: With a source
    slide2 = slide_class.SlideData(
        title="Slide Two",
        content="Includes a source"
    )
    source = source_class.Source(
        title="Example.com",
        link="https://example.com"
    )
    slide2.add_source(source)
    presentation.add_slide(slide2)

    #slide3
    slide3 = slide_class.SlideData(
        title="Slide Three",
        content="AAAAAAAAAAAAAAAAAAAAAAAAAAAAA" * 50
    )
    presentation.add_slide(slide3)

    presentation.add_title_slide()

    # Save file
    filename = f"presentation_test_{run_name}"
    presentation.save_to_file(test_output_path, filename)

def test_slide_utilities(test_output_path, run_name):
    """Tests title slide, sources slides, and dynamic slide content behavior."""

    pres = presentation_class.PresentationBuilder(title="Slide Utility Test")

    # Add a few slides with sources
    for i in range(3):
        slide = slide_class.SlideData(
            title=f"Main Slide {i+1}",
            content=f"This is slide {i+1}.\nIt contains example content."
        )
        slide.add_source(source_class.Source(f"Source Title {i+1}", f"https://example.com/{i+1}"))
        pres.add_slide(slide)

    # Add shared source
    shared = source_class.Source("Shared Source", "https://example.com/shared")
    for slide in pres.slides:
        slide.add_source(shared)

    # Add title slide at the beginning
    pres.add_title_slide()

    # Add sources slide(s) at the end
    pres.add_sources_slides()

    # Save presentation to file
    filename = f"test_slide_utilities_{run_name}"
    pres.save_to_file(test_output_path, filename)

    print(f"Presentation with slides and sources saved to: {filename}.pptx")

def test_database_search():
    """Tests the keyword-based search functionality of the AIDatabase."""

    db = ai_database.AIDatabase(name="SearchTestDB", max_size=10)

    # Add entries with varying keywords and uses
    db.add_entry("AI Overview", ["ai", "machine", "learning"], "An overview of AI.")
    db.entries[-1].uses = 3

    db.add_entry("Robotics Intro", ["robot", "automation", "ai"], "Intro to robotics.")
    db.entries[-1].uses = 1

    db.add_entry("History of Computing", ["history", "computing", "hardware"], "Early days of computers.")
    db.entries[-1].uses = 0

    db.add_entry("AI Ethics", ["ai", "ethics", "philosophy"], "Discussion on AI ethics.")
    db.entries[-1].uses = 2

    # Perform a search
    print("Search results for: 'ai robot':")
    results = db.search("ai robot")
    for entry in results:
        print(entry)
        print("-" * 40)

def test_unique_sources():
    """Tests collection of unique sources across multiple slides."""

    pres = presentation_class.PresentationBuilder(title="Unique Source Test")

    # Create two identical source objects (same id)
    shared_source = source_class.Source(
        title="Shared Source",
        link="https://example.com/shared"
    )

    # Slide 1: has shared + unique
    slide1 = slide_class.SlideData(
        title="Slide 1",
        content="Slide with two sources"
    )
    slide1.add_source(shared_source)
    slide1.add_source(source_class.Source("Unique 1", "https://example.com/u1"))
    pres.add_slide(slide1)

    # Slide 2: has shared again
    slide2 = slide_class.SlideData(
        title="Slide 2",
        content="Slide with shared again"
    )
    slide2.add_source(shared_source)
    pres.add_slide(slide2)

    # Slide 3: new source
    slide3 = slide_class.SlideData(
        title="Slide 3",
        content="Another unique source"
    )
    slide3.add_source(source_class.Source("Unique 2", "https://example.com/u2"))
    pres.add_slide(slide3)

    # Collect unique sources
    print("Unique sources in presentation:")
    unique = pres.get_all_unique_sources()
    for src in unique:
        print(src)

