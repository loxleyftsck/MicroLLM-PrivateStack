# Memory Optimization Benchmark Suite

## Overview

Standardized benchmark suite for measuring memory access patterns, cache performance, and identifying optimization opportunities in MicroLLM-PrivateStack.

## Benchmarks Available

### 1. Sequential vs Random Access (`sequential_vs_random.py`)
**Purpose:** Measure cache performance differences between access patterns

**What it tests:**
- Sequential read/write performance
- Random read/write performance  
- Strided access with different strides
- Speedup calculations

**Usage:**
```bash
# Basic run
python sequential_vs_random.py

# Custom size and iterations
python sequential_vs_random.py --size 20000000 --iterations 200

# Save as baseline
python sequential_vs_random.py --baseline

# Compare with baseline
python sequential_vs_random.py --compare results/baseline.json
```

**Expected output:**
- Sequential vs random speedup: **10x-100x faster**
- Write performance comparison
- JSON results for tracking

---

### 2. Cache Performance (`cache_performance.py`)
**Purpose:** Estimate cache levels and bandwidth utilization

**What it tests:**
- Cache level identification (L1, L2, L3)
- Stride effect on cache line utilization
- Spatial locality analysis
- Memory bandwidth estimation

**Usage:**
```bash
# Basic run
python cache_performance.py

# Test larger sizes
python cache_performance.py --max-size 128

# Custom output
python cache_performance.py --output results/my_cache_test.json
```

**Expected output:**
- Cache level thresholds (L1: <2ns/elem, L2: <10ns/elem, L3: <50ns/elem)
- Stride 1 vs Stride 16: **2-4x slowdown**
- Bandwidth: 10-50 GB/s (typical DDR4)

---

### 3. Embedding Lookup (`embedding_lookup.py`)
**Purpose:** Compare Array-of-Structs vs Struct-of-Arrays for semantic caching

**What it tests:**
- Similarity search performance (AoS vs SoA)
- Partial dimension access
- Memory layout overhead

**Usage:**
```bash
# Basic run (10K embeddings, 768 dim)
python embedding_lookup.py

# Custom configuration
python embedding_lookup.py --embeddings 50000 --dim 384 --iterations 200

# Test with different top-k
python embedding_lookup.py --top-k 20
```

**Expected output:**
- SoA vs AoS speedup: **1.5x-10x faster** for similarity search
- Memory overhead analysis
- Recommendation for MicroLLM-PrivateStack

---

## Quick Start

### Install Dependencies
```bash
pip install numpy
```

### Run All Benchmarks
```bash
# Create results directory
mkdir -p results

# Run benchmarks
python sequential_vs_random.py --baseline
python cache_performance.py
python embedding_lookup.py
```

### View Results
Results saved as JSON in `results/` directory:
- `baseline.json` - Sequential vs random baseline
- `cache_performance.json` - Cache analysis
- `embedding_benchmark.json` - Embedding storage comparison

---

## Interpreting Results

### Sequential vs Random
```json
{
  "sequential_read": {"mean_ms": 50.2},
  "random_read": {"mean_ms": 450.8},
  "speedup": {"sequential_vs_random": 8.98}
}
```
**Interpretation:** Sequential access is ~9x faster. **Optimize for sequential access!**

### Cache Performance
```json
{
  "cache_levels": [
    {"size_kb": 32, "time_per_element_ns": 1.5, "estimated_cache": "L1 cache"},
    {"size_kb": 256, "time_per_element_ns": 8.2, "estimated_cache": "L2 cache"},
    {"size_kb": 8192, "time_per_element_ns": 45.1, "estimated_cache": "L3 cache"}
  ]
}
```
**Interpretation:** Working set should fit in L2 (256KB) or L3 (8MB) cache for best performance.

### Embedding Lookup
```json
{
  "similarity_search": {
    "aos_mean_ms": 120.5,
    "soa_mean_ms": 63.2,
    "speedup_soa_vs_aos": 1.91
  }
}
```
**Interpretation:** SoA is 1.9x faster. **Use SoA for semantic caching in MicroLLM-PrivateStack!**

