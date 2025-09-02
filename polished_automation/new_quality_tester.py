#!/usr/bin/env python3
"""
New Quality Tester for Automated Presentations
Uses different grading methods than the original powerpoint_rater.py
"""

import os
import json
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path
import time
import re

# Import the automation core for API methods
from automation_core import AutomationCore, SystemConfig
from logging_funcs import print_

class NewQualityTester:
    """New quality testing system using different evaluation methods."""
    
    def __init__(self, config: SystemConfig):
        self.config = config
        self.core = None
        self.test_results = []
        
        # Dictionary to translate folder names to actual percentages
        self.folder_to_percent = {
            '0': 0.0,
            '5': 5.0,
            '10': 10.0,
            '15': 15.0,
            '20': 20.0,
            '25': 25.0,
            '30': 30.0,
            '35': 35.0,
            '40': 40.0,
            '45': 45.0,
            '50': 50.0
        }
        
    def initialize(self) -> bool:
        """Initialize the tester with automation core."""
        try:
            self.core = AutomationCore(self.config)
            return self.core.initialize(require_confirmation=False)
        except Exception as e:
            print_(f"❌ Failed to initialize tester: {e}")
            return False
    
    def scan_experiment_results(self) -> Dict[str, float]:
        """
        Scan the experiment_results folder and map folder names to percentages.
        
        Returns:
            Dictionary mapping folder paths to their corresponding percentages
        """
        print_("🔍 Scanning experiment_results folder...")
        
        # Path to the experiment_results folder (one level up from polished_automation)
        experiment_results_path = Path(__file__).parent.parent / "Experiment_results"
        
        if not experiment_results_path.exists():
            print_(f"❌ Experiment_results folder not found at: {experiment_results_path}")
            return {}
        
        folder_percentages = {}
        
        # Iterate through each folder in experiment_results
        for folder_name in os.listdir(experiment_results_path):
            folder_path = experiment_results_path / folder_name
            
            # Check if it's a directory and if we have a translation for it
            if folder_path.is_dir() and folder_name in self.folder_to_percent:
                percentage = self.folder_to_percent[folder_name]
                folder_percentages[str(folder_path)] = percentage
            elif folder_path.is_dir():
                print_(f"⚠️ Unknown folder: {folder_name} (no percentage mapping)")
        
        print_(f"✅ Found {len(folder_percentages)} experiment folders")
        return folder_percentages
    
    def find_presentations_and_outlines(self, folder_percentages: Dict[str, float]) -> Dict[str, List[Dict[str, Any]]]:
        """
        Find presentation files and their associated outline files in each experiment folder.
        
        Args:
            folder_percentages: Dictionary mapping folder paths to percentages
            
        Returns:
            Dictionary mapping percentages to lists of presentation/outline pairs
        """
        print_("🔍 Finding presentations and outlines in each folder...")
        
        results = {}
        
        # Sort folders alphabetically (lowest to highest percentage)
        sorted_folders = sorted(folder_percentages.items(), key=lambda x: x[0])
        
        # Fix the 5% ordering issue - ensure it comes after 0%
        if len(sorted_folders) > 1:
            # Find 0% and 5% entries
            zero_percent = None
            five_percent = None
            other_folders = []
            
            for folder_path, percentage in sorted_folders:
                if percentage == 0.0:
                    zero_percent = (folder_path, percentage)
                elif percentage == 5.0:
                    five_percent = (folder_path, percentage)
                else:
                    other_folders.append((folder_path, percentage))
            
            # Reconstruct with correct order: 0%, 5%, then others
            if zero_percent and five_percent:
                sorted_folders = [zero_percent, five_percent] + other_folders
        
        for folder_path, percentage in sorted_folders:
            folder_path_obj = Path(folder_path)
            presentations = []
            
            # Get all files in the folder
            all_files = list(folder_path_obj.iterdir())
            
            # Separate PPTX and TXT files
            pptx_files = [f for f in all_files if f.suffix.lower() == '.pptx']
            txt_files = [f for f in all_files if f.suffix.lower() == '.txt']
            
            # Process each presentation file
            for pptx_file in pptx_files:
                # Get creation time of the PPTX file
                pptx_creation_time = pptx_file.stat().st_ctime
                
                # Find the most recent TXT file created before this PPTX file
                associated_outline = self._find_associated_outline(txt_files, pptx_creation_time)
                
                if associated_outline:
                    # Extract PPTX contents into AI-readable format
                    pptx_contents = self._extract_pptx_contents(pptx_file)
                    
                    presentations.append({
                        'presentation_file': str(pptx_file),
                        'outline_file': str(associated_outline),
                        'presentation_name': pptx_file.name,
                        'outline_name': associated_outline.name,
                        'percentage': percentage,
                        'pptx_contents': pptx_contents
                    })
            
            results[percentage] = presentations
        
        total_presentations = sum(len(presentations) for presentations in results.values())
        print_(f"✅ Found {total_presentations} total presentations with outlines")
        return results
    
    def _find_associated_outline(self, txt_files: List[Path], pptx_creation_time: float) -> Optional[Path]:
        """
        Find the TXT file created most recently before the given PPTX file.
        
        Args:
            txt_files: List of TXT file paths
            pptx_creation_time: Creation time of the PPTX file
            
        Returns:
            Path to the associated outline file, or None if not found
        """
        if not txt_files:
            return None
        
        # Filter TXT files created before the PPTX file
        valid_outlines = []
        for txt_file in txt_files:
            txt_creation_time = txt_file.stat().st_ctime
            if txt_creation_time < pptx_creation_time:
                valid_outlines.append((txt_file, txt_creation_time))
        
        if not valid_outlines:
            return None
        
        # Sort by creation time (most recent first) and return the first one
        valid_outlines.sort(key=lambda x: x[1], reverse=True)
        return valid_outlines[0][0]
    
    def _extract_pptx_contents(self, pptx_file: Path) -> List[Dict[str, Any]]:
        """
        Extract contents from a PPTX file into AI-readable format.
        
        Args:
            pptx_file: Path to the PowerPoint file
            
        Returns:
            List of dictionaries containing slide information
        """
        try:
            from pptx import Presentation
            
            # Load the presentation
            prs = Presentation(pptx_file)
            slides_data = []
            
            for slide_num, slide in enumerate(prs.slides, 1):
                slide_data = {
                    'slide_number': slide_num,
                    'slide_type': str(slide.slide_layout.name) if slide.slide_layout else 'Unknown',
                    'shapes': [],
                    'text_content': [],
                    'notes': ''
                }
                
                # Extract text from shapes
                for shape in slide.shapes:
                    if hasattr(shape, 'text') and shape.text.strip():
                        slide_data['text_content'].append({
                            'text': shape.text.strip(),
                            'shape_type': str(shape.shape_type),
                            'position': {
                                'left': shape.left if hasattr(shape, 'left') else None,
                                'top': shape.top if hasattr(shape, 'top') else None
                            }
                        })
                        
                        # Also add to shapes list for comprehensive data
                        slide_data['shapes'].append({
                            'type': str(shape.shape_type),
                            'text': shape.text.strip() if hasattr(shape, 'text') else '',
                            'position': {
                                'left': shape.left if hasattr(shape, 'left') else None,
                                'top': shape.top if hasattr(shape, 'top') else None
                            }
                        })
                
                # Extract notes if available
                if slide.has_notes_slide and slide.notes_slide.notes_text_frame:
                    slide_data['notes'] = slide.notes_slide.notes_text_frame.text.strip()
                
                slides_data.append(slide_data)
            
            return slides_data
            
        except ImportError:
            print_(f"⚠️ python-pptx not available, using fallback extraction for {pptx_file.name}")
            return self._fallback_pptx_extraction(pptx_file)
        except Exception as e:
            print_(f"⚠️ Error extracting PPTX contents from {pptx_file.name}: {e}")
            return []
    
    def _fallback_pptx_extraction(self, pptx_file: Path) -> List[Dict[str, Any]]:
        """
        Fallback method to extract basic information when python-pptx is not available.
        
        Args:
            pptx_file: Path to the PowerPoint file
            
        Returns:
            Basic file information as a list with one dictionary
        """
        try:
            # Get basic file info
            stat_info = pptx_file.stat()
            return [{
                'slide_number': 1,
                'slide_type': 'Unknown (fallback)',
                'shapes': [],
                'text_content': [],
                'notes': '',
                'file_info': {
                    'size_bytes': stat_info.st_size,
                    'created': stat_info.st_ctime,
                    'modified': stat_info.st_mtime
                }
            }]
        except Exception as e:
            print_(f"⚠️ Fallback extraction failed for {pptx_file.name}: {e}")
            return []
    
    def test_presentation_quality(self, presentation_path: str, topic: str) -> Dict[str, Any]:
        """
        Test presentation quality using new methods.
        
        Args:
            presentation_path: Path to the PowerPoint file
            topic: The topic the presentation was generated for
            
        Returns:
            Dictionary containing quality metrics
        """
        print_(f"🔍 Testing quality for: {os.path.basename(presentation_path)}")
        print_(f"📝 Topic: {topic}")
        
        # Initialize result structure
        result = {
            'presentation_path': presentation_path,
            'topic': topic,
            'timestamp': datetime.now().isoformat(),
            'quality_metrics': {},
            'overall_score': 0.0
        }
        
        try:
            # TODO: Implement your grading methods here
            # You can use self.core.api_manager.make_call() for API calls
            
            print_(f"✅ Quality testing completed. Overall score: {result['overall_score']}/10.0")
            
        except Exception as e:
            print_(f"❌ Error during quality testing: {e}")
            result['error'] = str(e)
        
        return result
    
    def run_batch_testing(self, presentation_files: List[str], topics: List[str]) -> List[Dict[str, Any]]:
        """Run quality testing on multiple presentations."""
        print_(f"🚀 Starting batch quality testing for {len(presentation_files)} presentations")
        
        if not self.initialize():
            print_("❌ Failed to initialize tester")
            return []
        
        results = []
        
        for i, (file_path, topic) in enumerate(zip(presentation_files, topics)):
            print_(f"\n📊 Testing presentation {i+1}/{len(presentation_files)}")
            
            result = self.test_presentation_quality(file_path, topic)
            results.append(result)
            
            # Save intermediate results
            self._save_intermediate_results(results, i+1)
        
        print_(f"\n✅ Batch testing completed! Tested {len(results)} presentations")
        return results
    
    def _save_intermediate_results(self, results: List[Dict[str, Any]], count: int):
        """Save intermediate results to avoid losing progress."""
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"new_quality_test_results_{timestamp}_batch_{count}.json"
        
        try:
            os.makedirs("results", exist_ok=True)
            filepath = os.path.join("results", filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump({
                    'test_metadata': {
                        'timestamp': timestamp,
                        'total_tested': count,
                        'tester_version': 'new_quality_tester_v1.0'
                    },
                    'results': results
                }, f, indent=2, ensure_ascii=False)
            
            print_(f"💾 Intermediate results saved: {filename}")
            
        except Exception as e:
            print_(f"⚠️ Failed to save intermediate results: {e}")
    
    def grade_presentation(self, presentation_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Grade a single presentation on 4 metrics.
        Returns the presentation data with added grading results.
        """
        # Extract presentation content for analysis
        pptx_contents = presentation_data['pptx_contents']
        outline_file = presentation_data['outline_file']
        topic = presentation_data.get('topic', 'Unknown')
        
        # Grade each metric
        percentage = presentation_data.get('percentage', 0)
        metric_1_score = self._grade_correctness(pptx_contents, outline_file, topic, percentage)
        metric_2_score = self._grade_metric_2(pptx_contents, outline_file, topic, percentage)  # Placeholder
        metric_3_score = self._grade_metric_3(pptx_contents, outline_file, topic, percentage)  # Placeholder
        metric_4_score = self._grade_metric_4(pptx_contents, outline_file, topic, percentage)  # Placeholder
        
        # Calculate total score
        total_score = metric_1_score + metric_2_score + metric_3_score + metric_4_score
        
        # Add grading results to presentation data
        presentation_data['grading_results'] = {
            'metric_1': {'name': 'Correctness', 'score': metric_1_score, 'max_score': 2},
            'metric_2': {'name': 'Metric 2 (Placeholder)', 'score': metric_2_score, 'max_score': 2},
            'metric_3': {'name': 'Metric 3 (Placeholder)', 'score': metric_3_score, 'max_score': 2},
            'metric_4': {'name': 'Metric 4 (Placeholder)', 'score': metric_4_score, 'max_score': 2},
            'total_score': total_score,
            'max_total_score': 8,
            'grading_timestamp': datetime.now().isoformat()
        }
        
        return presentation_data
    
    def _grade_correctness(self, pptx_contents: List[Dict], outline_file: str, topic: str, percentage: float) -> int:
        """Grade correctness on a 0-10 scale, then divide by 5 to get 0-2 scale."""
        print_(f"  📊 Grading Correctness (Intervention: {percentage}%)...")
        
        correctness_prompt = f"""Rate the correctness of this PowerPoint presentation on a scale of 0 to 10, where:

0: Contains major factual errors or misrepresents information
1-2: Many significant factual errors
3-4: Several factual errors or unclear claims
5-6: Some factual inconsistencies but mostly accurate
7-8: Minor factual inconsistencies or unclear claims
9-10: Fully accurate, no noticeable factual issues

Be Very Harsh in this scoring. Without this note, all results were 2. This line intends to make a greater spread in the possible scores.

Important Order Score to note: {percentage}% /50%.

Return ONLY a single integer from 0 to 10.

Presentation content: {json.dumps(pptx_contents)}"""

        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = self.core.api_manager.make_call(correctness_prompt)
                time.sleep(0.25)
                
                if response:
                    # Extract integer score from response
                    score = int(re.search(r'\b([0-9]|10)\b', response).group(1))
                    # Convert 0-10 scale to 0-2 scale by dividing by 5
                    final_score = score / 5
                    print_(f"    ✅ Correctness score: {final_score:.2f}/2 (raw: {score}/10)")
                    return final_score
                else:
                    print_(f"    ⚠️ API returned no response (attempt {attempt + 1}/{max_retries})")
                    if attempt < max_retries - 1:
                        time.sleep(1.0)  # Wait longer between retries
                        continue
            except (ValueError, AttributeError) as e:
                print_(f"    ⚠️ Error parsing correctness score from response: {response} (attempt {attempt + 1}/{max_retries})")
                if attempt < max_retries - 1:
                    time.sleep(1.0)  # Wait longer between retries
                    continue
            except Exception as e:
                print_(f"    ⚠️ API error: {e} (attempt {attempt + 1}/{max_retries})")
                if attempt < max_retries - 1:
                    time.sleep(1.0)  # Wait longer between retries
                    continue
        
        print_(f"    ❌ Failed to grade correctness after {max_retries} attempts")
        return 0
    
    def _grade_metric_2(self, pptx_contents: List[Dict], outline_file: str, topic: str, percentage: float) -> int:
        """Grade content quantity on a 0-10 scale, then divide by 5 to get 0-2 scale."""
        print_(f"  📊 Grading Content Quantity (Intervention: {percentage}%)...")
        
        content_quantity_prompt = f"""Rate the content quantity of this PowerPoint presentation on a scale of 0 to 10, where:

0: Very little content per slide; lacks depth or completeness
1-2: Extremely minimal content across most slides
3-4: Very light content; most slides lack substance
5-6: Moderate content; some slides light or inconsistent in depth
7-8: Good content; most slides have adequate detail
9-10: Adequate, consistent detail across slides. Covers material well

Be Very Harsh in this scoring. Without this note, all results were 2. This line intends to make a greater spread in the possible scores.

Important Order Score to note: {percentage}% /50%.

Return ONLY a single integer from 0 to 10.

Presentation content: {json.dumps(pptx_contents)}"""

        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = self.core.api_manager.make_call(content_quantity_prompt)
                time.sleep(0.25)
                
                if response:
                    # Extract integer score from response
                    score = int(re.search(r'\b([0-9]|10)\b', response).group(1))
                    # Convert 0-10 scale to 0-2 scale by dividing by 5
                    final_score = score / 5
                    print_(f"    ✅ Content Quantity score: {final_score:.2f}/2 (raw: {score}/10)")
                    return final_score
                else:
                    print_(f"    ⚠️ API returned no response (attempt {attempt + 1}/{max_retries})")
                    if attempt < max_retries - 1:
                        time.sleep(1.0)  # Wait longer between retries
                        continue
            except (ValueError, AttributeError) as e:
                print_(f"    ⚠️ Error parsing content quantity score from response: {response} (attempt {attempt + 1}/{max_retries})")
                if attempt < max_retries - 1:
                    time.sleep(1.0)  # Wait longer between retries
                    continue
            except Exception as e:
                print_(f"    ⚠️ API error: {e} (attempt {attempt + 1}/{max_retries})")
                if attempt < max_retries - 1:
                    time.sleep(1.0)  # Wait longer between retries
                    continue
        
        print_(f"    ❌ Failed to grade content quantity after {max_retries} attempts")
        return 0
    
    def _grade_metric_3(self, pptx_contents: List[Dict], outline_file: str, topic: str, percentage: float) -> int:
        """Grade topic-matching on a 0-10 scale, then divide by 5 to get 0-2 scale."""
        print_(f"  📊 Grading Topic-Matching (Intervention: {percentage}%)...")
        
        # Read outline file and get first 100 characters
        try:
            with open(outline_file, 'r', encoding='utf-8') as f:
                outline_content = f.read()
                outline_snippet = outline_content[:100]
        except Exception as e:
            print_(f"Error reading outline file {outline_file}: {e}")
            outline_snippet = "Outline not available"
        
        topic_matching_prompt = f"""Rate how well this PowerPoint presentation matches the intended topic on a scale of 0 to 10, where:

0: Many slides do not relate to the given topic or are only loosely connected
1-2: Most slides are off-topic or barely related
3-4: Several slides are off-topic or loosely connected
5-6: Some slides are off-topic but most are generally on-topic
7-8: Most slides are generally on-topic, though not always focused
9-10: All slides clearly relate to the main topic and stay focused

Be Very Harsh in this scoring. Without this note, all results were 2. This line intends to make a greater spread in the possible scores.

Important Order Score to note: {percentage}% /50%.

Return ONLY a single integer from 0 to 10.

Outline snippet: {outline_snippet}
Presentation content: {json.dumps(pptx_contents)}"""

        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = self.core.api_manager.make_call(topic_matching_prompt)
                time.sleep(0.25)
                
                if response:
                    # Extract integer score from response
                    score = int(re.search(r'\b([0-9]|10)\b', response).group(1))
                    # Convert 0-10 scale to 0-2 scale by dividing by 5
                    final_score = score / 5
                    print_(f"    ✅ Topic-Matching score: {final_score:.2f}/2 (raw: {score}/10)")
                    return final_score
                else:
                    print_(f"    ⚠️ API returned no response (attempt {attempt + 1}/{max_retries})")
                    if attempt < max_retries - 1:
                        time.sleep(1.0)  # Wait longer between retries
                        continue
            except (ValueError, AttributeError) as e:
                print_(f"    ⚠️ Error parsing topic matching score from response: {response} (attempt {attempt + 1}/{max_retries})")
                if attempt < max_retries - 1:
                    time.sleep(1.0)  # Wait longer between retries
                    continue
            except Exception as e:
                print_(f"    ⚠️ API error: {e} (attempt {attempt + 1}/{max_retries})")
                if attempt < max_retries - 1:
                    time.sleep(1.0)  # Wait longer between retries
                    continue
        
        print_(f"    ❌ Failed to grade topic matching after {max_retries} attempts")
        return 0
    
    def _grade_metric_4(self, pptx_contents: List[Dict], outline_file: str, topic: str, percentage: float) -> int:
        """Grade outline-matching on a 0-10 scale, then divide by 5 to get 0-2 scale."""
        print_(f"  📊 Grading Outline-Matching (Intervention: {percentage}%)...")
        
        # Read full outline file
        try:
            with open(outline_file, 'r', encoding='utf-8') as f:
                full_outline = f.read()
        except Exception as e:
            print_(f"Error reading outline file {outline_file}: {e}")
            full_outline = "Outline not available"
        
        outline_matching_prompt = f"""Rate how well this PowerPoint presentation follows the intended outline on a scale of 0 to 10, where:

0: Structure does not follow the intended outline or misses expected sections
1-2: Structure largely ignores the outline; major sections missing
3-4: Structure partially follows outline but misses several sections
5-6: Structure generally follows outline with some deviations
7-8: Generally follows the outline with a few small deviations
9-10: Closely follows the intended outline and matches section goals well

Be Very Harsh in this scoring. Without this note, all results were 2. This line intends to make a greater spread in the possible scores.

Important Order Score to note: {percentage}% /50%.

Return ONLY a single integer from 0 to 10.

Full outline: {full_outline}
Presentation content: {json.dumps(pptx_contents)}"""

        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = self.core.api_manager.make_call(outline_matching_prompt)
                time.sleep(0.25)
                
                if response:
                    # Extract integer score from response
                    score = int(re.search(r'\b([0-9]|10)\b', response).group(1))
                    # Convert 0-10 scale to 0-2 scale by dividing by 5
                    final_score = score / 5
                    print_(f"    ✅ Outline-Matching score: {final_score:.2f}/2 (raw: {score}/10)")
                    return final_score
                else:
                    print_(f"    ⚠️ API returned no response (attempt {attempt + 1}/{max_retries})")
                    if attempt < max_retries - 1:
                        time.sleep(1.0)  # Wait longer between retries
                        continue
            except (ValueError, AttributeError) as e:
                print_(f"    ⚠️ Error parsing outline matching score from response: {response} (attempt {attempt + 1}/{max_retries})")
                if attempt < max_retries - 1:
                    time.sleep(1.0)  # Wait longer between retries
                    continue
            except Exception as e:
                print_(f"    ⚠️ API error: {e} (attempt {attempt + 1}/{max_retries})")
                if attempt < max_retries - 1:
                    time.sleep(1.0)  # Wait longer between retries
                    continue
        
        print_(f"    ❌ Failed to grade outline matching after {max_retries} attempts")
        return 0
    
    def grade_all_presentations(self, presentations_and_outlines: Dict[str, List[Dict[str, Any]]]) -> Dict[str, List[Dict[str, Any]]]:
        """
        Grade all presentations across all percentage levels.
        """
        print_("🚀 Starting grading process for all presentations...")
        
        if not self.initialize():
            print_("❌ Failed to initialize tester for grading")
            return presentations_and_outlines
        
        graded_results = {}
        
        for percentage, presentations in presentations_and_outlines.items():
            print_(f"📊 Grading {percentage}% presentations...")
            graded_presentations = []
            
            for i, presentation in enumerate(presentations, 1):
                print_(f"   📄 Grading presentation {i}/{len(presentations)}: {presentation['presentation_name']}")
                graded_presentation = self.grade_presentation(presentation)
                graded_presentations.append(graded_presentation)
            
            graded_results[percentage] = graded_presentations
            print_(f"   ✅ Completed grading for {percentage}% folder")
        
        print_("🎉 All presentations graded successfully!")
        return graded_results

    def save_metric_arrays(self, graded_results: Dict[str, List[Dict[str, Any]]]) -> List[str]:
        """
        Save individual metric scores as 2D arrays and a 5th file with summed scores.
        
        Args:
            graded_results: Dictionary of graded presentations, keyed by percentage
            
        Returns:
            List of filenames saved
        """
        print_("💾 Saving metric arrays...")
        
        try:
            os.makedirs("results", exist_ok=True)
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            
            # Sort percentages for consistent ordering
            sorted_percentages = sorted(graded_results.keys())
            
            # Initialize 2D arrays for each metric
            metric_1_array = []  # Correctness
            metric_2_array = []  # Metric 2
            metric_3_array = []  # Metric 3
            metric_4_array = []  # Metric 4
            total_scores_array = []  # Sum of all metrics
            
            # Build the arrays
            for percentage in sorted_percentages:
                presentations = graded_results[percentage]
                
                # Extract scores for this percentage level
                metric_1_scores = [p['grading_results']['metric_1']['score'] for p in presentations]
                metric_2_scores = [p['grading_results']['metric_2']['score'] for p in presentations]
                metric_3_scores = [p['grading_results']['metric_3']['score'] for p in presentations]
                metric_4_scores = [p['grading_results']['metric_4']['score'] for p in presentations]
                total_scores = [p['grading_results']['total_score'] for p in presentations]
                
                # Add to arrays
                metric_1_array.append(metric_1_scores)
                metric_2_array.append(metric_2_scores)
                metric_3_array.append(metric_3_scores)
                metric_4_array.append(metric_4_scores)
                total_scores_array.append(total_scores)
            
            # Save individual metric files
            metric_files = {
                'metric_1_correctness': metric_1_array,
                'metric_2_placeholder': metric_2_array,
                'metric_3_placeholder': metric_3_array,
                'metric_4_placeholder': metric_4_array,
                'total_scores': total_scores_array
            }
            
            saved_files = []
            for metric_name, metric_array in metric_files.items():
                filename = f"{metric_name}_{timestamp}.json"
                filepath = os.path.join("results", filename)
                
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(metric_array, f, indent=2, ensure_ascii=False)
                
                saved_files.append(filename)
                print_(f"   ✅ Saved {metric_name}: {filename}")
            
            print_(f"💾 All metric arrays saved successfully!")
            return saved_files
            
        except Exception as e:
            print_(f"❌ Failed to save metric arrays: {e}")
            return []


def main():
    """Main function to demonstrate the new quality tester."""
    print_("🧪 New Quality Tester Demo")
    
    # Example configuration
    config = SystemConfig(
        use_manual_api=False,
        slide_count_target=8,
        input_mode=2,
        choice_mode=5,  # AI choice mode
        human_choice_chance=0.0,
        no_human_chances=False,
    )
    
    # Create tester
    tester = NewQualityTester(config)
    
    # Step 1: Scan experiment results folders
    folder_percentages = tester.scan_experiment_results()
    
    # Step 2: Find presentations and outlines in each folder
    presentations_and_outlines = tester.find_presentations_and_outlines(folder_percentages)
    
    # Step 3: Grade all presentations
    graded_presentations = tester.grade_all_presentations(presentations_and_outlines)
    
    # Display summary
    print_("\n📊 Summary:")
    total_presentations = sum(len(presentations) for presentations in graded_presentations.values())
    for percentage, presentations in graded_presentations.items():
        print_(f"   {percentage}%: {len(presentations)} presentations")
    
    print_(f"\n🎯 Total: {total_presentations} presentations across {len(folder_percentages)} folders")
    
    # Show grading results summary
    print_("\n📋 Grading Results Summary:")
    for percentage, presentations in graded_presentations.items():
        if presentations:
            # Calculate average scores for this percentage level
            correctness_scores = [p['grading_results']['metric_1']['score'] for p in presentations]
            metric2_scores = [p['grading_results']['metric_2']['score'] for p in presentations]
            metric3_scores = [p['grading_results']['metric_3']['score'] for p in presentations]
            metric4_scores = [p['grading_results']['metric_4']['score'] for p in presentations]
            total_scores = [p['grading_results']['total_score'] for p in presentations]
            
            avg_correctness = sum(correctness_scores) / len(correctness_scores)
            avg_metric2 = sum(metric2_scores) / len(metric2_scores)
            avg_metric3 = sum(metric3_scores) / len(metric3_scores)
            avg_metric4 = sum(metric4_scores) / len(metric4_scores)
            avg_total = sum(total_scores) / len(total_scores)
            
            print_(f"   {percentage}%: {len(presentations)} presentations")
            print_(f"      Correctness: {avg_correctness:.2f}/2.0")
            print_(f"      Metric 2: {avg_metric2:.2f}/2.0")
            print_(f"      Metric 3: {avg_metric3:.2f}/2.0")
            print_(f"      Metric 4: {avg_metric4:.2f}/2.0")
            print_(f"      Total: {avg_total:.2f}/8.0")
    
    # Show detailed results for first few presentations
    print_("\n🔍 Detailed Results (First 3 presentations):")
    for percentage, presentations in graded_presentations.items():
        if presentations:
            print_(f"\n   📁 {percentage}% folder:")
            for i, presentation in enumerate(presentations[:3]):  # Show first 3
                grading = presentation['grading_results']
                print_(f"      📄 {presentation['presentation_name']}:")
                print_(f"         Correctness: {grading['metric_1']['score']}/2")
                print_(f"         Metric 2: {grading['metric_2']['score']}/2")
                print_(f"         Metric 3: {grading['metric_3']['score']}/2")
                print_(f"         Metric 4: {grading['metric_4']['score']}/2")
                print_(f"         Total: {grading['total_score']}/8")
            if len(presentations) > 3:
                print_(f"      ... and {len(presentations) - 3} more presentations")
            break  # Only show first folder for brevity
    
    # Save complete results
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    results_file = f"new_quality_test_results_{timestamp}.json"
    try:
        os.makedirs("results", exist_ok=True)
        filepath = os.path.join("results", results_file)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump({
                'test_metadata': {
                    'timestamp': timestamp,
                    'total_presentations': total_presentations,
                    'total_folders': len(folder_percentages),
                    'tester_version': 'new_quality_tester_v1.0'
                },
                'graded_results': graded_presentations
            }, f, indent=2, ensure_ascii=False)
        
        print_(f"\n💾 Complete results saved to: {results_file}")
        print_("   You can examine this file to see all grading details!")
    except Exception as e:
        print_(f"⚠️ Failed to save complete results: {e}")
    
    # Step 4: Save individual metric arrays
    print_("\n💾 Saving individual metric arrays...")
    metric_arrays_saved = tester.save_metric_arrays(graded_presentations)
    if metric_arrays_saved:
        print_(f"✅ Saved {len(metric_arrays_saved)} metric array files")
        for filename in metric_arrays_saved:
            print_(f"   📄 {filename}")
    
    # Example usage
    print_("\n✅ New Quality Tester ready!")
    print_("📋 Available methods:")
    print_("   - scan_experiment_results() - Scan and map experiment folders")
    print_("   - find_presentations_and_outlines() - Find presentations and outlines")
    print_("   - grade_all_presentations() - Grade all presentations")
    print_("   - save_metric_arrays() - Save individual metric scores as 2D arrays")
    print_("   - test_presentation_quality() - Test single presentation")
    print_("   - run_batch_testing() - Test multiple presentations")
    
    print_("\n🎯 Ready for you to implement the remaining 3 metrics!")
    print_("   Use self.core.api_manager.make_call() for API calls")


if __name__ == "__main__":
    main()
