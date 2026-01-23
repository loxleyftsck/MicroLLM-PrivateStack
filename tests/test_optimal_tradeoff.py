"""
MicroLLM-PrivateStack - Optimal Trade-off Finder
Tests multiple parameter combinations to find the best balance between:
- Speed (response time)
- Quality (response length & coherence)
- Resource efficiency
"""

import requests
import time
import statistics
import sys
from itertools import product

API_URL = "http://localhost:8000"

# Parameters to test
MAX_TOKENS_OPTIONS = [64, 128, 256]
TEMPERATURE_OPTIONS = [0.1, 0.5, 0.7, 0.9]
# Note: Context length and threads are model-level settings

# Fresh queries (to avoid cache hits)
TEST_QUERIES = [
    "Explain blockchain technology",
    "What is quantum computing?",
    "How do neural networks learn?",
    "Describe cloud computing benefits",
    "What is cybersecurity?",
]

def setup_auth():
    """Get auth token"""
    try:
        requests.post(f"{API_URL}/api/auth/register", json={
            "email": "optimizer@test.com",
            "password": "Optimizer2026!",
            "display_name": "Trade-off Optimizer"
        }, timeout=10)
    except:
        pass
    
    resp = requests.post(f"{API_URL}/api/auth/login", json={
        "email": "optimizer@test.com",
        "password": "Optimizer2026!"
    }, timeout=10)
    
    if resp.status_code == 200:
        return resp.json()['token']
    else:
        print(f"Auth failed: {resp.text}")
        sys.exit(1)

def test_config(token: str, max_tokens: int, temperature: float, query: str) -> dict:
    """Test a single configuration"""
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    
    start = time.time()
    try:
        resp = requests.post(
            f"{API_URL}/api/chat",
            headers=headers,
            json={
                "message": query,
                "max_tokens": max_tokens,
                "temperature": temperature
            },
            timeout=120
        )
        duration = time.time() - start
        
        if resp.status_code == 200:
            data = resp.json()
            response_text = data.get("response", "")
            return {
                "success": True,
                "time": duration,
                "tokens": data.get("tokens_generated", 0),
                "response_len": len(response_text),
                "response": response_text[:200]
            }
        else:
            return {"success": False, "time": duration, "error": resp.text}
    except Exception as e:
        return {"success": False, "time": time.time() - start, "error": str(e)}

def calculate_trade_off_score(results: list) -> dict:
    """
    Calculate composite trade-off score
    
    Factors:
    - Speed Score: Inverse of avg time (faster = better)
    - Quality Score: Based on response length (longer = more complete, up to a point)
    - Efficiency Score: Tokens per second
    - Reliability Score: Success rate
    """
    successful = [r for r in results if r.get("success")]
    
    if not successful:
        return {"total_score": 0, "speed": 0, "quality": 0, "efficiency": 0, "reliability": 0}
    
    avg_time = statistics.mean([r["time"] for r in successful])
    avg_tokens = statistics.mean([r["tokens"] for r in successful])
    avg_len = statistics.mean([r["response_len"] for r in successful])
    success_rate = len(successful) / len(results)
    
    # Speed Score (0-100): Target is 3s = 100, 10s = 30
    speed_score = max(0, min(100, 100 - (avg_time - 3) * 10))
    
    # Quality Score (0-100): Based on response length
    # Target: 200-500 chars = optimal
    if avg_len < 100:
        quality_score = avg_len / 100 * 50  # Penalize short responses
    elif avg_len < 500:
        quality_score = 50 + (avg_len - 100) / 400 * 50  # Reward up to 500
    else:
        quality_score = 100  # Max out at 500+
    
    # Efficiency Score: Tokens per second
    tokens_per_sec = avg_tokens / avg_time if avg_time > 0 else 0
    efficiency_score = min(100, tokens_per_sec * 5)  # 20 tok/s = 100
    
    # Reliability Score
    reliability_score = success_rate * 100
    
    # Weighted Total Score
    # Speed: 30%, Quality: 30%, Efficiency: 20%, Reliability: 20%
    total_score = (
        speed_score * 0.30 +
        quality_score * 0.30 +
        efficiency_score * 0.20 +
        reliability_score * 0.20
    )
    
    return {
        "total_score": round(total_score, 1),
        "speed": round(speed_score, 1),
        "quality": round(quality_score, 1),
        "efficiency": round(efficiency_score, 1),
        "reliability": round(reliability_score, 1),
        "avg_time": round(avg_time, 2),
        "avg_tokens": round(avg_tokens, 1),
        "avg_len": round(avg_len, 0)
    }

