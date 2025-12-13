"""
SmartEco+ Digital Twin - AI Detection & Auto-Fix System
Uses machine learning to detect anomalies and trigger automated fixes
"""

import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.linear_model import LinearRegression
from collections import defaultdict
from typing import Dict, List, Any
import time

class AIDetectionSystem:
    """AI-powered anomaly detection and predictive analytics"""
    
    def __init__(self):
        # History buffer for each location-sensor pair
        self.history = defaultdict(list)
        self.max_history = 100  # Keep last 100 data points
        
        # Trained models cache
        self.anomaly_detectors = {}
        self.prediction_models = {}
        
        # Detection thresholds
        self.contamination_rate = 0.1  # 10% expected anomalies
        self.prediction_window = 10  # Predict 10 steps ahead
        
        # Metrics
        self.detections = {
            'total_anomalies': 0,
            'total_predictions': 0,
            'auto_fixes_triggered': 0
        }
    
    def update_history(self, location_id: str, sensor_type: str, value: float):
        """Add new data point to history"""
        key = f"{location_id}_{sensor_type}"
        self.history[key].append(value)
        
        # Keep only recent history
        if len(self.history[key]) > self.max_history:
            self.history[key].pop(0)
    
    def detect_anomaly(self, location_id: str, sensor_type: str, current_value: float) -> Dict[str, Any]:
        """
        Use Isolation Forest to detect if current value is anomalous
        Returns: {is_anomaly: bool, confidence: float, reason: str}
        """
        key = f"{location_id}_{sensor_type}"
        
        # Need at least 20 data points to train
        if len(self.history[key]) < 20:
            return {
                'is_anomaly': False,
                'confidence': 0.0,
                'reason': 'Insufficient data for ML detection',
                'method': 'threshold_only'
            }
        
        try:
            # Prepare data for Isolation Forest
            data_points = np.array(self.history[key]).reshape(-1, 1)
            
            # Train Isolation Forest
            clf = IsolationForest(
                contamination=self.contamination_rate,
                random_state=42
            )
            clf.fit(data_points)
            
            # Predict if current value is anomaly
            prediction = clf.predict([[current_value]])[0]
            
            # Get anomaly score (lower = more anomalous)
            score = clf.score_samples([[current_value]])[0]
            
            # Calculate confidence (normalized)
            confidence = abs(score) * 100
            
            is_anomaly = (prediction == -1)
            
            if is_anomaly:
                self.detections['total_anomalies'] += 1
                
                # Determine reason based on value comparison
                mean_val = np.mean(self.history[key])
                std_val = np.std(self.history[key])
                
                if current_value > mean_val + 2 * std_val:
                    reason = f"Value {current_value:.2f} significantly higher than normal ({mean_val:.2f} ± {std_val:.2f})"
                elif current_value < mean_val - 2 * std_val:
                    reason = f"Value {current_value:.2f} significantly lower than normal ({mean_val:.2f} ± {std_val:.2f})"
                else:
                    reason = f"Unusual pattern detected (anomaly score: {score:.3f})"
            else:
                reason = "Value within normal range"
            
            return {
                'is_anomaly': is_anomaly,
                'confidence': min(confidence, 100),
                'reason': reason,
                'method': 'isolation_forest',
                'score': score
            }
            
        except Exception as e:
            # Fallback to simple threshold
            return {
                'is_anomaly': False,
                'confidence': 0.0,
                'reason': f'ML detection failed: {str(e)}',
                'method': 'error_fallback'
            }
    
    def predict_future_value(self, location_id: str, sensor_type: str, steps_ahead: int = 10) -> Dict[str, Any]:
        """
        Use Linear Regression to predict future value
        Returns: {predicted_value: float, confidence: float, trend: str}
        """
        key = f"{location_id}_{sensor_type}"
        
        # Need at least 10 data points for prediction
        if len(self.history[key]) < 10:
            return {
                'predicted_value': None,
                'confidence': 0.0,
                'trend': 'unknown',
                'reason': 'Insufficient data for prediction'
            }
        
        try:
            # Prepare data for Linear Regression
            X = np.array(range(len(self.history[key]))).reshape(-1, 1)
            y = np.array(self.history[key]).reshape(-1, 1)
            
            # Train Linear Regression
            model = LinearRegression()
            model.fit(X, y)
            
            # Predict future value
            future_step = len(self.history[key]) + steps_ahead
            predicted_value = model.predict([[future_step]])[0][0]
            
            # Calculate R² score (confidence in prediction)
            r2_score = model.score(X, y)
            confidence = r2_score * 100
            
            # Determine trend
            slope = model.coef_[0][0]
            if slope > 0.1:
                trend = 'increasing'
            elif slope < -0.1:
                trend = 'decreasing'
            else:
                trend = 'stable'
            
            self.detections['total_predictions'] += 1
            
            return {
                'predicted_value': predicted_value,
                'confidence': min(confidence, 100),
                'trend': trend,
                'slope': slope,
                'r2_score': r2_score,
                'steps_ahead': steps_ahead
            }
            
        except Exception as e:
            return {
                'predicted_value': None,
                'confidence': 0.0,
                'trend': 'error',
                'reason': f'Prediction failed: {str(e)}'
            }
    
    def should_trigger_auto_fix(self, location_id: str, sensor_type: str, 
                                current_value: float, threshold: float) -> Dict[str, Any]:
        """
        Decide if auto-fix should be triggered based on AI analysis
        Returns: {should_fix: bool, reason: str, urgency: str, predicted_impact: float}
        """
        # Run anomaly detection
        anomaly_result = self.detect_anomaly(location_id, sensor_type, current_value)
        
        # Run prediction
        prediction_result = self.predict_future_value(location_id, sensor_type)
        
        should_fix = False
        reason = ""
        urgency = "low"
        predicted_impact = 0.0
        
        # Decision logic
        if current_value > threshold:
            # Immediate threshold breach
            should_fix = True
            urgency = "high"
            reason = f"Threshold breach: {current_value:.2f} > {threshold:.2f}"
            
            # Calculate predicted wastage if not fixed
            if prediction_result['predicted_value']:
                predicted_impact = (prediction_result['predicted_value'] - threshold) * 10
            else:
                predicted_impact = (current_value - threshold) * 10
                
        elif anomaly_result['is_anomaly'] and anomaly_result['confidence'] > 70:
            # AI detected strong anomaly
            should_fix = True
            urgency = "medium"
            reason = f"AI anomaly detection: {anomaly_result['reason']}"
            predicted_impact = current_value * 0.5
            
        elif prediction_result['predicted_value'] and prediction_result['predicted_value'] > threshold:
            # Predicted to breach threshold soon
            should_fix = True
            urgency = "medium"
            reason = f"Predictive alert: Will reach {prediction_result['predicted_value']:.2f} (threshold: {threshold:.2f})"
            predicted_impact = (prediction_result['predicted_value'] - threshold) * 5
        
        if should_fix:
            self.detections['auto_fixes_triggered'] += 1
        
        return {
            'should_fix': should_fix,
            'reason': reason,
            'urgency': urgency,
            'predicted_impact': round(predicted_impact, 2),
            'anomaly_confidence': anomaly_result['confidence'],
            'prediction_confidence': prediction_result['confidence'],
            'trend': prediction_result.get('trend', 'unknown')
        }
    
    def get_insights(self, location_id: str, sensor_type: str) -> Dict[str, Any]:
        """Get AI insights for a specific sensor"""
        key = f"{location_id}_{sensor_type}"
        
        if key not in self.history or len(self.history[key]) < 5:
            return {
                'status': 'insufficient_data',
                'data_points': len(self.history.get(key, []))
            }
        
        data = self.history[key]
        
        return {
            'status': 'ready',
            'data_points': len(data),
            'statistics': {
                'mean': round(np.mean(data), 2),
                'std': round(np.std(data), 2),
                'min': round(np.min(data), 2),
                'max': round(np.max(data), 2),
                'current': round(data[-1], 2)
            },
            'recent_trend': self._calculate_recent_trend(data),
            'volatility': self._calculate_volatility(data)
        }
    
    def _calculate_recent_trend(self, data: List[float], window: int = 10) -> str:
        """Calculate trend over recent window"""
        if len(data) < window:
            window = len(data)
        
        recent = data[-window:]
        first_half = np.mean(recent[:window//2])
        second_half = np.mean(recent[window//2:])
        
        change_percent = ((second_half - first_half) / first_half) * 100 if first_half > 0 else 0
        
        if change_percent > 10:
            return 'rising'
        elif change_percent < -10:
            return 'falling'
        else:
            return 'stable'
    
    def _calculate_volatility(self, data: List[float]) -> str:
        """Calculate data volatility"""
        if len(data) < 2:
            return 'unknown'
        
        std = np.std(data)
        mean = np.mean(data)
        
        cv = (std / mean) * 100 if mean > 0 else 0  # Coefficient of variation
        
        if cv > 30:
            return 'high'
        elif cv > 15:
            return 'medium'
        else:
            return 'low'
    
    def get_detection_stats(self) -> Dict[str, Any]:
        """Get overall AI detection statistics"""
        return {
            'total_anomalies_detected': self.detections['total_anomalies'],
            'total_predictions_made': self.detections['total_predictions'],
            'auto_fixes_triggered': self.detections['auto_fixes_triggered'],
            'locations_monitored': len(set(key.split('_')[0] for key in self.history.keys())),
            'sensors_tracked': len(self.history),
            'total_data_points': sum(len(data) for data in self.history.values())
        }


# Global AI system instance
ai_system = AIDetectionSystem()