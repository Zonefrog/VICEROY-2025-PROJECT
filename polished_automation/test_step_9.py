#!/usr/bin/env python3
"""
Test script for Step 9: Source Association and Content Enhancement
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from polished_automation.automation_core import AutomationCore, SystemConfig
from logging_funcs import print_
from presentation_class import PresentationBuilder
from slide_class import SlideData

def test_step_9():
    """Test Step 9: Source Association and Content Enhancement"""
    print_("🧪 Testing Step 9: Source Association and Content Enhancement")
    
    # Create configuration
    config = SystemConfig(
        use_manual_api=False,  # Use automatic API mode for testing
        slide_count_target=20
    )
    
    # Create automation core and initialize it
    core = AutomationCore(config)
    if not core.initialize():
        print_("❌ Failed to initialize automation core")
        return False
    
    # Mock data from Step 4.5
    mock_slide_topics_list = [
        "Introduction to Artificial Intelligence",
        "Types of AI Systems",
        "AI Applications Overview",
        "Machine Learning Fundamentals",
        "Supervised Learning Algorithms",
        "Unsupervised Learning Techniques",
        "Deep Learning Basics",
        "Neural Network Architectures",
        "Training Deep Learning Models",
        "Deep Learning Applications",
        "AI in Healthcare",
        "AI in Finance",
        "AI in Manufacturing",
        "AI in Transportation",
        "Future AI Trends",
        "Ethical Considerations in AI",
        "AI Safety and Governance",
        "Impact of AI on Society",
        "Challenges in AI Development",
        "Conclusion and Next Steps"
    ]
    
    # Mock teaching outline from Step 4.5
    mock_teaching_outline = """
    Detailed Teaching Outline for AI and Machine Learning:
    
    1. Introduction to Artificial Intelligence
       - Definition and scope of AI
       - Historical development and milestones
       - Current state of AI technology
    
    2. Types of AI Systems
       - Narrow AI vs General AI
       - Rule-based systems
       - Machine learning systems
       - Expert systems
    
    3. AI Applications Overview
       - Industry applications
       - Consumer applications
       - Research applications
       - Future potential applications
    
    4. Machine Learning Fundamentals
       - Definition and principles
       - Types of learning
       - Data requirements
       - Model evaluation
    
    5. Supervised Learning Algorithms
       - Linear regression
       - Classification algorithms
       - Decision trees
       - Support vector machines
    
    6. Unsupervised Learning Techniques
       - Clustering algorithms
       - Dimensionality reduction
       - Association rules
       - Anomaly detection
    
    7. Deep Learning Basics
       - Neural network fundamentals
       - Activation functions
       - Backpropagation
       - Gradient descent
    
    8. Neural Network Architectures
       - Feedforward networks
       - Convolutional networks
       - Recurrent networks
       - Transformer networks
    
    9. Training Deep Learning Models
       - Data preparation
       - Model initialization
       - Training process
       - Hyperparameter tuning
    
    10. Deep Learning Applications
        - Computer vision
        - Natural language processing
        - Speech recognition
        - Game playing
    
    11. AI in Healthcare
        - Medical diagnosis
        - Drug discovery
        - Patient monitoring
        - Healthcare administration
    
    12. AI in Finance
        - Algorithmic trading
        - Risk assessment
        - Fraud detection
        - Customer service
    
    13. AI in Manufacturing
        - Predictive maintenance
        - Quality control
        - Supply chain optimization
        - Robotics and automation
    
    14. AI in Transportation
        - Autonomous vehicles
        - Traffic management
        - Logistics optimization
        - Public transportation
    
    15. Future AI Trends
        - Explainable AI
        - Edge computing
        - AI ethics
        - Quantum AI
    
    16. Ethical Considerations in AI
        - Bias and fairness
        - Privacy concerns
        - Accountability
        - Transparency
    
    17. AI Safety and Governance
        - Safety protocols
        - Regulatory frameworks
        - International cooperation
        - Best practices
    
    18. Impact of AI on Society
        - Economic impact
        - Social changes
        - Employment effects
        - Cultural implications
    
    19. Challenges in AI Development
        - Technical challenges
        - Resource limitations
        - Ethical dilemmas
        - Regulatory hurdles
    
    20. Conclusion and Next Steps
        - Summary of key concepts
        - Future directions
        - Implementation strategies
        - Continued learning resources
    """
    
    # Mock presentation object with titles and content from previous steps
    presentation = PresentationBuilder()
    mock_titles = [
        "Understanding the Foundations of Artificial Intelligence",
        "Exploring the Diversity of AI Systems",
        "AI Applications Revolutionizing Industries",
        "Mastering the Basics of Machine Learning",
        "Mastering Supervised Learning Algorithms in Artificial Intelligence",
        "Mastering Unsupervised Learning Techniques in Artificial Intelligence",
        "Delving into the Depths of Deep Learning",
        "Diving into the World of Neural Network Architectures",
        "Mastering the Training Process of Deep Learning Models",
        "Exploring the Impact of Deep Learning in Diverse Fields",
        "Harnessing the Power of Artificial Intelligence in Healthcare",
        "Revolutionizing Financial Services with Artificial Intelligence",
        "Revolutionizing Manufacturing with Artificial Intelligence",
        "Transforming Transportation with Artificial Intelligence",
        "Navigating the Future of Artificial Intelligence: Emerging Trends and Innovations",
        "Addressing Ethical Dilemmas in Artificial Intelligence",
        "Safeguarding the Future: Ensuring AI Safety and Governance",
        "Analyzing the Societal Impacts of Artificial Intelligence",
        "Overcoming Hurdles: Addressing the Challenges in AI Development",
        "Embracing the Future: Implementing AI Strategies for Success"
    ]
    
    mock_content_themes = [
        "Overview of Artificial Intelligence",
        "Types of AI Systems and their Applications",
        "AI Applications Overview across Industries",
        "Machine Learning Fundamentals",
        "Supervised Learning Algorithms",
        "Unsupervised Learning Techniques",
        "Deep Learning Basics",
        "Neural Network Architectures",
        "Training Deep Learning Models",
        "Deep Learning Applications in Various Fields",
        "AI in Healthcare",
        "AI in Finance",
        "AI in Manufacturing",
        "AI in Transportation",
        "Future AI Trends",
        "Ethical Considerations in AI",
        "AI Safety and Governance",
        "Impact of AI on Society",
        "Challenges in AI Development",
        "Conclusion and Next Steps"
    ]
    
    for i, slide_topic in enumerate(mock_slide_topics_list):
        new_slide = SlideData(title=mock_titles[i], content=mock_content_themes[i], sources=[])
        presentation.slides.append(new_slide)
    
    # Mock knowledge database with research entries
    class MockKnowledgeDB:
        def __init__(self):
            self.entries = [
                {
                    "id": 1,
                    "title": "AI Fundamentals",
                    "keywords": ["artificial intelligence", "basics", "fundamentals"],
                    "text": "Artificial intelligence is a branch of computer science that aims to create intelligent machines capable of performing tasks that typically require human intelligence.",
                    "link": "https://example.com/ai-basics",
                    "uses": 0
                },
                {
                    "id": 2,
                    "title": "Machine Learning Overview",
                    "keywords": ["machine learning", "algorithms", "supervised", "unsupervised"],
                    "text": "Machine learning is a subset of AI that enables computers to learn and improve from experience without being explicitly programmed.",
                    "link": "https://example.com/ml-overview",
                    "uses": 0
                },
                {
                    "id": 3,
                    "title": "Deep Learning Networks",
                    "keywords": ["neural networks", "deep learning", "training"],
                    "text": "Deep learning uses neural networks with multiple layers to model complex patterns in data and achieve state-of-the-art performance.",
                    "link": "https://example.com/deep-learning",
                    "uses": 0
                },
                {
                    "id": 4,
                    "title": "AI in Healthcare",
                    "keywords": ["healthcare", "medical", "diagnosis", "treatment"],
                    "text": "AI is revolutionizing healthcare through improved diagnosis, personalized treatment plans, and enhanced patient care.",
                    "link": "https://example.com/ai-healthcare",
                    "uses": 0
                },
                {
                    "id": 5,
                    "title": "AI in Finance",
                    "keywords": ["finance", "banking", "trading", "risk"],
                    "text": "Financial institutions are leveraging AI for algorithmic trading, risk assessment, fraud detection, and customer service automation.",
                    "link": "https://example.com/ai-finance",
                    "uses": 0
                },
                {
                    "id": 6,
                    "title": "AI Ethics and Safety",
                    "keywords": ["ethics", "safety", "governance", "bias"],
                    "text": "As AI becomes more prevalent, addressing ethical concerns, safety protocols, and governance frameworks is crucial.",
                    "link": "https://example.com/ai-ethics",
                    "uses": 0
                },
                {
                    "id": 7,
                    "title": "Future of AI",
                    "keywords": ["future", "trends", "innovation", "development"],
                    "text": "Emerging trends in AI include explainable AI, edge computing, quantum AI, and enhanced human-AI collaboration.",
                    "link": "https://example.com/ai-future",
                    "uses": 0
                },
                {
                    "id": 8,
                    "title": "AI Applications",
                    "keywords": ["applications", "industry", "automation", "optimization"],
                    "text": "AI is being applied across various industries including manufacturing, transportation, retail, and entertainment.",
                    "link": "https://example.com/ai-applications",
                    "uses": 0
                }
            ]
        
        def search(self, search_term):
            """Mock search that returns entries containing keywords from search term"""
            results = []
            search_keywords = search_term.lower().split()
            
            for entry in self.entries:
                entry_keywords = " ".join(entry["keywords"]).lower()
                if any(keyword in entry_keywords for keyword in search_keywords):
                    # Create a mock entry object with add_use method
                    class MockEntry:
                        def __init__(self, data):
                            self.id = data["id"]
                            self.title = data["title"]
                            self.keywords = data["keywords"]
                            self.text = data["text"]
                            self.link = data["link"]
                            self.uses = data["uses"]
                        
                        def add_use(self):
                            self.uses += 1
                    
                    results.append(MockEntry(entry))
            
            return results
        
        def get_all_keywords(self):
            """Return all keywords from all entries"""
            all_keywords = []
            for entry in self.entries:
                all_keywords.extend(entry["keywords"])
            return list(set(all_keywords))  # Remove duplicates
    
    # Mock generation context
    generation_context = {
        "prompt": "Create a comprehensive presentation about artificial intelligence",
        "slide_count_target": 20,
        "knowledge_db": MockKnowledgeDB()
    }
    
    try:
        # Execute Step 9
        print_("🚀 Executing Step 9...")
        updated_presentation = core.execute_step_9(generation_context, mock_slide_topics_list, mock_teaching_outline, presentation)
        
        # Verify results
        print_(f"✅ Step 9 completed successfully!")
        print_(f"📊 Total slides processed: {len(updated_presentation.slides)}")
        
        # Check source associations
        slides_with_sources = 0
        total_sources = 0
        print_("\n📋 Source Associations:")
        for i, slide in enumerate(updated_presentation.slides):
            if slide.sources:
                slides_with_sources += 1
                total_sources += len(slide.sources)
                print_(f"   ✅ Slide {i + 1}: {len(slide.sources)} sources")
                for j, source in enumerate(slide.sources):
                    print_(f"      Source {j + 1}: {source.title}")
            else:
                print_(f"   ❌ Slide {i + 1}: No sources associated")
        
        print_(f"📝 Slides with sources: {slides_with_sources}/{len(updated_presentation.slides)}")
        print_(f"📊 Total sources associated: {total_sources}")
        
        # Check content enhancement
        slides_with_enhanced_content = 0
        print_("\n📋 Content Enhancement:")
        for i, slide in enumerate(updated_presentation.slides):
            if slide.content and len(slide.content) > len(mock_content_themes[i]):
                slides_with_enhanced_content += 1
                print_(f"   ✅ Slide {i + 1}: Content enhanced ({len(mock_content_themes[i])} → {len(slide.content)} chars)")
            else:
                print_(f"   ⚠️ Slide {i + 1}: Content not significantly enhanced")
        
        print_(f"📝 Slides with enhanced content: {slides_with_enhanced_content}/{len(updated_presentation.slides)}")
        
        # Check source usage tracking
        print_("\n📊 Source Usage Tracking:")
        for entry in generation_context["knowledge_db"].entries:
            print_(f"   Source '{entry['title']}': {entry['uses']} uses")
        
        print_("\n🎉 Step 9 test completed successfully!")
        return True
        
    except Exception as e:
        print_(f"❌ Step 9 test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_step_9()
    sys.exit(0 if success else 1)
















