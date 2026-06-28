from datetime import datetime
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, asdict

@dataclass
class Prediction:
    period: str
    prediction: str
    pattern: str
    status: str
    result: int
    
    def to_dict(self) -> Dict:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Prediction':
        return cls(
            period=data.get('period', ''),
            prediction=data.get('prediction', ''),
            pattern=data.get('pattern', ''),
            status=data.get('status', 'PENDING'),
            result=int(data.get('result', 0))
        )

@dataclass
class PredictionRequest:
    pattern: str
    history: Optional[List[Dict]] = None
    
    def to_dict(self) -> Dict:
        return asdict(self)

@dataclass
class PredictionResponse:
    period: str
    prediction: str
    pattern: str
    confidence: float
    probabilities: Dict[str, float]
    reasoning: List[str]
    timestamp: str
    
    def to_dict(self) -> Dict:
        return asdict(self)
