"""
MongoDB Database Configuration and Connection
"""
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import os
from config import Config

# MongoDB Connection Settings
MONGO_URI = Config.MONGO_URI
DATABASE_NAME = Config.DATABASE_NAME

class MongoDB:
    """MongoDB connection manager"""
    
    def __init__(self):
        self.client = None
        self.db = None
        self.connected = False
        
    def connect(self):
        """Establish MongoDB connection"""
        try:
            self.client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
            # Test connection
            self.client.admin.command('ping')
            self.db = self.client[DATABASE_NAME]
            self.connected = True
            print(f"✅ Connected to MongoDB: {DATABASE_NAME}")
            self._create_indexes()
            return True
        except ConnectionFailure as e:
            print(f"❌ MongoDB connection failed: {e}")
            self.connected = False
            return False
    
    def _create_indexes(self):
        """Create indexes for better query performance"""
        if not self.db:
            return
        
        # Telemetry indexes
        self.db[Config.COLLECTION_TELEMETRY].create_index([("timestamp", -1)])
        self.db[Config.COLLECTION_TELEMETRY].create_index([("source", 1)])
        self.db[Config.COLLECTION_TELEMETRY].create_index([("location", 1)])
        
        # Alerts indexes
        self.db[Config.COLLECTION_ALERTS].create_index([("timestamp", -1)])
        self.db[Config.COLLECTION_ALERTS].create_index([("resolved", 1)])
        self.db[Config.COLLECTION_ALERTS].create_index([("severity", 1)])
        self.db[Config.COLLECTION_ALERTS].create_index([("type", 1)])
        
        # Predictions indexes
        self.db[Config.COLLECTION_PREDICTIONS].create_index([("timestamp", -1)])
        self.db[Config.COLLECTION_PREDICTIONS].create_index([("resource_type", 1)])
        self.db[Config.COLLECTION_PREDICTIONS].create_index([("prediction_type", 1)])
        
        # Datasets indexes
        self.db[Config.COLLECTION_DATASETS].create_index([("uploaded_at", -1)])
        self.db[Config.COLLECTION_DATASETS].create_index([("status", 1)])
        
        # System logs indexes
        self.db[Config.COLLECTION_SYSTEM_LOGS].create_index([("timestamp", -1)])
        self.db[Config.COLLECTION_SYSTEM_LOGS].create_index([("level", 1)])
        self.db[Config.COLLECTION_SYSTEM_LOGS].create_index([("component", 1)])
        
        print("✅ Database indexes created for all collections")
    
    def disconnect(self):
        """Close MongoDB connection"""
        if self.client:
            self.client.close()
            self.connected = False
            print("MongoDB connection closed")
    
    # Telemetry Operations
    def save_telemetry(self, energy: float, water: float, waste: float, occupancy: int = 0, 
                      source: str = "simulator", location: str = "main"):
        """Save telemetry data"""
        if not self.connected:
            return None
        
        doc = {
            "timestamp": datetime.now(),
            "energy_kwh": round(energy, 2),
            "water_lpm": round(water, 2),
            "waste_pct": round(waste, 2),
            "occupancy": occupancy,
            "source": source,
            "location": location
        }
        
        result = self.db[Config.COLLECTION_TELEMETRY].insert_one(doc)
        return result.inserted_id
    
    def get_telemetry_history(self, hours: int = 24, limit: int = 1000) -> List[Dict]:
        """Get historical telemetry data"""
        if not self.connected:
            return []
        
        from_time = datetime.now() - timedelta(hours=hours)
        
        cursor = self.db[Config.COLLECTION_TELEMETRY].find(
            {"timestamp": {"$gte": from_time}},
            {"_id": 0}
        ).sort("timestamp", -1).limit(limit)
        
        return list(cursor)
    
    def get_latest_telemetry(self) -> Optional[Dict]:
        """Get most recent telemetry reading"""
        if not self.connected:
            return None
        
        doc = self.db[Config.COLLECTION_TELEMETRY].find_one(
            {},
            {"_id": 0},
            sort=[("timestamp", -1)]
        )
        return doc
    
    # Alert Operations
    def save_alert(self, alert_type: str, message: str, severity: str = "warning", 
                  alert_id: str = None, estimated_loss_inr: float = 0):
        """Save alert to database"""
        if not self.connected:
            return None
        
        doc = {
            "timestamp": datetime.now(),
            "alert_id": alert_id,
            "type": alert_type,
            "message": message,
            "severity": severity.upper(),
            "estimated_loss_inr": estimated_loss_inr,
            "resolved": False,
            "acknowledged": False
        }
        
        result = self.db[Config.COLLECTION_ALERTS].insert_one(doc)
        return result.inserted_id
    
    def get_active_alerts(self) -> List[Dict]:
        """Get unresolved alerts"""
        if not self.connected:
            return []
        
        cursor = self.db[Config.COLLECTION_ALERTS].find(
            {"resolved": False},
            {"_id": 0}
        ).sort("timestamp", -1)
        
        return list(cursor)
    
    def get_alerts_history(self, hours: int = 24, limit: int = 100) -> List[Dict]:
        """Get alert history"""
        if not self.connected:
            return []
        
        from_time = datetime.now() - timedelta(hours=hours)
        cursor = self.db[Config.COLLECTION_ALERTS].find(
            {"timestamp": {"$gte": from_time}},
            {"_id": 0}
        ).sort("timestamp", -1).limit(limit)
        
        return list(cursor)
    
    def resolve_alert(self, alert_id: str):
        """Mark alert as resolved"""
        if not self.connected:
            return False
        
        from bson import ObjectId
        result = self.db[Config.COLLECTION_ALERTS].update_one(
            {"_id": ObjectId(alert_id)},
            {"$set": {"resolved": True, "resolved_at": datetime.now()}}
        )
        return result.modified_count > 0
    
    def acknowledge_alert(self, alert_id: str):
        """Mark alert as acknowledged"""
        if not self.connected:
            return False
        
        from bson import ObjectId
        result = self.db[Config.COLLECTION_ALERTS].update_one(
            {"_id": ObjectId(alert_id)},
            {"$set": {"acknowledged": True, "acknowledged_at": datetime.now()}}
        )
        return result.modified_count > 0
    
    # Dataset Operations
    def save_dataset_info(self, filename: str, rows: int, status: str = "uploaded", 
                         file_size: int = 0, columns: List[str] = None):
        """Save dataset upload information"""
        if not self.connected:
            return None
        
        doc = {
            "uploaded_at": datetime.now(),
            "filename": filename,
            "file_size": file_size,
            "rows_count": rows,
            "columns": columns or [],
            "status": status
        }
        
        result = self.db[Config.COLLECTION_DATASETS].insert_one(doc)
        return result.inserted_id
    
    def get_datasets(self, limit: int = 10) -> List[Dict]:
        """Get uploaded datasets"""
        if not self.connected:
            return []
        
        cursor = self.db[Config.COLLECTION_DATASETS].find(
            {},
            {"_id": 0}
        ).sort("uploaded_at", -1).limit(limit)
        
        return list(cursor)
    
    # Prediction Operations
    def save_prediction(self, resource_type: str, prediction_type: str, predicted_value: float,
                       confidence: float = 0.0, model_version: str = "v1", features_used: Dict = None):
        """Save ML prediction result"""
        if not self.connected:
            return None
        
        doc = {
            "timestamp": datetime.now(),
            "resource_type": resource_type,
            "prediction_type": prediction_type,
            "predicted_value": round(predicted_value, 2),
            "confidence": round(confidence, 4),
            "model_version": model_version,
            "features_used": features_used or {}
        }
        
        result = self.db[Config.COLLECTION_PREDICTIONS].insert_one(doc)
        return result.inserted_id
    
    def get_predictions_history(self, resource_type: str = None, hours: int = 24, limit: int = 100) -> List[Dict]:
        """Get prediction history"""
        if not self.connected:
            return []
        
        from_time = datetime.now() - timedelta(hours=hours)
        query = {"timestamp": {"$gte": from_time}}
        
        if resource_type:
            query["resource_type"] = resource_type
        
        cursor = self.db[Config.COLLECTION_PREDICTIONS].find(
            query,
            {"_id": 0}
        ).sort("timestamp", -1).limit(limit)
        
        return list(cursor)
    
    # System Logs Operations
    def log_system_event(self, level: str, component: str, message: str, details: Dict = None):
        """Log system event"""
        if not self.connected:
            return None
        
        doc = {
            "timestamp": datetime.now(),
            "level": level.upper(),
            "component": component,
            "message": message,
            "details": details or {}
        }
        
        result = self.db[Config.COLLECTION_SYSTEM_LOGS].insert_one(doc)
        return result.inserted_id
    
    def get_system_logs(self, level: str = None, component: str = None, hours: int = 24, limit: int = 100) -> List[Dict]:
        """Get system logs"""
        if not self.connected:
            return []
        
        from_time = datetime.now() - timedelta(hours=hours)
        query = {"timestamp": {"$gte": from_time}}
        
        if level:
            query["level"] = level.upper()
        if component:
            query["component"] = component
        
        cursor = self.db[Config.COLLECTION_SYSTEM_LOGS].find(
            query,
            {"_id": 0}
        ).sort("timestamp", -1).limit(limit)
        
        return list(cursor)
    
    # Analytics Operations
    def get_statistics(self, hours: int = 24) -> Dict[str, Any]:
        """Get statistical summary"""
        if not self.connected:
            return {}
        
        from_time = datetime.now() - timedelta(hours=hours)
        
        pipeline = [
            {"$match": {"timestamp": {"$gte": from_time}}},
            {"$group": {
                "_id": None,
                "avg_energy": {"$avg": "$energy_kwh"},
                "max_energy": {"$max": "$energy_kwh"},
                "min_energy": {"$min": "$energy_kwh"},
                "avg_water": {"$avg": "$water_lpm"},
                "max_water": {"$max": "$water_lpm"},
                "min_water": {"$min": "$water_lpm"},
                "avg_waste": {"$avg": "$waste_pct"},
                "max_waste": {"$max": "$waste_pct"},
                "count": {"$sum": 1}
            }}
        ]
        
        result = list(self.db[Config.COLLECTION_TELEMETRY].aggregate(pipeline))
        return result[0] if result else {}
    
    def clear_old_data(self, days: int = None):
        """Delete data older than specified days"""
        if not self.connected:
            return {"telemetry": 0, "alerts": 0, "logs": 0}
        
        # Use retention policies from Config if not specified
        telemetry_days = days or Config.TELEMETRY_RETENTION_DAYS
        alerts_days = days or Config.ALERTS_RETENTION_DAYS
        logs_days = days or Config.LOGS_RETENTION_DAYS
        
        results = {}
        
        # Clean telemetry
        from_time = datetime.now() - timedelta(days=telemetry_days)
        result = self.db[Config.COLLECTION_TELEMETRY].delete_many(
            {"timestamp": {"$lt": from_time}}
        )
        results["telemetry"] = result.deleted_count
        
        # Clean alerts
        from_time = datetime.now() - timedelta(days=alerts_days)
        result = self.db[Config.COLLECTION_ALERTS].delete_many(
            {"timestamp": {"$lt": from_time}, "resolved": True}
        )
        results["alerts"] = result.deleted_count
        
        # Clean logs
        from_time = datetime.now() - timedelta(days=logs_days)
        result = self.db[Config.COLLECTION_SYSTEM_LOGS].delete_many(
            {"timestamp": {"$lt": from_time}}
        )
        results["logs"] = result.deleted_count
        
        print(f"Cleaned old data: {results}")
        return results


# Global MongoDB instance
db = MongoDB()

def get_db() -> MongoDB:
    """Get MongoDB instance"""
    if not db.connected:
        db.connect()
    return db