---

## Integration with MicroLLM-PrivateStack

### Step 1: Establish Baseline
```bash
# Run all benchmarks to establish current performance
python sequential_vs_random.py --baseline
python cache_performance.py --output results/baseline_cache.json
python embedding_lookup.py --output results/baseline_embeddings.json
```

### Step 2: Identify Bottlenecks
Review results and identify optimization opportunities:
- High random access time → Optimize for sequential
- Low cache hit rate → Reduce working set or use tiling
- Slow embedding search → Convert to SoA storage

### Step 3: Implement Optimizations
Apply optimizations from `memory_optimization_plan.md`

### Step 4: Validate Improvements
```bash
# Run benchmarks again
python sequential_vs_random.py --compare results/baseline.json
python cache_performance.py
python embedding_lookup.py
```

Expected improvements:
- Sequential access: maintain performance
- Cache hit rate: increase by 20-40%
- Embedding search: 1.5x-3x speedup with SoA

---

## Advanced Usage

### Profiling with System Tools

**Linux (perf):**
```bash
# Cache miss analysis
perf stat -e cache-references,cache-misses,dTLB-loads,dTLB-load-misses \
    python sequential_vs_random.py

# Memory bandwidth
perf stat -e uncore_imc/data_reads/,uncore_imc/data_writes/ \
    python cache_performance.py
```

**Windows (VTune):**
```powershell
# Using Intel VTune
vtune -collect memory-access-latency -app-working-dir . python embedding_lookup.py
```

### Continuous Benchmarking
```bash
# Create benchmark script
cat > run_benchmarks.sh << 'EOF'
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
mkdir -p results/$DATE
python sequential_vs_random.py --output results/$DATE/sequential.json
python cache_performance.py --output results/$DATE/cache.json
python embedding_lookup.py --output results/$DATE/embedding.json
echo "✅ Benchmarks saved to results/$DATE/"
EOF

chmod +x run_benchmarks.sh
./run_benchmarks.sh
```

---

## Benchmark Matrix

| Benchmark | What It Measures | Why It Matters | Target Metric |
|-----------|------------------|----------------|---------------|
| Sequential vs Random | Cache efficiency | Identify sequential access benefits | >5x speedup |
| Cache Performance | Cache levels, bandwidth | Understand hardware limits | >10 GB/s bandwidth |
| Embedding Lookup | AoS vs SoA | Optimize semantic cache storage | >1.5x SoA speedup |

---

## Troubleshooting

### Low Sequential Speedup (<2x)
**Possible causes:**
- Data size too small (fits in cache anyway)
- System under load
- NUMA issues on multi-socket systems

**Solution:** Increase test size, run on idle system, pin to single NUMA node

### Inconsistent Results
**Possible causes:**
- Background processes
- CPU throttling
- Automatic frequency scaling

**Solution:** 
```bash
# Linux: Disable CPU frequency scaling
echo performance | sudo tee /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor
```

### Very High Memory (>50 GB/s)
**Likely cause:** Compiler optimizations eliminating the benchmark

**Solution:** Use results to prevent optimization:
```python
result = data.sum()
print(f"Result: {result}")  # Force computation
```

---

## Next Steps

1. **Run baseline benchmarks** (this week)
2. **Add benchmarks to CI/CD** for regression detection
3. **Profile actual MicroLLM code** to find hotspots
4. **Implement optimizations** from plan
5. **Validate with benchmarks** before deployment

---

## References

- [Implementation Plan](../../.gemini/antigravity/brain/ac6bdf18-7e7d-49fb-a224-669fd762edce/memory_optimization_plan.md)
- [Sequential Access Theory](../docs/SEQUENTIAL_ACCESS_GUIDE.md) (to be created)
- Project: [MicroLLM-PrivateStack](https://github.com/loxleyftsck/MicroLLM-PrivateStack)

---

**Status:** 🚀 Ready to use  
**Maintained by:** Herald Michain Samuel Theo Ginting  
**Last Updated:** January 18, 2026
