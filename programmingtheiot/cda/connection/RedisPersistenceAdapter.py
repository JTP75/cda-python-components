import redis
import logging

import programmingtheiot.common.ConfigConst as ConfigConst
from programmingtheiot.common.ConfigUtil import ConfigUtil

from programmingtheiot.common.ResourceNameEnum import ResourceNameEnum
from programmingtheiot.data.SensorData import SensorData
from programmingtheiot.data.DataUtil import DataUtil

class RedisPersistenceAdapter:
    """
    Adapter for Redis client connection
    """
    
    def __init__(self):
        self.configUtil = ConfigUtil()
        
        self.host = self.configUtil.getProperty(
            section=ConfigConst.DATA_GATEWAY_SERVICE, 
            key=ConfigConst.HOST_KEY
        )
        self.port = self.configUtil.getInteger(
            section=ConfigConst.DATA_GATEWAY_SERVICE, 
            key=ConfigConst.PORT_KEY
        )
        
        self.client = None
        self.connected = False
        
    def connectClient(self) -> bool:
        if self.connected:
            logging.warning("Redis client is already connected.")
            return True
        
        try:
            self.client = redis.Redis(host=self.host, port=self.port)
            logging.info(f"Connected to Redis server at {self.host}:{self.port}")
            if self.client.ping():
                logging.info("Successfully pinged Redis server.")
                self.connected = True
                return True
            else:
                logging.error("Failed to ping Redis server.")
                self.client.close()
                self.connected = False
                return False
        except Exception as e:
            logging.error(f"Failed to connect to Redis server: {e}")
            self.client.close()
            self.connected = False
            return False
    
    def disconnectClient(self) -> bool:
        if not self.connected:
            logging.warning("Redis client is already disconnected.")
            return True
        
        try:
            self.client.close()
            logging.info("Disconnected from Redis server.")
            self.connected = False
            return True
        except Exception as e:
            logging.error(f"Failed to disconnect from Redis server: {e}")
            return False
        
    def storeSensorData(self, resource: ResourceNameEnum, data: SensorData) -> bool:
        if not self.connected:
            logging.error("Redis client is not connected. Cannot store data.")
            return False
        
        # publish data to redis server
        try:
            key = resource.value
            value = DataUtil().sensorDataToJson(data)
            self.client.set(key, value)
            logging.info(f"Stored data under key '{key}': {value}")
            return True
        except Exception as e:
            logging.error(f"Failed to store data in Redis: {e}")
            return False
        