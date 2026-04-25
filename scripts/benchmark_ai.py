import json
import os
import sys
import time

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ai.assistant import get_assistant_response

def run_benchmark():
    dataset_path = "business_ai_dataset.json"
    if not os.path.exists(dataset_path):
        print("Dataset not found! Run generate_dataset.py first.")
        return

    with open(dataset_path, "r") as f:
        dataset = json.load(f)

    # We will test a representative subset (e.g., first 100) to save time/Ollama resources, 
    # then report findings.
    test_subset = dataset[:10] 
    
    results = {
        "total": len(test_subset),
        "success": 0,
        "failed": 0,
        "errors": []
    }

    print(f"Starting Benchmark on {len(test_subset)} samples...")
    
    for entry in test_subset:
        question = entry["question"]
        print(f"Testing ID {entry['id']}: {question}")
        try:
            # We use a timeout to avoid hanging on a bad model response
            start_time = time.time()
            response = get_assistant_response(question)
            end_time = time.time()
            
            # Check for common failure indicators in the grounding logic
            fail_indicators = ["couldn't find", "Database Error", "zero results", "unavailable"]
            is_failure = any(indicator.lower() in response.lower() for indicator in fail_indicators)
            
            if is_failure:
                results["failed"] += 1
                results["errors"].append({
                    "id": entry["id"],
                    "question": question,
                    "response": response
                })
            else:
                results["success"] += 1
                
        except Exception as e:
            results["failed"] += 1
            results["errors"].append({
                "id": entry["id"],
                "question": question,
                "error": str(e)
            })

    # Save detailed report
    with open("benchmark_results.json", "w") as f:
        json.dump(results, f, indent=2)

    # Summary Report
    print("\n" + "="*40)
    print("BENCHMARK REPORT")
    print("="*40)
    print(f"Total Tested: {results['total']}")
    print(f"Success:      {results['success']} ({(results['success']/results['total'])*100:.1f}%)")
    print(f"Failures:     {results['failed']}")
    print("="*40)

    if results["errors"]:
        print("\nTOP FAILURE PATTERNS:")
        # Show top 5 errors
        for err in results["errors"][:5]:
            print(f"- Question: {err['question']}")
            print(f"  Issue:    {err.get('response', err.get('error', 'Unknown error'))[:100]}...")
            print("-" * 20)

if __name__ == "__main__":
    run_benchmark()
