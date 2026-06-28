import numpy as np
from typing import Dict, List, Tuple, Optional
from collections import Counter
import random
from datetime import datetime

class PredictionEngine:
    def __init__(self):
        self.position_weights = [0.05, 0.06, 0.07, 0.08, 0.09, 0.10, 0.12, 0.15, 0.18, 0.20]
        self.history = []
        self.pattern_cache = {}
    
    def analyze_pattern(self, pattern: str) -> Dict[str, any]:
        digits = [int(d) for d in pattern]
        
        features = {
            'digits': digits,
            'ones_count': digits.count(1),
            'twos_count': digits.count(2),
            'total': sum(digits),
            'weighted_score': self._calculate_weighted_score(digits),
            'consecutive_runs': self._find_runs(digits),
            'transitions': self._count_transitions(digits),
            'last_three': digits[-3:],
            'first_three': digits[:3],
            'middle_four': digits[3:7]
        }
        
        return features
    
    def _calculate_weighted_score(self, digits: List[int]) -> float:
        return sum(d * w for d, w in zip(digits, self.position_weights))
    
    def _find_runs(self, digits: List[int]) -> Dict[int, List[int]]:
        runs = {1: [], 2: []}
        if not digits:
            return runs
            
        current = digits[0]
        count = 1
        
        for i in range(1, len(digits)):
            if digits[i] == current:
                count += 1
            else:
                if current in runs:
                    runs[current].append(count)
                current = digits[i]
                count = 1
        
        if current in runs:
            runs[current].append(count)
        
        return runs
    
    def _count_transitions(self, digits: List[int]) -> int:
        transitions = 0
        for i in range(1, len(digits)):
            if digits[i] != digits[i-1]:
                transitions += 1
        return transitions
    
    def calculate_probabilities(self, pattern: str) -> Dict[str, float]:
        features = self.analyze_pattern(pattern)
        digits = features['digits']
        
        prob_big = features['twos_count'] / 10
        prob_small = features['ones_count'] / 10
        
        weighted = features['weighted_score']
        weighted_prob_big = weighted / 2
        
        runs = features['consecutive_runs']
        
        if 2 in runs and max(runs[2]) >= 3:
            if max(runs[2]) >= 5:
                prob_big = max(0.3, prob_big - 0.2)
            else:
                prob_big = min(0.8, prob_big + 0.1)
        
        recent_sum = sum(features['last_three'])
        if recent_sum >= 5:
            prob_big = min(0.9, prob_big + 0.15)
        elif recent_sum <= 3:
            prob_big = max(0.1, prob_big - 0.15)
        
        final_prob_big = (prob_big + weighted_prob_big) / 2
        final_prob_big = max(0.1, min(0.9, final_prob_big))
        
        prob_high = self._calculate_high_probability(digits)
        prob_low = 1 - prob_high
        
        return {
            'BIG': round(final_prob_big, 3),
            'SMALL': round(1 - final_prob_big, 3),
            'HIGH': round(prob_high, 3),
            'LOW': round(prob_low, 3),
            'CONFIDENCE': round(abs(final_prob_big - 0.5) * 2, 3)
        }
    
    def _calculate_high_probability(self, digits: List[int]) -> float:
        twos_count = digits.count(2)
        prob_high = twos_count / 10
        weighted_twos = sum(1 if d == 2 else 0 for d in digits[-5:])
        prob_high_recent = weighted_twos / 5
        final_prob = (prob_high + prob_high_recent) / 2
        return max(0.1, min(0.9, final_prob))
    
    def generate_prediction(self, pattern: str) -> Dict[str, any]:
        probabilities = self.calculate_probabilities(pattern)
        
        if probabilities['BIG'] >= 0.5:
            primary = 'BIG'
        else:
            primary = 'SMALL'
        
        secondary = 'HIGH' if probabilities['HIGH'] >= 0.5 else 'LOW'
        confidence = probabilities['CONFIDENCE']
        
        if confidence >= 0.8:
            prediction = f"{primary} @ SURESHOT"
        elif confidence >= 0.6:
            if secondary == 'HIGH':
                prediction = f"{primary} & {secondary}"
            else:
                prediction = f"{primary} % {secondary}"
        else:
            prediction = primary
        
        reasoning = self._generate_reasoning(pattern, probabilities)
        
        return {
            'prediction': prediction,
            'primary': primary,
            'secondary': secondary,
            'confidence': confidence,
            'probabilities': probabilities,
            'reasoning': reasoning
        }
    
    def _generate_reasoning(self, pattern: str, probabilities: Dict) -> List[str]:
        reasoning = []
        features = self.analyze_pattern(pattern)
        
        if features['twos_count'] > features['ones_count']:
            reasoning.append(f"Pattern has more 2s ({features['twos_count']}) than 1s ({features['ones_count']})")
        else:
            reasoning.append(f"Pattern has more 1s ({features['ones_count']}) than 2s ({features['twos_count']})")
        
        runs = features['consecutive_runs']
        if 2 in runs and max(runs[2]) >= 3:
            reasoning.append(f"Contains a run of {max(runs[2])} consecutive 2s")
        if 1 in runs and max(runs[1]) >= 3:
            reasoning.append(f"Contains a run of {max(runs[1])} consecutive 1s")
        
        transitions = features['transitions']
        if transitions > 6:
            reasoning.append(f"High pattern volatility with {transitions} transitions")
        elif transitions < 3:
            reasoning.append(f"Low pattern volatility with only {transitions} transitions")
        
        last_three = features['last_three']
        if sum(last_three) >= 5:
            reasoning.append(f"Recent trend favors BIG/2 with last three: {last_three}")
        else:
            reasoning.append(f"Recent trend favors SMALL/1 with last three: {last_three}")
        
        confidence = probabilities['CONFIDENCE']
        if confidence >= 0.8:
            reasoning.append(f"High confidence prediction ({confidence:.2%})")
        elif confidence >= 0.6:
            reasoning.append(f"Moderate confidence prediction ({confidence:.2%})")
        else:
            reasoning.append(f"Low confidence prediction ({confidence:.2%})")
        
        return reasoning
    
    def predict_specific_number(self, pattern: str) -> Dict[int, float]:
        features = self.analyze_pattern(pattern)
        probabilities = self.calculate_probabilities(pattern)
        
        base_probs = {}
        big_prob = probabilities['BIG']
        high_prob = probabilities['HIGH']
        
        for num in range(10):
            if num <= 4:
                base = (1 - big_prob) / 5
            else:
                base = big_prob / 5
            
            if num >= 5:
                base *= high_prob
            else:
                base *= (1 - high_prob)
            
            if num in [0, 9]:
                base *= 0.9
            elif num in [1, 8]:
                base *= 1.1
            
            base_probs[num] = round(base, 3)
        
        total = sum(base_probs.values())
        if total > 0:
            base_probs = {k: round(v/total, 3) for k, v in base_probs.items()}
        
        return base_probs
    
    def update_history(self, new_data: Dict):
        self.history.append(new_data)
        if len(self.history) > 1000:
            self.history = self.history[-1000:]
    
    def get_accuracy(self) -> Dict[str, float]:
        if not self.history:
            return {'accuracy': 0, 'total': 0}
        
        wins = sum(1 for h in self.history if h.get('status') == 'WIN')
        total = len(self.history)
        
        return {
            'accuracy': round(wins / total * 100, 2),
            'total': total,
            'wins': wins,
            'losses': total - wins
          }