def main():
    print("=" * 70)
    print("MicroLLM-PrivateStack - OPTIMAL TRADE-OFF FINDER")
    print("=" * 70)
    
    # Generate all combinations
    combinations = list(product(MAX_TOKENS_OPTIONS, TEMPERATURE_OPTIONS))
    print(f"Testing {len(combinations)} parameter combinations")
    print(f"Using {len(TEST_QUERIES)} unique queries to avoid cache")
    print()
    
    # Auth
    print("Authenticating...", end=" ")
    token = setup_auth()
    print("OK\n")
    
    all_results = []
    query_idx = 0
    
    for i, (max_tokens, temp) in enumerate(combinations, 1):
        config_name = f"tokens={max_tokens}, temp={temp}"
        print(f"[{i}/{len(combinations)}] {config_name}")
        
        # Use rotating queries to avoid cache
        query = TEST_QUERIES[query_idx % len(TEST_QUERIES)]
        query_idx += 1
        
        result = test_config(token, max_tokens, temp, query)
        
        if result["success"]:
            print(f"    Time: {result['time']:.2f}s | Tokens: {result['tokens']} | Len: {result['response_len']}")
        else:
            print(f"    ERROR: {result.get('error', 'Unknown')[:50]}")
        
        result["max_tokens"] = max_tokens
        result["temperature"] = temp
        all_results.append(result)
    
    # Group results by config and calculate scores
    print("\n" + "=" * 70)
    print("TRADE-OFF ANALYSIS")
    print("=" * 70)
    
    # For this test, each config has 1 result, but we can still score them
    scored_configs = []
    for r in all_results:
        if r["success"]:
            score_data = calculate_trade_off_score([r])
            scored_configs.append({
                "max_tokens": r["max_tokens"],
                "temperature": r["temperature"],
                **score_data
            })
    
    # Sort by total score
    scored_configs.sort(key=lambda x: x["total_score"], reverse=True)
    
    print("\n{:<20} {:>8} {:>8} {:>8} {:>8} {:>10}".format(
        "Config", "Speed", "Quality", "Effic.", "Reliab.", "TOTAL"
    ))
    print("-" * 70)
    
    for sc in scored_configs[:10]:  # Top 10
        config_str = f"T{sc['max_tokens']}/t{sc['temperature']}"
        print("{:<20} {:>8} {:>8} {:>8} {:>8} {:>10}".format(
            config_str,
            sc["speed"],
            sc["quality"],
            sc["efficiency"],
            sc["reliability"],
            f"{sc['total_score']} ⭐" if sc == scored_configs[0] else sc["total_score"]
        ))
    
    # Best configuration
    best = scored_configs[0]
    
    print("\n" + "=" * 70)
    print("🏆 OPTIMAL CONFIGURATION FOUND")
    print("=" * 70)
    print(f"\n  max_tokens:   {best['max_tokens']}")
    print(f"  temperature:  {best['temperature']}")
    print(f"\n  Performance:")
    print(f"    Avg Response Time: {best['avg_time']}s")
    print(f"    Avg Tokens:        {best['avg_tokens']}")
    print(f"    Avg Response Len:  {best['avg_len']} chars")
    print(f"\n  Scores:")
    print(f"    Speed:      {best['speed']}/100")
    print(f"    Quality:    {best['quality']}/100")
    print(f"    Efficiency: {best['efficiency']}/100")
    print(f"    Reliability:{best['reliability']}/100")
    print(f"    ─────────────────")
    print(f"    TOTAL:      {best['total_score']}/100")
    print("=" * 70)
    
    # Apply recommendation
    print("\n📋 APPLY THIS CONFIG:")
    print(f'   MODEL_TEMPERATURE="{best["temperature"]}"')
    print(f'   Default max_tokens={best["max_tokens"]}')

if __name__ == "__main__":
    main()
