"""
Benchmark: Cache Performance Analysis
Estimates cache hit rates and bandwidth utilization

This benchmark provides estimates for cache performance metrics.
For detailed hardware-level cache analysis, use:
- Linux: perf stat -e cache-references,cache-misses
- Windows: Intel VTune or Performance Analyzer
"""

import numpy as np
import time
import json
from typing import Dict, List

class CachePerformanceBenchmark:
    """Estimate cache performance through access pattern testing"""
    
    # Typical cache sizes (can be overridden)
    L1_SIZE = 32 * 1024      # 32 KB
    L2_SIZE = 256 * 1024     # 256 KB  
    L3_SIZE = 8 * 1024 * 1024  # 8 MB
    
    def __init__(self):
        self.results = {}
        
    def benchmark_cache_levels(self, max_size_mb=64, iterations=100):
        """Test performance at different working set sizes to identify cache levels
        
        Args:
            max_size_mb: Maximum working set size in MB
            iterations: Number of iterations per size
        """
        print(f"\nBenchmarking cache levels (up to {max_size_mb}MB)...")
        
        # Test powers of 2 from 4KB to max_size_mb
        sizes_kb = [4, 8, 16, 32, 64, 128, 256, 512, 1024, 2048, 4096, 8192, 16384, 32768, 65536]
        sizes_kb = [s for s in sizes_kb if s <= max_size_mb * 1024]
        
        results = []
        
        for size_kb in sizes_kb:
            size_bytes = size_kb * 1024
            size_elements = size_bytes // 4  # float32
            
            # Create array
            data = np.random.randn(size_elements).astype(np.float32)
            
            # Warm up
            _ = data.sum()
            
            # Benchmark
            times = []
            for _ in range(iterations):
                start = time.perf_counter()
                _ = data.sum()
                end = time.perf_counter()
                times.append(end - start)
            
            mean_time_ns = np.mean(times) * 1e9
            time_per_element_ns = mean_time_ns / size_elements
            
            results.append({
                'size_kb': size_kb,
                'size_mb': size_kb / 1024,
                'elements': size_elements,
                'mean_time_ns': mean_time_ns,
                'time_per_element_ns': time_per_element_ns,
                'estimated_cache': self._estimate_cache_level(size_kb, time_per_element_ns)
            })
            
            print(f"  {size_kb:6} KB: {time_per_element_ns:.2f} ns/element "
                  f"[{results[-1]['estimated_cache']}]")
        
        self.results['cache_levels'] = results
        return results
    
    def _estimate_cache_level(self, size_kb, time_per_element):
        """Estimate which cache level is being used based on timing"""
        # These are rough heuristics
        if time_per_element < 2.0:
            return "L1 cache"
        elif time_per_element < 10.0:
            return "L2 cache"
        elif time_per_element < 50.0:
            return "L3 cache"
        else:
            return "Main memory"
    
    def benchmark_stride_effect(self, size_mb=8, strides=[1, 2, 4, 8, 16, 32, 64], iterations=50):
        """Test cache line effects with different strides
        
        Args:
            size_mb: Array size in MB
            strides: Stride lengths to test (in elements)
            iterations: Number of iterations
        """
        print(f"\nBenchmarking stride effects ({size_mb}MB array)...")
        
        size_elements = (size_mb * 1024 * 1024) // 4
        data = np.random.randn(size_elements).astype(np.float32)
        
        results = []
        baseline_time = None
        
        for stride in strides:
            times = []
            for _ in range(iterations):
                start = time.perf_counter()
                _ = data[::stride].sum()
                end = time.perf_counter()
                times.append(end - start)
            
            mean_time_ms = np.mean(times) * 1000
            accesses = size_elements // stride
            
            if stride == 1:
                baseline_time = mean_time_ms
            
            slowdown = mean_time_ms / baseline_time if baseline_time else 1.0
            
            # Estimate cache line utilization (assuming 64-byte cache lines, 4 bytes per float)
            elements_per_cache_line = 16
            utilization = min(1.0, elements_per_cache_line / stride) if stride > 0 else 1.0
            
            results.append({
                'stride': stride,
                'stride_bytes': stride * 4,
                'mean_time_ms': mean_time_ms,
                'accesses': accesses,
                'slowdown_vs_stride1': slowdown,
                'estimated_cache_line_utilization': utilization * 100
            })
            
            print(f"  Stride {stride:3}: {mean_time_ms:.3f} ms, "
                  f"slowdown {slowdown:.2f}x, "
                  f"cache line util ~{utilization*100:.0f}%")
        
        self.results['stride_effects'] = results
        return results
    
    def analyze_spatial_locality(self, array_size=1_000_000, window_sizes=[1, 10, 100, 1000]):
        """Analyze spatial locality by measuring access time for nearby vs distant elements
        
        Args:
            array_size: Size of test array
            window_sizes: Different access window sizes to test
        """
        print(f"\nAnalyzing spatial locality (array size: {array_size:,})...")
        
        data = np.random.randn(array_size).astype(np.float32)
        results = []
        
        for window in window_sizes:
            # Generate indices with given locality window
            base_indices = np.random.randint(0, array_size - window, size=10000)
            local_indices = base_indices + np.random.randint(0, window, size=10000)
            
            # Benchmark local access
            start = time.perf_counter()
            _ = data[local_indices].sum()
            end = time.perf_counter()
            local_time_ms = (end - start) * 1000
            
            # Benchmark random access (for comparison)
            random_indices = np.random.randint(0, array_size, size=10000)
            start = time.perf_counter()
            _ = data[random_indices].sum()
            end = time.perf_counter()
            random_time_ms = (end - start) * 1000
            
            improvement = (random_time_ms - local_time_ms) / random_time_ms * 100
            
            results.append({
                'window_size': window,
                'local_access_ms': local_time_ms,
                'random_access_ms': random_time_ms,
                'locality_benefit_pct': improvement
            })
            
            print(f"  Window {window:5}: local {local_time_ms:.3f} ms vs "
                  f"random {random_time_ms:.3f} ms "
                  f"({improvement:+.1f}% benefit)")
        
        self.results['spatial_locality'] = results
        return results
    
    def estimate_bandwidth_utilization(self, size_mb=100, iterations=10):
        """Estimate memory bandwidth utilization
        
        Args:
            size_mb: Test data size in MB
            iterations: Number of iterations
        """
        print(f"\nEstimating memory bandwidth ({size_mb}MB transfers)...")
        
        size_bytes = size_mb * 1024 * 1024
        size_elements = size_bytes // 4
        
        data = np.random.randn(size_elements).astype(np.float32)
        
        # Sequential read bandwidth
        times = []
        for _ in range(iterations):
            start = time.perf_counter()
            _ = data.sum()
            end = time.perf_counter()
            times.append(end - start)
        
        mean_time_s = np.mean(times)
        bandwidth_gbps = (size_bytes / mean_time_s) / (1024**3)
        
        # Sequential write bandwidth
        write_times = []
        for _ in range(iterations):
            start = time.perf_counter()
            data[:] = 1.0
            end = time.perf_counter()
            write_times.append(end - start)
        
        write_mean_time_s = np.mean(write_times)
        write_bandwidth_gbps = (size_bytes / write_mean_time_s) / (1024**3)
        
        result = {
            'test_size_mb': size_mb,
            'sequential_read_bandwidth_gbps': bandwidth_gbps,
            'sequential_write_bandwidth_gbps': write_bandwidth_gbps,
            'read_time_ms': mean_time_s * 1000,
            'write_time_ms': write_mean_time_s * 1000
        }
        
        self.results['bandwidth'] = result
        
        print(f"  Sequential Read:  {bandwidth_gbps:.2f} GB/s")
        print(f"  Sequential Write: {write_bandwidth_gbps:.2f} GB/s")
        
        # Typical modern system: 10-50 GB/s for DDR4
        # Under 10 GB/s might indicate bottleneck
        if bandwidth_gbps < 5:
            print(f"  ⚠️  Low bandwidth detected - possible bottleneck")
        
        return result
    
    def print_summary(self):
        """Print summary of cache analysis"""
        print("\n" + "="*70)
        print("CACHE PERFORMANCE ANALYSIS SUMMARY")
        print("="*70)
        
        if 'cache_levels' in self.results:
            levels = self.results['cache_levels']
            print("\nCache Level Identification:")
            for level in levels:
                if level['size_kb'] in [32, 256, 8192]:  # Common cache sizes
                    print(f"  {level['size_kb']:6} KB: {level['time_per_element_ns']:.2f} ns/elem "
                          f"→ {level['estimated_cache']}")
        
        if 'bandwidth' in self.results:
            bw = self.results['bandwidth']
            print(f"\nMemory Bandwidth:")
            print(f"  Read:  {bw['sequential_read_bandwidth_gbps']:.2f} GB/s")
            print(f"  Write: {bw['sequential_write_bandwidth_gbps']:.2f} GB/s")
        
        if 'stride_effects' in self.results:
            stride1 = [s for s in self.results['stride_effects'] if s['stride'] == 1][0]
            stride16 = [s for s in self.results['stride_effects'] if s['stride'] == 16]
            if stride16:
                print(f"\nStride Impact:")
                print(f"  Stride  1: {stride1['mean_time_ms']:.3f} ms (100% cache line util)")
                print(f"  Stride 16: {stride16[0]['mean_time_ms']:.3f} ms "
                      f"({stride16[0]['slowdown_vs_stride1']:.2f}x slower)")
        
        print("\n" + "="*70)
    
    def save_results(self, filename='results/cache_performance.json'):
        """Save results to JSON"""
        import json
        from pathlib import Path
        
        Path(filename).parent.mkdir(parents=True, exist_ok=True)
        
        with open(filename, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        print(f"\n✅ Results saved to: {filename}")


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Cache Performance Benchmark')
    parser.add_argument('--max-size', type=int, default=64,
                       help='Maximum test size in MB (default: 64)')
    parser.add_argument('--output', type=str, default='results/cache_performance.json',
                       help='Output file')
    
    args = parser.parse_args()
    
    bench = CachePerformanceBenchmark()
    
    # Run benchmarks
    bench.benchmark_cache_levels(max_size_mb=args.max_size, iterations=100)
    bench.benchmark_stride_effect(size_mb=8, iterations=50)
    bench.analyze_spatial_locality()
    bench.estimate_bandwidth_utilization()
    
    bench.print_summary()
    bench.save_results(args.output)
    
    print("\n💡 For hardware-level cache metrics, use:")
    print("   Linux:   perf stat -e cache-references,cache-misses,dTLB-load-misses python your_script.py")
    print("   Windows: Intel VTune or Windows Performance Analyzer")


if __name__ == '__main__':
    main()
