import json
import time
from tabulate import tabulate
from engine import RulebookEngine
from retriever import build_hybrid_retriever

def run_evaluation(test_set_path="eval_test_set.json"):
    print("⏳ Initializing Hybrid Retriever & Engine...")
    retriever = build_hybrid_retriever("./corpus")
    engine = RulebookEngine(retriever)
    
    try:
        with open(test_set_path, "r") as f:
            test_cases = json.load(f)
    except FileNotFoundError:
        print(f"❌ Error: Could not find {test_set_path}. Make sure it is in the root folder!")
        return

    results = []
    correct_states = 0
    total = len(test_cases)
    
    state_breakdown = {
        "RESOLVED": {"total": 0, "correct": 0},
        "CONTRADICTED": {"total": 0, "correct": 0},
        "UNADDRESSED": {"total": 0, "correct": 0}
    }

    print(f"\n🚀 Running Evaluation across {total} test queries...\n")

    for idx, tc in enumerate(test_cases, 1):
        q = tc["question"]
        expected_state = tc["expected_state"]
        
        start = time.time()
        # Suppress internal warnings for a cleaner output
        try:
            verdict = engine.query(q)
            predicted = verdict.state.value
        except Exception as e:
            predicted = f"ERROR: {str(e)[:30]}"
            
        latency = round(time.time() - start, 2)
        
        is_match = (predicted == expected_state)
        if is_match:
            correct_states += 1
            state_breakdown[expected_state]["correct"] += 1
            
        # Ensure we don't count missing keys in breakdown
        if expected_state in state_breakdown:
            state_breakdown[expected_state]["total"] += 1

        results.append([
            idx,
            q[:45] + "..." if len(q) > 45 else q,
            expected_state,
            predicted,
            "✅ PASS" if is_match else "❌ FAIL",
            f"{latency}s"
        ])
        print(f"[{idx}/{total}] Processed: {q[:30]}... -> {predicted}")

    # Print Detailed Table
    print("\n" + "="*80)
    print(tabulate(
        results, 
        headers=["#", "Query", "Expected", "Predicted", "Result", "Latency"], 
        tablefmt="github"
    ))

    # Print Summary Metrics
    print("\n================ EVALUATION SUMMARY ================")
    print(f"Overall State Accuracy: {correct_states}/{total} ({(correct_states/total*100):.1f}%)")
    for st, counts in state_breakdown.items():
        if counts["total"] > 0:
            pct = (counts["correct"] / counts["total"] * 100)
            print(f" - {st:<13} Accuracy: {counts['correct']}/{counts['total']} ({pct:.1f}%)")
    print("====================================================\n")

if __name__ == "__main__":
    run_evaluation()