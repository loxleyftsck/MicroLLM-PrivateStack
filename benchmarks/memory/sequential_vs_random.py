"""
Benchmark: Sequential vs Random Memory Access
Measures cache performance and latency differences between access patterns

Usage:
    python sequential_vs_random.py --size 10000000 --iterations 100
    python sequential_vs_random.py --baseline  # Save baseline results
    python sequential_vs_random.py --compare results/baseline.json
"""

import numpy as np
import time
import json
import argparse
from pathlib import Path
import sys

# Add parent directory to path for utils
sys.path.append(str(Path(__file__).parent.parent))


class MemoryAccessBenchmark:
    """Benchmark different memory access patterns"""
    
    def __init__(self, size=10_000_000, dtype=np.float32):
        """
        Args:
            size: Number of elements in array
            dtype: NumPy data type
        """
        self.size = size
        self.dtype = dtype
        self.data = None
        self.results = {}
        
    def setup(self):
        """Initialize data array"""
        print(f"Allocating {self.size:,} elements ({self.size * 4 / 1024**2:.2f} MB)")
        self.data = np.random.randn(self.size).astype(self.dtype)
        # Touch all pages to ensure allocation
        _ = self.data.sum()
        
    def benchmark_sequential_read(self, iterations=100):
        """Benchmark sequential memory reads"""
        print(f"\nRunning sequential read benchmark ({iterations} iterations)...")
        
        times = []
        for i in range(iterations):
            start = time.perf_counter()
            _ = self.data.sum()  # Sequential access
            end = time.perf_counter()
            times.append(end - start)
            
            if (i + 1) % 10 == 0:
                print(f"  Progress: {i+1}/{iterations}")
        
        result = {
            'mean_ms': np.mean(times) * 1000,
            'median_ms': np.median(times) * 1000,
            'p95_ms': np.percentile(times, 95) * 1000,
            'p99_ms': np.percentile(times, 99) * 1000,
            'std_ms': np.std(times) * 1000,
            'min_ms': np.min(times) * 1000,
            'max_ms': np.max(times) * 1000,
        }
        
        self.results['sequential_read'] = result
        return result
    
    def benchmark_random_read(self, iterations=100, access_fraction=0.1):
        """Benchmark random memory reads
        
        Args:
            iterations: Number of iterations
            access_fraction: Fraction of array to access (0.1 = 10%)
        """
        print(f"\nRunning random read benchmark ({iterations} iterations)...")
        
        # Generate random indices (same for all iterations for fairness)
        n_accesses = int(self.size * access_fraction)
        indices = np.random.randint(0, self.size, size=n_accesses)
        
        times = []
        for i in range(iterations):
            start = time.perf_counter()
            _ = self.data[indices].sum()  # Random access
            end = time.perf_counter()
            times.append(end - start)
            
            if (i + 1) % 10 == 0:
                print(f"  Progress: {i+1}/{iterations}")
        
        result = {
            'mean_ms': np.mean(times) * 1000,
            'median_ms': np.median(times) * 1000,
            'p95_ms': np.percentile(times, 95) * 1000,
            'p99_ms': np.percentile(times, 99) * 1000,
            'std_ms': np.std(times) * 1000,
            'accesses': n_accesses,
        }
        
        self.results['random_read'] = result
        return result
    
    def benchmark_strided_access(self, iterations=100, stride=8):
        """Benchmark strided memory access
        
        Args:
            iterations: Number of iterations
            stride: Stride length (bytes = stride * element_size)
        """
        print(f"\nRunning strided access benchmark (stride={stride}, {iterations} iterations)...")
        
        times = []
        for i in range(iterations):
            start = time.perf_counter()
            _ = self.data[::stride].sum()  # Strided access
            end = time.perf_counter()
            times.append(end - start)
            
            if (i + 1) % 10 == 0:
                print(f"  Progress: {i+1}/{iterations}")
        
        result = {
            'mean_ms': np.mean(times) * 1000,
            'median_ms': np.median(times) * 1000,
            'p95_ms': np.percentile(times, 95) * 1000,
            'stride': stride,
            'accesses': self.size // stride,
        }
        
        self.results[f'strided_read_stride{stride}'] = result
        return result
    
    def benchmark_write_patterns(self, iterations=50):
        """Benchmark sequential vs random writes"""
        print(f"\nRunning write pattern benchmarks ({iterations} iterations)...")
        
        # Sequential writes
        seq_times = []
        for i in range(iterations):
            start = time.perf_counter()
            self.data[:] = 1.0  # Sequential write
            end = time.perf_counter()
            seq_times.append(end - start)
        
        # Random writes
        n_writes = self.size // 10  # 10% of array
        indices = np.random.randint(0, self.size, size=n_writes)
        rand_times = []
        
        for i in range(iterations):
            start = time.perf_counter()
            self.data[indices] = 1.0  # Random write
            end = time.perf_counter()
            rand_times.append(end - start)
        
        self.results['sequential_write'] = {
            'mean_ms': np.mean(seq_times) * 1000,
            'p95_ms': np.percentile(seq_times, 95) * 1000,
        }
        
        self.results['random_write'] = {
            'mean_ms': np.mean(rand_times) * 1000,
            'p95_ms': np.percentile(rand_times, 95) * 1000,
            'writes': n_writes,
        }
        
        return self.results['sequential_write'], self.results['random_write']
    
    def calculate_speedup(self):
        """Calculate speedup of sequential over random access"""
        if 'sequential_read' in self.results and 'random_read' in self.results:
            seq_time = self.results['sequential_read']['mean_ms']
            rand_time = self.results['random_read']['mean_ms']
            speedup = rand_time / seq_time
            
            self.results['speedup'] = {
                'sequential_vs_random': round(speedup, 2),
                'description': f'Sequential is {speedup:.2f}x faster than random'
            }
    
    def print_summary(self):
        """Print benchmark results summary"""
        print("\n" + "="*70)
        print("BENCHMARK RESULTS SUMMARY")
        print("="*70)
        
        print(f"\nArray Size: {self.size:,} elements ({self.size * 4 / 1024**2:.2f} MB)")
        
        if 'sequential_read' in self.results:
            r = self.results['sequential_read']
            print(f"\nSequential Read:")
            print(f"  Mean:   {r['mean_ms']:.3f} ms")
            print(f"  Median: {r['median_ms']:.3f} ms")
            print(f"  P95:    {r['p95_ms']:.3f} ms")
            print(f"  P99:    {r['p99_ms']:.3f} ms")
        
        if 'random_read' in self.results:
            r = self.results['random_read']
            print(f"\nRandom Read ({r['accesses']:,} accesses):")
            print(f"  Mean:   {r['mean_ms']:.3f} ms")
            print(f"  Median: {r['median_ms']:.3f} ms")
            print(f"  P95:    {r['p95_ms']:.3f} ms")
        
        if 'speedup' in self.results:
            print(f"\nSpeedup: {self.results['speedup']['description']}")
        
        if 'sequential_write' in self.results:
            seq = self.results['sequential_write']
            rand = self.results['random_write']
            print(f"\nWrite Performance:")
            print(f"  Sequential: {seq['mean_ms']:.3f} ms")
            print(f"  Random:     {rand['mean_ms']:.3f} ms ({rand['writes']:,} writes)")
            print(f"  Write Speedup: {rand['mean_ms']/seq['mean_ms']:.2f}x")
        
        print("\n" + "="*70)
    
    def save_results(self, filename):
        """Save results to JSON file"""
        output_path = Path(filename)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        metadata = {
            'size': self.size,
            'dtype': str(self.dtype),
            'memory_mb': self.size * 4 / 1024**2,
        }
        
        output_data = {
            'metadata': metadata,
            'results': self.results,
        }
        
        with open(output_path, 'w') as f:
            json.dump(output_data, f, indent=2)
        
        print(f"\n✅ Results saved to: {output_path}")
        return output_path


