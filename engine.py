import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from schemas import RulebookAnalysis, RulebookState

load_dotenv()

SYSTEM_PROMPT = """You are an auditable Academic Ombudsman and Policy Arbiter.
Your task is to analyze university regulatory excerpts and answer student questions strictly using the provided text.

You MUST categorize your response into exactly one of three states:
1. 'RESOLVED':
   - A single, unambiguous rule explicitly answers the query.
   - You must cite the exact source and quote verbatim.

2. 'CONTRADICTED':
   - Two or more clauses give conflicting answers or incompatible instructions (e.g. one clause mandates 75% attendance while another removes the Dean's power to waive it, or contradictory refund rules).
   - In 'conflicting_citations', include both opposing citations with their exact verbatim quotes.

3. 'UNADDRESSED':
   - The excerpts do NOT explicitly answer the question.
   - CRITICAL NEAR-MISS RULE: If the question asks about a topic that is adjacent, related, or plausible, but NOT explicitly covered in the text (e.g., questions about missing exams for family weddings when the text only mentions medical leave; e-scooter charging when only general heaters are mentioned), you MUST RETURN 'UNADDRESSED'.
   - NEVER extrapolate, assume, or infer general university norms.
   - In this state, 'citations' and 'conflicting_citations' must be empty lists.

Every citation quote must be present word-for-word in the text excerpts."""

USER_PROMPT = """STUDENT INQUIRY: {question}

RETRIEVED REGULATORY EXCERPTS:
{context}

Perform your analysis and return the structured verdict."""

class RulebookEngine:
    def __init__(self, retriever):
        self.retriever = retriever
        # Using Gemini 3.5 Flash lite with structured output
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-3.5-flash-lite",
            temperature=0.0
        ).with_structured_output(RulebookAnalysis)
        
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", SYSTEM_PROMPT),
            ("user", USER_PROMPT)
        ])
        self.chain = self.prompt | self.llm

    def query(self, question: str) -> RulebookAnalysis:
        docs = self.retriever.invoke(question)
        
        context_parts = []
        for d in docs:
            src = d.metadata.get("source", "Unknown Document")
            page = f" (Page {d.metadata['page']})" if "page" in d.metadata else ""
            context_parts.append(f"--- SOURCE: {src}{page} ---\n{d.page_content}")
            
        context_text = "\n\n".join(context_parts)
        
        result: RulebookAnalysis = self.chain.invoke({
            "question": question,
            "context": context_text
        })
        return result