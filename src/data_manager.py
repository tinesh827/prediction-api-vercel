import json
from typing import List, Dict, Optional
from datetime import datetime
import pandas as pd

class DataManager:
    def __init__(self, data_file=None):
        self.data = []
    
    def _load_data(self):
        pass
    
    def _save_data(self):
        pass
    
    def add_prediction(self, prediction: Dict):
        if 'timestamp' not in prediction:
            prediction['timestamp'] = datetime.now().isoformat()
        self.data.append(prediction)
        if len(self.data) > 1000:
            self.data = self.data[-1000:]
    
    def get_all_predictions(self) -> List[Dict]:
        return self.data
    
    def get_prediction_by_period(self, period: str) -> Optional[Dict]:
        for pred in self.data:
            if pred.get('period') == period:
                return pred
        return None
    
    def get_history(self, limit: int = 100) -> List[Dict]:
        return self.data[-limit:] if self.data else []
    
    def get_patterns(self) -> List[str]:
        return [d.get('pattern', '') for d in self.data if d.get('pattern')]
    
    def get_analytics(self) -> Dict:
        if not self.data:
            return {'total': 0, 'message': 'No data yet'}
        
        df = pd.DataFrame(self.data)
        
        analytics = {
            'total': len(df),
            'win_rate': round((df['status'] == 'WIN').mean() * 100, 2) if 'status' in df else 0,
            'unique_patterns': df['pattern'].nunique() if 'pattern' in df else 0,
            'predictions': {}
        }
        
        if 'prediction' in df:
            analytics['predictions'] = df['prediction'].value_counts().to_dict()
        
        return analytics
