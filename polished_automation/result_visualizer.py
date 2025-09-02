#!/usr/bin/env python3
"""
Result Visualizer for New Quality Tester
Imports the newest result files and creates graphs from the grading data
"""

import os
import json
import glob
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

# Import the logging function
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from logging_funcs import print_

class ResultVisualizer:
    """Visualizes results from the new quality tester."""
    
    def __init__(self):
        self.results_dir = "results"
        self.latest_results = {}
        
    def find_newest_result_files(self) -> Dict[str, str]:
        """
        Find the newest result files of each of the 5 types.
        
        Returns:
            Dictionary mapping metric names to their newest file paths
        """
        print_("🔍 Finding newest result files...")
        
        if not os.path.exists(self.results_dir):
            print_(f"❌ Results directory not found: {self.results_dir}")
            return {}
        
        # Define the 5 metric file types we're looking for
        metric_patterns = {
            'metric_1_correctness': 'metric_1_correctness_*.json',
            'metric_2_placeholder': 'metric_2_placeholder_*.json',
            'metric_3_placeholder': 'metric_3_placeholder_*.json',
            'metric_4_placeholder': 'metric_4_placeholder_*.json',
            'total_scores': 'total_scores_*.json'
        }
        
        newest_files = {}
        
        for metric_name, pattern in metric_patterns.items():
            # Find all files matching this pattern
            search_pattern = os.path.join(self.results_dir, pattern)
            matching_files = glob.glob(search_pattern)
            
            if matching_files:
                # Find the newest file based on modification time
                newest_file = max(matching_files, key=os.path.getmtime)
                newest_files[metric_name] = newest_file
                print_(f"   ✅ {metric_name}: {os.path.basename(newest_file)}")
            else:
                print_(f"   ❌ No files found for {metric_name}")
        
        self.latest_results = newest_files
        return newest_files
    
    def load_result_data(self) -> Dict[str, Any]:
        """
        Load the data from all the newest result files.
        
        Returns:
            Dictionary containing all loaded metric data
        """
        print_("\n📊 Loading result data...")
        
        if not self.latest_results:
            print_("❌ No result files found. Run find_newest_result_files() first.")
            return {}
        
        loaded_data = {}
        
        for metric_name, file_path in self.latest_results.items():
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    loaded_data[metric_name] = data
                    print_(f"   ✅ Loaded {metric_name}: {len(data)} percentage levels")
            except Exception as e:
                print_(f"   ❌ Failed to load {metric_name}: {e}")
                loaded_data[metric_name] = []
        
        return loaded_data
    
    def analyze_data_structure(self, data: Dict[str, Any]) -> None:
        """
        Analyze and display the structure of the loaded data.
        
        Args:
            data: Dictionary containing loaded metric data
        """
        print_("\n📋 Data Structure Analysis:")
        
        for metric_name, metric_data in data.items():
            if isinstance(metric_data, list):
                print_(f"   {metric_name}:")
                print_(f"     - Type: 2D Array")
                print_(f"     - Rows (percentage levels): {len(metric_data)}")
                if metric_data:
                    print_(f"     - Columns (presentations per level): {len(metric_data[0]) if metric_data[0] else 0}")
                    print_(f"     - Sample scores: {metric_data[0][:5] if metric_data[0] else 'None'}")
            else:
                print_(f"   {metric_name}: Unexpected data type - {type(metric_data)}")
    
    def prepare_for_visualization(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Prepare the data for visualization by organizing it into a structured format.
        
        Args:
            data: Dictionary containing loaded metric data
            
        Returns:
            Dictionary organized for visualization
        """
        print_("\n🎨 Preparing data for visualization...")
        
        # Define the expected percentage levels (should match the folder structure)
        expected_percentages = [0.0, 5.0, 10.0, 15.0, 20.0, 25.0, 30.0, 35.0, 40.0, 45.0, 50.0]
        
        organized_data = {
            'percentages': expected_percentages,
            'metrics': {}
        }
        
        for metric_name, metric_data in data.items():
            if isinstance(metric_data, list) and len(metric_data) == len(expected_percentages):
                organized_data['metrics'][metric_name] = metric_data
                print_(f"   ✅ {metric_name}: Data aligned with {len(expected_percentages)} percentage levels")
            else:
                print_(f"   ⚠️ {metric_name}: Data structure mismatch - expected {len(expected_percentages)} levels, got {len(metric_data) if isinstance(metric_data, list) else 'invalid'}")
        
        return organized_data
    
    def create_visualizations(self, organized_data: Dict[str, Any]) -> None:
        """
        Create graphs and visualizations from the organized data.
        
        Args:
            organized_data: Dictionary containing organized data for visualization
        """
        print_("\n📈 Creating visualizations...")
        
        try:
            import matplotlib.pyplot as plt
            import numpy as np
            
            # Create the quality score vs intervention percentage graph
            self._plot_quality_vs_intervention(organized_data)
            
        except ImportError:
            print_("   ❌ matplotlib not available. Install with: pip install matplotlib")
            print_("   📊 Ready to implement visualization methods!")
        except Exception as e:
            print_(f"   ❌ Error creating visualizations: {e}")
    
    def _plot_quality_vs_intervention(self, organized_data: Dict[str, Any]) -> None:
        """
        Create a graph plotting quality scores against percentage of human intervention.
        
        Args:
            organized_data: Dictionary containing organized data for visualization
        """
        print_("   📊 Creating Quality Score vs Intervention Percentage graph...")
        
        try:
            import matplotlib.pyplot as plt
            import numpy as np
            
            percentages = organized_data['percentages']
            metrics = organized_data['metrics']
            
            # Calculate average scores for each percentage level
            avg_scores = []
            
            # Also calculate individual metric scores for plotting
            metric_scores = {
                'Correctness': [],
                'Content Quality': [],
                'Topic': [],
                'Outline': []
            }
            
            for i, percentage in enumerate(percentages):
                # Simply average the results within each row for each metric
                correctness_scores = metrics.get('metric_1_correctness', [[]])[i] if i < len(metrics.get('metric_1_correctness', [])) else []
                content_scores = metrics.get('metric_2_placeholder', [[]])[i] if i < len(metrics.get('metric_2_placeholder', [])) else []
                topic_scores = metrics.get('metric_3_placeholder', [[]])[i] if i < len(metrics.get('metric_3_placeholder', [])) else []
                outline_scores = metrics.get('metric_4_placeholder', [[]])[i] if i < len(metrics.get('metric_4_placeholder', [])) else []
                
                # Calculate averages for each metric
                correctness_avg = np.mean(correctness_scores) if correctness_scores else 0
                content_avg = np.mean(content_scores) if content_scores else 0
                topic_avg = np.mean(topic_scores) if topic_scores else 0
                outline_avg = np.mean(outline_scores) if outline_scores else 0
                
                # Sum of all 4 metric averages
                total_avg = correctness_avg + content_avg + topic_avg + outline_avg
                
                avg_scores.append(total_avg)
                
                # Store individual metric averages
                metric_scores['Correctness'].append(correctness_avg)
                metric_scores['Content Quality'].append(content_avg)
                metric_scores['Topic'].append(topic_avg)
                metric_scores['Outline'].append(outline_avg)
            
            # Create the plot
            plt.figure(figsize=(10, 6))
            
            # Plot individual metric lines first (behind)
            plt.plot(percentages, metric_scores['Correctness'], 'r-', linewidth=1.5, alpha=0.7, label='Red: Correctness')
            plt.plot(percentages, metric_scores['Content Quality'], 'y-', linewidth=1.5, alpha=0.7, label='Yellow: Content Quality')
            plt.plot(percentages, metric_scores['Topic'], 'b-', linewidth=1.5, alpha=0.7, label='Blue: Topic')
            plt.plot(percentages, metric_scores['Outline'], 'g-', linewidth=1.5, alpha=0.7, label='Green: Outline')
            
            # Plot the average line last (in foreground)
            plt.plot(percentages, avg_scores, 'ko-', linewidth=3, markersize=8, label='Black: Average Quality Score')
            
            # Add individual presentation dots for each percentage level
            for i, percentage in enumerate(percentages):
                # Get individual scores for each metric at this percentage level
                correctness_scores = []
                content_scores = []
                topic_scores = []
                outline_scores = []
                
                for metric_name, metric_data in metrics.items():
                    if i < len(metric_data) and metric_data[i]:
                        if metric_name == 'metric_1_correctness':
                            correctness_scores = metric_data[i]
                        elif metric_name == 'metric_2_placeholder':
                            content_scores = metric_data[i]
                        elif metric_name == 'metric_3_placeholder':
                            topic_scores = metric_data[i]
                        elif metric_name == 'metric_4_placeholder':
                            outline_scores = metric_data[i]
                
                # Calculate total score for each individual presentation
                num_presentations = max(len(correctness_scores), len(content_scores), len(topic_scores), len(outline_scores))
                
                for j in range(num_presentations):
                    total_score = 0
                    if j < len(correctness_scores):
                        total_score += correctness_scores[j]
                    if j < len(content_scores):
                        total_score += content_scores[j]
                    if j < len(topic_scores):
                        total_score += topic_scores[j]
                    if j < len(outline_scores):
                        total_score += outline_scores[j]
                    
                    # Plot individual dot for this presentation
                    plt.plot(percentage, total_score, 'ko', markersize=3, alpha=0.6, markeredgecolor='white', markeredgewidth=0.5)
            
            # Customize the plot
            plt.xlabel('Percentage of Human Intervention', fontsize=12)
            plt.ylabel('Average Quality Score', fontsize=12)
            plt.title('Quality Score vs Human Intervention Percentage', fontsize=14, fontweight='bold')
            plt.grid(True, alpha=0.3)
            plt.legend()
            
            # Set y-axis scale from 0 to 8
            plt.ylim(0, 8)
            
            # Set x-axis ticks to show all percentage levels
            plt.xticks(percentages)
            
            # Add data points labels
            for i, (percentage, score) in enumerate(zip(percentages, avg_scores)):
                plt.annotate(f'{score:.2f}', (percentage, score), 
                           textcoords="offset points", xytext=(0,10), 
                           ha='center', fontsize=9)
            
            # Adjust layout and save the plot first
            plt.tight_layout()
            
            # Save the plot before showing
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            plot_filename = f"quality_vs_intervention_{timestamp}.png"
            plot_path = os.path.join(self.results_dir, plot_filename)
            plt.savefig(plot_path, dpi=300, bbox_inches='tight')
            
            # Display the plot on screen
            plt.show()
            
            # Close the plot after display
            plt.close()
            
            print_(f"   ✅ Graph saved as: {plot_filename}")
            
            # Display summary statistics
            print_("\n   📈 Summary Statistics:")
            print_(f"      - Highest quality: {max(avg_scores):.2f} at {percentages[avg_scores.index(max(avg_scores))]}% intervention")
            print_(f"      - Lowest quality: {min(avg_scores):.2f} at {percentages[avg_scores.index(min(avg_scores))]}% intervention")
            print_(f"      - Overall average: {np.mean(avg_scores):.2f}")
            print_(f"      - Score range: {max(avg_scores) - min(avg_scores):.2f}")
            
        except Exception as e:
            print_(f"   ❌ Error creating quality vs intervention plot: {e}")
    
    def run_analysis(self) -> None:
        """
        Run the complete analysis pipeline.
        """
        print_("🧪 Result Visualizer - Starting Analysis")
        print_("=" * 50)
        
        # Step 1: Find newest result files
        self.find_newest_result_files()
        
        if not self.latest_results:
            print_("❌ No result files found. Exiting.")
            return
        
        # Step 2: Load the data
        loaded_data = self.load_result_data()
        
        if not loaded_data:
            print_("❌ No data loaded. Exiting.")
            return
        
        # Step 3: Analyze data structure
        self.analyze_data_structure(loaded_data)
        
        # Step 4: Prepare for visualization
        organized_data = self.prepare_for_visualization(loaded_data)
        
        # Step 5: Create visualizations
        self.create_visualizations(organized_data)
        
        print_("\n✅ Analysis complete!")


def main():
    """Main function to run the result visualizer."""
    visualizer = ResultVisualizer()
    visualizer.run_analysis()


if __name__ == "__main__":
    main()
