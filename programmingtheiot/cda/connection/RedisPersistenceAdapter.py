import redis
import logging

import programmingtheiot.common.ConfigConst as ConfigConst
from programmingtheiot.common.ConfigUtil import ConfigUtil

from programmingtheiot.common.ResourceNameEnum import ResourceNameEnum
from programmingtheiot.data.SensorData import SensorData

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
        return False
        # if self.connected:
        #     logging.warning("Redis client is already connected.")
        #     return True
        
        # try:
        #     self.client = redis.Redis(host=self.host, port=self.port)
        #     logging.info(f"Connected to Redis server at {self.host}:{self.port}")
        #     self.connected = True
        #     return True
        # except Exception as e:
        #     logging.error(f"Failed to connect to Redis server: {e}")
        #     self.client.close()
        #     self.connected = False
        #     return False
    
    def disconnectClient(self) -> bool:
        return False
        # if not self.connected:
        #     logging.warning("Redis client is already disconnected.")
        #     return True
        
        # try:
        #     self.client.close()
        #     logging.info("Disconnected from Redis server.")
        #     self.connected = False
        #     return True
        # except Exception as e:
        #     logging.error(f"Failed to disconnect from Redis server: {e}")
        #     return False
        
    def storeData(self, resource: ResourceNameEnum, data: SensorData) -> bool:
        return False