#!/usr/bin/env python3
"""
Complete Energy Analysis Pipeline
=================================

This script orchestrates the complete energy analysis pipeline for Monte Carlo Pi
and video processing workloads, running all analysis and visualization scripts
in the correct order.

Author: Energy Analysis Suite
Date: 2025
"""

import os
import sys
import subprocess
import time
from pathlib import Path
from datetime import datetime
from cleanup_directories import cleanup_output_directories

class EnergyAnalysisPipeline:
    """Main pipeline orchestrator for energy analysis."""
    
    def __init__(self):
        self.script_dir = Path(__file__).parent
        self.start_time = datetime.now()
        self.completed_steps = []
        self.failed_steps = []
        
        # Define all output directories that should be cleaned
        self.output_directories = [
            '100_local_analyze_universal_profiling',
            '101_local_generate_local_hypothesis_2_plots',
            '102_local_generate_local_hypothesis_3_plots',
            '103_local_generate_universal_ebpf_energy_plots',
            '104_local_generate_universal_perf_energy_plots',
            '105_local_generate_universal_rapl_energy_plots',
            '106_local_generate_universal_tdp_energy_plots',
            '107_local_multistage_stacked_graphs_universal'
        ]
 
    def print_step(self, step_num, total_steps, description):
        """Print current step information."""
        print(f"📊 Step {step_num}/{total_steps}: {description}")
        print("-" * 80)
    
    def run_script(self, script_name, description, args=None):
        """Run a Python script and handle errors."""
        script_path = self.script_dir / script_name
        
        if not script_path.exists():
            print(f"❌ Script not found: {script_path}")
            self.failed_steps.append(f"{script_name} - Script not found")
            return False
        
        try:
            print(f"🔄 Running: {script_name}")
            
            # Prepare command
            cmd = [sys.executable, str(script_path)]
            if args:
                cmd.extend(args)
            
            # Run the script
            result = subprocess.run(
                cmd,
                cwd=self.script_dir,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            if result.returncode == 0:
                print(f"✅ {description} - Completed successfully")
                self.completed_steps.append(script_name)
                
                # Print key output lines (last few lines usually contain summary)
                if result.stdout:
                    output_lines = result.stdout.strip().split('\n')
                    if len(output_lines) > 3:
                        print("📋 Key outputs:")
                        for line in output_lines[-3:]:
                            if line.strip() and ('✅' in line or '✓' in line or 'complete' in line.lower()):
                                print(f"   {line.strip()}")
                
                print()
                return True
            else:
                print(f"❌ {description} - Failed with return code {result.returncode}")
                if result.stderr:
                    print(f"Error: {result.stderr.strip()}")
                self.failed_steps.append(f"{script_name} - Return code {result.returncode}")
                print()
                return False
                
        except subprocess.TimeoutExpired:
            print(f"⏰ {description} - Timed out after 5 minutes")
            self.failed_steps.append(f"{script_name} - Timeout")
            print()
            return False
        except Exception as e:
            print(f"❌ {description} - Exception: {e}")
            self.failed_steps.append(f"{script_name} - Exception: {e}")
            print()
            return False
    
    def run_pipeline(self):

        
        # Clean up output directories first
        cleanup_output_directories(self.script_dir, self.output_directories)
        
        # Define all pipeline steps
        pipeline_steps = [
            # Step 1: Universal profiling analysis (generates data for all other scripts)
            {
                'script': '100_local_analyze_universal_profiling.py',
                'description': 'Universal Profiling Analysis (All Examples & Workers)',
                'args': None
            },
            # Step 2-5: Universal energy plots (support both Pi and Video)
            {
                'script': '103_local_generate_universal_ebpf_energy_plots.py',
                'description': 'Universal eBPF Energy Plots (Pi + Video)',
                'args': None
            },
            {
                'script': '104_local_generate_universal_perf_energy_plots.py',
                'description': 'Universal Perf Energy Plots (Pi + Video)',
                'args': None
            },
            {
                'script': '105_local_generate_universal_rapl_energy_plots.py',
                'description': 'Universal RAPL Energy Plots (Pi + Video)',
                'args': None
            },
            {
                'script': '106_local_generate_universal_tdp_energy_plots.py',
                'description': 'Universal TDP Energy Plots (Pi + Video)',
                'args': None
            },
            # Step 6-7: Hypothesis analysis plots
            {
                'script': '101_local_generate_local_hypothesis_2_plots.py',
                'description': 'Local Hypothesis 2 Analysis Plots',
                'args': None
            },
            {
                'script': '102_local_generate_local_hypothesis_3_plots.py',
                'description': 'Local Hypothesis 3 Analysis Plots',
                'args': None
            },
            # Step 8: Universal multistage stacked graphs
            {
                'script': '107_local_multistage_stacked_graphs_universal.py',
                'description': 'Universal Multi-stage Stacked Graphs (Pi + Video)',
                'args': None
            }
        ]
        
        total_steps = len(pipeline_steps)
        
        # Run each step
        for i, step in enumerate(pipeline_steps, 1):
            self.print_step(i, total_steps, step['description'])
            
            success = self.run_script(
                step['script'],
                step['description'],
                step['args']
            )
            
            if not success:
                print(f"⚠️  Step {i} failed, but continuing with remaining steps...")
                print()
        
        # Print final summary
        self.print_summary()
    
    def print_summary(self):
        """Print pipeline execution summary."""
        end_time = datetime.now()
        duration = end_time - self.start_time
        
        print("=" * 100)
        print("📊 PIPELINE EXECUTION SUMMARY")
        print("=" * 100)
        print(f"⏱️  Total Duration: {duration}")
        print(f"✅ Completed Steps: {len(self.completed_steps)}")
        print(f"❌ Failed Steps: {len(self.failed_steps)}")
        print()
        
        if self.completed_steps:
            print("✅ Successfully Completed:")
            for step in self.completed_steps:
                print(f"   ✓ {step}")
            print()
        
        if self.failed_steps:
            print("❌ Failed Steps:")
            for step in self.failed_steps:
                print(f"   ✗ {step}")
            print()
        
        # Overall status
        success_rate = len(self.completed_steps) / (len(self.completed_steps) + len(self.failed_steps)) * 100
        
        if success_rate == 100:
            print("🎉 PIPELINE COMPLETED SUCCESSFULLY!")
            print("All energy analysis and visualization scripts executed without errors.")
        elif success_rate >= 80:
            print("✅ PIPELINE MOSTLY SUCCESSFUL!")
            print(f"Success rate: {success_rate:.1f}% - Most analysis completed successfully.")
        else:
            print("⚠️  PIPELINE COMPLETED WITH ISSUES")
            print(f"Success rate: {success_rate:.1f}% - Several steps failed, please review errors.")
        

def main():
    """Main function to run the complete energy analysis pipeline."""
    try:
        pipeline = EnergyAnalysisPipeline()
        pipeline.run_pipeline()
    except KeyboardInterrupt:
        print("\n⚠️  Pipeline interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Pipeline failed with exception: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
