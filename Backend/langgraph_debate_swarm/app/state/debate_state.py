from typing import List, Optional, TypedDict


class DebateTurn(TypedDict):
    round: int
    speaker: str
    argument: str


class DebateState(TypedDict):
    topic: str
    current_round: int
    max_rounds: int
    proposer_argument: str
    opponent_argument: str
    debate_history: List[DebateTurn]
    next_speaker: str
    debate_finished: bool
    winner: Optional[str]
