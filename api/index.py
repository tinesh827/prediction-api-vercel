from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime
import re
import random
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.prediction_engine import PredictionEngine
from src.data_manager import DataManager

app = Flask(__name__)
CORS(app)

data_manager = DataManager()
prediction_engine = PredictionEngine()

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'environment': 'vercel'
    })

@app.route('/api/predict', methods=['POST'])
def predict():
    try:
        data = request.get_json()
        
        if not data or 'pattern' not in data:
            return jsonify({'error': 'Pattern required'}), 400
        
        pattern = data['pattern']
        
        if not re.match(r'^[12]{10}$', pattern):
            return jsonify({'error': 'Invalid pattern'}), 400
        
        result = prediction_engine.generate_prediction(pattern)
        period = f"202606171000{random.randint(10000, 99999)}"
        
        response = {
            'period': period,
            'pattern': pattern,
            'prediction': result['prediction'],
            'confidence': result['confidence'],
            'probabilities': result['probabilities'],
            'reasoning': result['reasoning'],
            'specific_numbers': prediction_engine.predict_specific_number(pattern),
            'timestamp': datetime.now().isoformat()
        }
        
        data_manager.add_prediction({
            'period': period,
            'pattern': pattern,
            'prediction': result['prediction'],
            'status': 'PENDING',
            'probabilities': result['probabilities']
        })
        
        return jsonify(response)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/analytics', methods=['GET'])
def get_analytics():
    try:
        analytics = data_manager.get_analytics()
        accuracy = prediction_engine.get_accuracy()
        
        return jsonify({
            'analytics': analytics,
            'accuracy': accuracy,
            'timestamp': datetime.now().isoformat()
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/history', methods=['GET'])
def get_history():
    try:
        limit = request.args.get('limit', 50, type=int)
        history = data_manager.get_history(limit)
        
        return jsonify({
            'total': len(history),
            'history': history,
            'timestamp': datetime.now().isoformat()
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/update-result', methods=['POST'])
def update_result():
    try:
        data = request.get_json()
        
        if not data or 'period' not in data or 'result' not in data:
            return jsonify({'error': 'Period and result required'}), 400
        
        period = data['period']
        result = data['result']
        
        if not (0 <= result <= 9):
            return jsonify({'error': 'Result must be 0-9'}), 400
        
        pred = data_manager.get_prediction_by_period(period)
        
        if not pred:
            return jsonify({'error': 'Prediction not found'}), 404
        
        result_category = 'BIG' if result >= 5 else 'SMALL'
        predicted = pred.get('prediction', '')
        predicted_primary = 'BIG' if 'BIG' in predicted else 'SMALL'
        status = 'WIN' if result_category == predicted_primary else 'LOSS'
        
        pred['status'] = status
        pred['result'] = result
        pred['updated_at'] = datetime.now().isoformat()
        
        prediction_engine.update_history(pred)
        
        return jsonify({
            'period': period,
            'result': result,
            'status': status,
            'message': f'Marked as {status}'
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/predict-number', methods=['POST'])
def predict_number():
    try:
        data = request.get_json()
        
        if not data or 'pattern' not in data:
            return jsonify({'error': 'Pattern required'}), 400
        
        pattern = data['pattern']
        
        if not re.match(r'^[12]{10}$', pattern):
            return jsonify({'error': 'Invalid pattern'}), 400
        
        number_probs = prediction_engine.predict_specific_number(pattern)
        best_number = max(number_probs, key=number_probs.get)
        
        return jsonify({
            'pattern': pattern,
            'number_probabilities': number_probs,
            'best_prediction': {
                'number': best_number,
                'probability': number_probs[best_number]
            }
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/batch-predict', methods=['POST'])
def batch_predict():
    try:
        data = request.get_json()
        
        if not data or 'patterns' not in data:
            return jsonify({'error': 'Patterns required'}), 400
        
        results = []
        
        for pattern in data['patterns']:
            if re.match(r'^[12]{10}$', pattern):
                result = prediction_engine.generate_prediction(pattern)
                results.append({
                    'pattern': pattern,
                    'prediction': result['prediction'],
                    'confidence': result['confidence']
                })
        
        return jsonify({
            'total': len(results),
            'results': results,
            'timestamp': datetime.now().isoformat()
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/analyze-pattern', methods=['POST'])
def analyze_pattern():
    try:
        data = request.get_json()
        
        if not data or 'pattern' not in data:
            return jsonify({'error': 'Pattern required'}), 400
        
        pattern = data['pattern']
        
        if not re.match(r'^[12]{10}$', pattern):
            return jsonify({'error': 'Invalid pattern'}), 400
        
        features = prediction_engine.analyze_pattern(pattern)
        probabilities = prediction_engine.calculate_probabilities(pattern)
        
        return jsonify({
            'pattern': pattern,
            'features': features,
            'probabilities': probabilities,
            'timestamp': datetime.now().isoformat()
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/compare-patterns', methods=['POST'])
def compare_patterns():
    try:
        data = request.get_json()
        
        if not data or 'patterns' not in data:
            return jsonify({'error': 'Patterns required'}), 400
        
        comparisons = []
        
        for pattern in data['patterns']:
            if re.match(r'^[12]{10}$', pattern):
                features = prediction_engine.analyze_pattern(pattern)
                probs = prediction_engine.calculate_probabilities(pattern)
                
                comparisons.append({
                    'pattern': pattern,
                    'features': features,
                    'probabilities': probs,
                    'prediction': prediction_engine.generate_prediction(pattern)['prediction']
                })
        
        return jsonify({
            'comparisons': comparisons,
            'total': len(comparisons),
            'timestamp': datetime.now().isoformat()
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
