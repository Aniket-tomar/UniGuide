from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field

class RulebookState(str, Enum):
    RESOLVED = "RESOLVED"           # Unambiguous answer backed by a clear rule
    CONTRADICTED = "CONTRADICTED"   # Two or more clauses give conflicting answers
    UNADDRESSED = "UNADDRESSED"     # Document contains zero answers (near-misses fall here)

class Citation(BaseModel):
    source: str = Field(description="Filename of the source document, e.g. Academic_Regulations_Handbook.md")
    section: str = Field(description="Section or clause header, e.g. Section 3.1.2 or Late Penalties Table")
    quote: str = Field(description="Verbatim excerpt from the document backing this claim")

class RulebookAnalysis(BaseModel):
    state: RulebookState = Field(
        description="The exact epistemic state: RESOLVED, CONTRADICTED, or UNADDRESSED"
    )
    confidence: float = Field(
        description="Confidence score between 0.0 and 1.0",
        ge=0.0,
        le=1.0
    )
    answer: str = Field(
        description="Clear, concise explanation for a student. If UNADDRESSED, explicitly state what policy is missing."
    )
    citations: List[Citation] = Field(
        default_factory=list,
        description="Verbatim citations supporting the resolution. Empty if UNADDRESSED."
    )
    conflicting_citations: Optional[List[Citation]] = Field(
        default=None,
        description="If CONTRADICTED, must contain the two opposing clauses that contradict each other."
    )