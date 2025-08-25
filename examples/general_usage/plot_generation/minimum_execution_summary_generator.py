#!/usr/bin/env python3
"""
Simplified Minimum Execution Summary Table Generator

Generates CSV first, then displays table from CSV data.
Much simpler approach with storage-first methodology.

Usage: python minimum_execution_summary_generator.py
"""

import json
import csv
import pandas as pd
from pathlib import Path

class ExecutionSummaryGenerator:
    """Ultra-simplified class - CSV first, then table display."""
    
    def __init__(self):
        self.examples = ['titanic', 'pi', 'ml', 'video']
        self.script_dir = Path(__file__).parent
        self.analysis_dir = self.script_dir / "analysis_results"
        self.csv_path = self.script_dir / "execution_summary.csv"
        
    def extract_data_from_json(self, json_file_path):
        """Extract data from JSON file."""
        try:
            with open(json_file_path, 'r') as f:
                data = json.load(f)
            
            results = []
            
            # Handle profiling_data format
            if 'profiling_data' in data:
                for entry in data['profiling_data']:
                    title = entry.get('title')
                    memory = entry.get('memory')
                    
                    # Parse memory
                    if isinstance(memory, str) and memory.endswith('Mb'):
                        memory = int(memory[:-2])
                    
                    # Get workers from configuration
                    config = entry.get('configuration', '')
                    workers = None
                    if config and config.startswith('(') and config.endswith(')'):
                        parts = config[1:-1].split(', ')
                        if len(parts) >= 3:
                            workers = int(parts[2])
                    
                    # Get metrics
                    metrics = entry.get('profiling_metrics', {})
                    total_executions = None
                    avg_compute_time = None
                    total_energy_tdp = None
                    aws_cost = None
                    
                    # Get total executions
                    for metric_key in ['read', 'compute', 'write']:
                        if metric_key in metrics and metrics[metric_key]:
                            total_executions = len(metrics[metric_key])
                            break
                    
                    # Get compute time
                    if 'compute' in metrics and metrics['compute']:
                        compute_times = [t for t in metrics['compute'] if t is not None]
                        if compute_times:
                            avg_compute_time = sum(compute_times) / len(compute_times)
                    
                    # Get energy
                    if 'energy_tdp' in metrics and metrics['energy_tdp']:
                        energy_values = [e for e in metrics['energy_tdp'] if e is not None]
                        if energy_values:
                            total_energy_tdp = sum(energy_values)
                    
                    # Get cost
                    if 'cost_aws_moneywise' in metrics and metrics['cost_aws_moneywise']:
                        cost_values = [c for c in metrics['cost_aws_moneywise'] if c is not None]
                        if cost_values:
                            aws_cost = sum(cost_values)
                    
                    results.append({
                        'title': title,
                        'memory': memory,
                        'workers': workers,
                        'total_executions': total_executions,
                        'avg_compute_time': avg_compute_time,
                        'total_energy_tdp': total_energy_tdp,
                        'aws_cost': aws_cost
                    })
            
            # Handle analysis_results format
            elif 'analysis_results' in data:
                for result in data['analysis_results']:
                    avg_compute_time = (result.get('avg_compute') or 
                                      result.get('avg_compute_time') or 
                                      result.get('compute_time') or 
                                      result.get('average_compute_time'))
                    
                    results.append({
                        'memory': result.get('memory'),
                        'workers': result.get('workers'),
                        'total_executions': result.get('total_executions'),
                        'avg_compute_time': avg_compute_time,
                        'total_energy_tdp': result.get('total_tdp'),
                        'aws_cost': result.get('cost_aws_moneywise')
                    })
            
            return results
                
        except Exception as e:
            print(f"Error reading {json_file_path}: {e}")
            return []

    def parse_filename(self, filename):
        """Parse filename to extract metadata."""
        parts = filename.split('_')
        
        result = {
            'example': parts[0] if len(parts) > 0 else None,
            'architecture': None,
            'memory': None,
            'stage': 'stage'  # default
        }
        
        # Look for architecture, memory, and stage in parts
        for part in parts:
            part_lower = part.lower()
            if part_lower in ['arm', 'x86']:
                result['architecture'] = 'ARM' if part_lower == 'arm' else 'x86'
            elif 'mb' in part_lower:
                import re
                match = re.search(r'(\d+)', part)
                if match:
                    result['memory'] = int(match.group(1))
            elif part_lower.startswith('stage'):
                # Extract stage names like "stage", "stage0", "stage1", etc.
                result['stage'] = part_lower
        
        return result

    def generate_csv(self):
        """Generate CSV file first."""
        print("📊 STEP 1: GENERATING CSV...")
        
        if not self.analysis_dir.exists():
            print(f"❌ Analysis directory not found: {self.analysis_dir}")
            return False
        
        # Prepare CSV data
        csv_data = []
        
        json_files = list(self.analysis_dir.glob("*.json"))
        if not json_files:
            print("❌ No JSON files found")
            return False
        
        for json_file in json_files:
            file_name = json_file.stem.replace('_analysis', '')
            data = self.extract_data_from_json(json_file)
            
            for item in data:
                # Get values
                memory = item.get('memory')
                workers = item.get('workers')
                total_executions = item.get('total_executions')
                avg_compute_time = item.get('avg_compute_time')
                total_energy_tdp = item.get('total_energy_tdp')
                aws_cost = item.get('aws_cost')
                
                # Skip if essential data is missing
                if not all([memory is not None, workers is not None, 
                           total_executions is not None, avg_compute_time is not None]):
                    continue
                
                # Parse metadata
                title = item.get('title', file_name)
                parsed = self.parse_filename(title)
                
                example = parsed['example']
                architecture = parsed['architecture']
                parsed_memory = parsed['memory']
                stage = parsed.get('stage', 'stage')
                
                # Use parsed memory if available
                if parsed_memory is not None:
                    memory = parsed_memory
                
                # Skip if we don't have required info
                if not example or not architecture or example not in self.examples:
                    continue
                
                # Add to CSV data
                csv_data.append({
                    'Architecture': architecture,
                    'Memory_MB': memory,
                    'Workers': workers,
                    'Stage': stage,
                    'Example': example,
                    'Executions': total_executions,
                    'Compute_Time_s': avg_compute_time,
                    'Energy_J': total_energy_tdp,
                    'Cost_dollars': aws_cost
                })
        
        # Write CSV
        if csv_data:
            df = pd.DataFrame(csv_data)
            df.to_csv(self.csv_path, index=False)
            print(f"✅ Generated CSV with {len(csv_data)} rows: {self.csv_path}")
            return True
        else:
            print("❌ No data to write to CSV")
            return False

    def display_table_from_csv(self):
        """Display table by reading from CSV with adaptive column widths."""
        print("\n📊 STEP 2: DISPLAYING TABLE FROM CSV...")
        
        if not self.csv_path.exists():
            print("❌ CSV file not found")
            return False
        
        # Read CSV
        df = pd.read_csv(self.csv_path)
        
        # Pivot data for table display
        pivot_data = {}
        
        for _, row in df.iterrows():
            key = (row['Architecture'], row['Memory_MB'], row['Workers'], row['Stage'])
            example = row['Example']
            
            if key not in pivot_data:
                pivot_data[key] = {}
            
            pivot_data[key][example] = {
                'executions': row['Executions'],
                'compute_time': row['Compute_Time_s'],
                'energy': row['Energy_J'] if pd.notna(row['Energy_J']) else None,
                'cost': row['Cost_dollars'] if pd.notna(row['Cost_dollars']) else None
            }
        
        # Sort keys
        sorted_keys = sorted(pivot_data.keys(), 
                           key=lambda x: (x[0] or '', x[1] or 0, x[2] or 0, x[3] or ''))
        
        # Calculate adaptive column widths
        col_widths = self._calculate_adaptive_widths(sorted_keys, pivot_data)
        
        # Print table
        print("\n# Execution Summary")
        print("Executions, compute time (s), energy (J), cost ($) by architecture/memory/workers/stage\n")
        
        # Print header with adaptive widths
        self._print_adaptive_header(col_widths)
        self._print_adaptive_separator(col_widths)
        
        # Print data rows with adaptive widths
        for arch, memory, workers, stage in sorted_keys:
            self._print_adaptive_data_row(arch, memory, workers, stage, pivot_data, col_widths)
        
        print(f"\n✅ Displayed {len(sorted_keys)} configurations from CSV")
        return True

    def _calculate_adaptive_widths(self, sorted_keys, pivot_data):
        """Calculate adaptive column widths based on actual data."""
        # Initialize with header widths
        col_widths = {
            'arch': len('Arch'),
            'memory': len('Memory'),
            'workers': len('Workers'),
            'stage': len('Stage')
        }
        
        # Initialize example column widths
        for example in self.examples:
            col_widths[f'{example}_ex'] = len(f'{example}-ex')
            col_widths[f'{example}_sec'] = len(f'{example}-sec')
            col_widths[f'{example}_j'] = len(f'{example}-J')
            col_widths[f'{example}_cost'] = len(f'{example}-$')
        
        # Check all data to find maximum widths
        for arch, memory, workers, stage in sorted_keys:
            # Update basic column widths
            col_widths['arch'] = max(col_widths['arch'], len(str(arch)) if arch else 0)
            col_widths['memory'] = max(col_widths['memory'], len(str(memory)) if memory else 0)
            col_widths['workers'] = max(col_widths['workers'], len(str(workers)) if workers else 0)
            col_widths['stage'] = max(col_widths['stage'], len(str(stage)) if stage else 0)
            
            # Update example column widths
            for example in self.examples:
                if example in pivot_data[(arch, memory, workers, stage)]:
                    data = pivot_data[(arch, memory, workers, stage)][example]
                    
                    # Executions column
                    exec_str = str(data['executions']) if data['executions'] is not None else ''
                    col_widths[f'{example}_ex'] = max(col_widths[f'{example}_ex'], len(exec_str))
                    
                    # Time column
                    time_str = f"{data['compute_time']:.2f}" if data['compute_time'] is not None else ''
                    col_widths[f'{example}_sec'] = max(col_widths[f'{example}_sec'], len(time_str))
                    
                    # Energy column
                    energy_str = f"{data['energy']:.2f}" if data['energy'] is not None else ''
                    col_widths[f'{example}_j'] = max(col_widths[f'{example}_j'], len(energy_str))
                    
                    # Cost column
                    cost_str = f"{data['cost']:.2f}" if data['cost'] is not None else ''
                    col_widths[f'{example}_cost'] = max(col_widths[f'{example}_cost'], len(cost_str))
        
        return col_widths

    def _print_adaptive_header(self, col_widths):
        """Print header with adaptive column widths."""
        header_parts = [
            f"{'Arch':^{col_widths['arch']}}",
            f"{'Memory':^{col_widths['memory']}}",
            f"{'Workers':^{col_widths['workers']}}",
            f"{'Stage':^{col_widths['stage']}}"
        ]
        
        for example in self.examples:
            header_parts.extend([
                f"{example}-ex".center(col_widths[f'{example}_ex']),
                f"{example}-sec".center(col_widths[f'{example}_sec']),
                f"{example}-J".center(col_widths[f'{example}_j']),
                f"{example}-$".center(col_widths[f'{example}_cost'])
            ])
        
        print("| " + " | ".join(header_parts) + " |")

    def _print_adaptive_separator(self, col_widths):
        """Print separator with adaptive column widths."""
        separator_parts = [
            "-" * col_widths['arch'],
            "-" * col_widths['memory'],
            "-" * col_widths['workers'],
            "-" * col_widths['stage']
        ]
        
        for example in self.examples:
            separator_parts.extend([
                "-" * col_widths[f'{example}_ex'],
                "-" * col_widths[f'{example}_sec'],
                "-" * col_widths[f'{example}_j'],
                "-" * col_widths[f'{example}_cost']
            ])
        
        print("|-" + "-|-".join(separator_parts) + "-|")

    def _print_adaptive_data_row(self, arch, memory, workers, stage, pivot_data, col_widths):
        """Print data row with adaptive column widths."""
        row_parts = [
            f"{str(arch) if arch else '':^{col_widths['arch']}}",
            f"{str(memory) if memory else '':^{col_widths['memory']}}",
            f"{str(workers) if workers else '':^{col_widths['workers']}}",
            f"{str(stage) if stage else '':^{col_widths['stage']}}"
        ]
        
        for example in self.examples:
            if example in pivot_data[(arch, memory, workers, stage)]:
                data = pivot_data[(arch, memory, workers, stage)][example]
                
                exec_str = str(data['executions']) if data['executions'] is not None else ''
                time_str = f"{data['compute_time']:.2f}" if data['compute_time'] is not None else ''
                energy_str = f"{data['energy']:.2f}" if data['energy'] is not None else ''
                cost_str = f"{data['cost']:.2f}" if data['cost'] is not None else ''
                
                row_parts.extend([
                    f"{exec_str:^{col_widths[f'{example}_ex']}}",
                    f"{time_str:^{col_widths[f'{example}_sec']}}",
                    f"{energy_str:^{col_widths[f'{example}_j']}}",
                    f"{cost_str:^{col_widths[f'{example}_cost']}}"
                ])
            else:
                row_parts.extend([
                    f"{'':^{col_widths[f'{example}_ex']}}",
                    f"{'':^{col_widths[f'{example}_sec']}}",
                    f"{'':^{col_widths[f'{example}_j']}}",
                    f"{'':^{col_widths[f'{example}_cost']}}"
                ])
        
        print("| " + " | ".join(row_parts) + " |")

    def run(self):
        """Main execution method."""
        print("=" * 50)
        print(" SIMPLIFIED EXECUTION SUMMARY GENERATOR")
        print("=" * 50)
        
        # Step 1: Generate CSV
        if not self.generate_csv():
            return False
        
        # Step 2: Display table from CSV
        if not self.display_table_from_csv():
            return False
        
        print("\n✅ COMPLETED SUCCESSFULLY")
        return True


def main():
    """Main function."""
    generator = ExecutionSummaryGenerator()
    return generator.run()


if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)
