from typing import List, TypedDict


class IterationRecord(TypedDict):
    iteration: int
    draft: str
    feedback: str
    refined: str


class SwarmState(TypedDict):
    topic: str
    speaker: str
    draft_argument: str
    opponent_argument: str
    critic_feedback: str
    refined_argument: str
    final_argument: str
    iteration_count: int
    max_iterations: int
    improvement_needed: bool
    iteration_history: List[IterationRecord]
