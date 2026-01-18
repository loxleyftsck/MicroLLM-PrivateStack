"""
Benchmark: Embedding Lookup Patterns
Tests Array-of-Structs (AoS) vs Struct-of-Arrays (SoA) for semantic caching

This benchmark is specifically designed for MicroLLM-PrivateStack's
semantic caching use case with 768-dimensional embeddings.
"""

import numpy as np
import time
import json
from dataclasses import dataclass
from typing import List, Tuple

@dataclass
class EmbeddingAoS:
    """Array of Structs: Each embedding is a complete object"""
    vector: np.ndarray  # shape: (768,)
    metadata_id: int
    
class EmbeddingStorageAoS:
    """Traditional embedding storage: list of embedding objects"""
    
    def __init__(self, n_embeddings=10000, dim=768):
        self.embeddings: List[EmbeddingAoS] = []
        self.dim = dim
        
        # Initialize with random embeddings
        for i in range(n_embeddings):
            emb = EmbeddingAoS(
                vector=np.random.randn(dim).astype(np.float32),
                metadata_id=i
            )
            self.embeddings.append(emb)
    
    def similarity_search(self, query: np.ndarray, top_k=10) -> List[Tuple[int, float]]:
        """Find top-k most similar embeddings (sequential scan)"""
        similarities = []
        
        for emb in self.embeddings:
            # Cosine similarity
            sim = np.dot(query, emb.vector) / (np.linalg.norm(query) * np.linalg.norm(emb.vector))
            similarities.append((emb.metadata_id, sim))
        
        # Sort and return top-k
        similarities.sort(key=lambda x: x[1], reverse=True)
        return similarities[:top_k]
    
    def partial_dimension_access(self, start_dim=0, end_dim=100):
        """Access only specific dimensions (common in dimension reduction)"""
        result = 0.0
        for emb in self.embeddings:
            result += emb.vector[start_dim:end_dim].sum()
        return result


class EmbeddingStorageSOA:
    """Struct of Arrays: Each dimension stored separately"""
    
    def __init__(self, n_embeddings=10000, dim=768):
        self.n_embeddings = n_embeddings
        self.dim = dim
        
        # Each dimension is stored as a separate array
        self.dimensions = np.random.randn(dim, n_embeddings).astype(np.float32)
        self.metadata_ids = np.arange(n_embeddings, dtype=np.int32)
    
    def similarity_search(self, query: np.ndarray, top_k=10) -> List[Tuple[int, float]]:
        """Find top-k most similar embeddings (vectorized)"""
        # Vectorized cosine similarity
        dots = np.dot(self.dimensions.T, query)
        
        # Norms
        embedding_norms = np.linalg.norm(self.dimensions, axis=0)
        query_norm = np.linalg.norm(query)
        
        similarities = dots / (embedding_norms * query_norm)
        
        # Top-k
        top_indices = np.argpartition(similarities, -top_k)[-top_k:]
        top_indices = top_indices[np.argsort(similarities[top_indices])][::-1]
        
        return [(int(self.metadata_ids[i]), float(similarities[i])) for i in top_indices]
    
    def partial_dimension_access(self, start_dim=0, end_dim=100):
        """Access only specific dimensions"""
        # Much faster: just access relevant dimension arrays
        return self.dimensions[start_dim:end_dim, :].sum()