def main():
    parser = argparse.ArgumentParser(description='Memory Access Pattern Benchmark')
    parser.add_argument('--size', type=int, default=10_000_000,
                       help='Number of elements (default: 10M)')
    parser.add_argument('--iterations', type=int, default=100,
                       help='Number of iterations (default: 100)')
    parser.add_argument('--baseline', action='store_true',
                       help='Save results as baseline')
    parser.add_argument('--compare', type=str,
                       help='Compare with baseline file')
    parser.add_argument('--output', type=str, default='results/memory_benchmark.json',
                       help='Output JSON file')
    
    args = parser.parse_args()
    
    # Run benchmark
    bench = MemoryAccessBenchmark(size=args.size)
    bench.setup()
    
    bench.benchmark_sequential_read(iterations=args.iterations)
    bench.benchmark_random_read(iterations=args.iterations)
    bench.benchmark_strided_access(iterations=args.iterations, stride=8)
    bench.benchmark_strided_access(iterations=args.iterations, stride=16)
    bench.benchmark_write_patterns(iterations=args.iterations // 2)
    
    bench.calculate_speedup()
    bench.print_summary()
    
    # Save results
    if args.baseline:
        output_file = 'results/baseline.json'
    else:
        output_file = args.output
    
    bench.save_results(output_file)
    
    # Compare with baseline if requested
    if args.compare:
        compare_with_baseline(bench.results, args.compare)


def compare_with_baseline(current_results, baseline_path):
    """Compare current results with baseline"""
    try:
        with open(baseline_path, 'r') as f:
            baseline_data = json.load(f)
        baseline = baseline_data['results']
        
        print("\n" + "="*70)
        print("COMPARISON WITH BASELINE")
        print("="*70)
        
        metrics = ['sequential_read', 'random_read']
        for metric in metrics:
            if metric in current_results and metric in baseline:
                current = current_results[metric]['mean_ms']
                base = baseline[metric]['mean_ms']
                improvement = ((base - current) / base) * 100
                
                print(f"\n{metric.replace('_', ' ').title()}:")
                print(f"  Baseline: {base:.3f} ms")
                print(f"  Current:  {current:.3f} ms")
                if improvement > 0:
                    print(f"  ✅ Improvement: {improvement:.1f}% faster")
                else:
                    print(f"  ⚠️  Regression: {abs(improvement):.1f}% slower")
        
        print("\n" + "="*70)
        
    except FileNotFoundError:
        print(f"❌ Baseline file not found: {baseline_path}")
    except Exception as e:
        print(f"❌ Error comparing with baseline: {e}")


if __name__ == '__main__':
    main()
