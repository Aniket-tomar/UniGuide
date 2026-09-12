from retriever import build_hybrid_retriever
from engine import RulebookEngine

print("Initializing Gemini Hybrid Retriever & Engine...")
retriever = build_hybrid_retriever("./corpus")
engine = RulebookEngine(retriever)

test_questions = [
    # 1. State: RESOLVED
    "What minimum attendance percentage is required to be eligible for end-semester exams?",
    
    # 2. State: CONTRADICTED
    "Does the Academic Dean have the power to lower my attendance requirement below 75% for medical reasons?",
    
    # 3. State: UNADDRESSED (Near-miss)
    "Can my parents stay overnight in the university guest house during convocation?"
]

for q in test_questions:
    print("\n" + "=" * 60)
    print(f"QUERY: {q}")
    verdict = engine.query(q)
    print(f"STATE: {verdict.state.value} (Confidence: {verdict.confidence})")
    print(f"ANSWER: {verdict.answer}")
    if verdict.citations:
        print("CITATIONS:")
        for c in verdict.citations:
            print(f" - [{c.source}] \"{c.quote}\"")
    if verdict.conflicting_citations:
        print("CONFLICTING CITATIONS:")
        for c in verdict.conflicting_citations:
            print(f" - CONFLICT: [{c.source}] \"{c.quote}\"")

print("\n" + "=" * 60)
print("Verification complete!")