class EmbeddingBenchmark:
    """Benchmark embedding storage strategies"""
    
    def __init__(self, n_embeddings=10000, dim=768):
        print(f"Initializing embedding storage ({n_embeddings:,} embeddings, {dim} dimensions)...")
        
        self.aos = EmbeddingStorageAoS(n_embeddings, dim)
        self.soa = EmbeddingStorageSOA(n_embeddings, dim)
        
        self.query = np.random.randn(dim).astype(np.float32)
        self.results = {}
    
    def benchmark_similarity_search(self, iterations=100, top_k=10):
        """Benchmark similarity search performance"""
        print(f"\nBenchmarking similarity search (top_k={top_k}, {iterations} iterations)...")
        
        # AoS (Array of Structs)
        aos_times = []
        for i in range(iterations):
            start = time.perf_counter()
            _ = self.aos.similarity_search(self.query, top_k)
            end = time.perf_counter()
            aos_times.append(end - start)
            
            if (i + 1) % 10 == 0:
                print(f"  AoS progress: {i+1}/{iterations}")
        
        # SoA (Struct of Arrays)
        soa_times = []
        for i in range(iterations):
            start = time.perf_counter()
            _ = self.soa.similarity_search(self.query, top_k)
            end = time.perf_counter()
            soa_times.append(end - start)
            
            if (i + 1) % 10 == 0:
                print(f"  SoA progress: {i+1}/{iterations}")
        
        aos_mean_ms = np.mean(aos_times) * 1000
        soa_mean_ms = np.mean(soa_times) * 1000
        speedup = aos_mean_ms / soa_mean_ms
        
        result = {
            'aos_mean_ms': aos_mean_ms,
            'aos_p95_ms': np.percentile(aos_times, 95) * 1000,
            'soa_mean_ms': soa_mean_ms,
            'soa_p95_ms': np.percentile(soa_times, 95) * 1000,
            'speedup_soa_vs_aos': speedup,
            'top_k': top_k
        }
        
        self.results['similarity_search'] = result
        
        print(f"  AoS: {aos_mean_ms:.3f} ms")
        print(f"  SoA: {soa_mean_ms:.3f} ms")
        print(f"  ✅ SoA is {speedup:.2f}x faster")
        
        return result
    
    def benchmark_partial_access(self, iterations=100):
        """Benchmark accessing subset of dimensions"""
        print(f"\nBenchmarking partial dimension access ({iterations} iterations)...")
        
        # AoS
        aos_times = []
        for _ in range(iterations):
            start = time.perf_counter()
            _ = self.aos.partial_dimension_access(start_dim=0, end_dim=100)
            end = time.perf_counter()
            aos_times.append(end - start)
        
        # SoA
        soa_times = []
        for _ in range(iterations):
            start = time.perf_counter()
            _ = self.soa.partial_dimension_access(start_dim=0, end_dim=100)
            end = time.perf_counter()
            soa_times.append(end - start)
        
        aos_mean_ms = np.mean(aos_times) * 1000
        soa_mean_ms = np.mean(soa_times) * 1000
        speedup = aos_mean_ms / soa_mean_ms
        
        result = {
            'aos_mean_ms': aos_mean_ms,
            'soa_mean_ms': soa_mean_ms,
            'speedup_soa_vs_aos': speedup
        }
        
        self.results['partial_dimension_access'] = result
        
        print(f"  AoS: {aos_mean_ms:.3f} ms")
        print(f"  SoA: {soa_mean_ms:.3f} ms")
        print(f"  ✅ SoA is {speedup:.2f}x faster for partial access")
        
        return result
    
    def benchmark_memory_layout(self):
        """Analyze memory layout overhead"""
        import sys
        
        print("\nAnalyzing memory overhead...")
        
        # AoS memory (estimate)
        aos_memory_mb = (len(self.aos.embeddings) * sys.getsizeof(self.aos.embeddings[0])) / (1024**2)
        
        # SoA memory
        soa_memory_mb = (self.soa.dimensions.nbytes + self.soa.metadata_ids.nbytes) / (1024**2)
        
        result = {
            'aos_memory_mb': aos_memory_mb,
            'soa_memory_mb': soa_memory_mb,
            'memory_overhead_pct': (aos_memory_mb - soa_memory_mb) / soa_memory_mb * 100
        }
        
        self.results['memory'] = result
        
        print(f"  AoS: {aos_memory_mb:.2f} MB")
        print(f"  SoA: {soa_memory_mb:.2f} MB")
        print(f"  Memory overhead: {result['memory_overhead_pct']:.1f}%")
        
        return result
    
    def print_summary(self):
        """Print benchmark summary"""
        print("\n" + "="*70)
        print("EMBEDDING STORAGE BENCHMARK SUMMARY")
        print("="*70)
        
        if 'similarity_search' in self.results:
            r = self.results['similarity_search']
            print(f"\nSimilarity Search (Top-{r['top_k']}):")
            print(f"  AoS: {r['aos_mean_ms']:.3f} ms")
            print(f"  SoA: {r['soa_mean_ms']:.3f} ms")
            print(f"  → SoA is {r['speedup_soa_vs_aos']:.2f}x faster ✅")
        
        if 'partial_dimension_access' in self.results:
            r = self.results['partial_dimension_access']
            print(f"\nPartial Dimension Access:")
            print(f"  AoS: {r['aos_mean_ms']:.3f} ms")
            print(f"  SoA: {r['soa_mean_ms']:.3f} ms")
            print(f"  → SoA is {r['speedup_soa_vs_aos']:.2f}x faster ✅")
        
        print("\n💡 Recommendation:")
        if 'similarity_search' in self.results:
            speedup = self.results['similarity_search']['speedup_soa_vs_aos']
            if speedup > 1.5:
                print(f"  ✅ USE SoA for semantic caching: {speedup:.1f}x speedup!")
            else:
                print(f"  ⚠️  Marginal benefit. Consider code complexity trade-off.")
        
        print("\n" + "="*70)
    
    def save_results(self, filename='results/embedding_benchmark.json'):
        """Save results to JSON"""
        from pathlib import Path
        
        Path(filename).parent.mkdir(parents=True, exist_ok=True)
        
        metadata = {
            'n_embeddings': len(self.aos.embeddings),
            'dimension': self.aos.dim
        }
        
        output_data = {
            'metadata': metadata,
            'results': self.results
        }
        
        with open(filename, 'w') as f:
            json.dump(output_data, f, indent=2)
        
        print(f"\n✅ Results saved to: {filename}")


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Embedding Storage Benchmark (AoS vs SoA)')
    parser.add_argument('--embeddings', type=int, default=10000,
                       help='Number of embeddings (default: 10000)')
    parser.add_argument('--dim', type=int, default=768,
                       help='Embedding dimension (default: 768)')
    parser.add_argument('--iterations', type=int, default=100,
                       help='Number of iterations (default: 100)')
    parser.add_argument('--top-k', type=int, default=10,
                       help='Top-k for similarity search (default: 10)')
    parser.add_argument('--output', type=str, default='results/embedding_benchmark.json',
                       help='Output file')
    
    args = parser.parse_args()
    
    # Run benchmark
    bench = EmbeddingBenchmark(n_embeddings=args.embeddings, dim=args.dim)
    
    bench.benchmark_similarity_search(iterations=args.iterations, top_k=args.top_k)
    bench.benchmark_partial_access(iterations=args.iterations)
    bench.benchmark_memory_layout()
    
    bench.print_summary()
    bench.save_results(args.output)


if __name__ == '__main__':
    main()
