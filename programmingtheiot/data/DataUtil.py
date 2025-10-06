#####
# 
# This class is part of the Programming the Internet of Things
# project, and is available via the MIT License, which can be
# found in the LICENSE file at the top level of this repository.
# 
# You may find it more helpful to your design to adjust the
# functionality, constants and interfaces (if there are any)
# provided within in order to meet the needs of your specific
# Programming the Internet of Things project.
# 

import json
import logging

from json import JSONEncoder

from programmingtheiot.data.BaseIotData import BaseIotData
from programmingtheiot.data.ActuatorData import ActuatorData
from programmingtheiot.data.SensorData import SensorData
from programmingtheiot.data.SystemPerformanceData import SystemPerformanceData

class DataUtil():
    """
    Util class for json conversion	
    """

    def __init__(self, encodeToUtf8 = False):
        self.encodeToUtf8 = encodeToUtf8
        
    def _objectToJson(self, data: BaseIotData) -> str:
        jsonData = json.dumps(data, indent=2, cls=JsonDataEncoder)
        if self.encodeToUtf8:
            jsonData = jsonData.encode('utf-8')
            
        return jsonData
    
    def _jsonToDict(self, jsonData: str) -> dict:            
        return json.loads(jsonData)
    
    def _fillIotDataFromDict(self, data: BaseIotData, dataDict: dict):
        for attr,val in dataDict.items():
            if hasattr(data, attr):
                setattr(data, attr, val)   
            else:
                logging.warning(f"'{attr}' is not a valid attribute of '{data.__class__.__name__}'")
                # raise AttributeError(f"'{attr}' is not a valid attribute of '{data.__class__.__name__}'") # we should probably crash here
                
    # all the pub methods are just callbacks
    
    def actuatorDataToJson(self, data: ActuatorData = None) -> str:
        if not data:
            logging.warning("ActuatorData is None, returning empty string")
            return ""
        return self._objectToJson(data)
    
    def sensorDataToJson(self, data: SensorData = None) -> str:
        if not data:
            logging.warning("SensorData is None, returning empty string")
            return ""
        return self._objectToJson(data)

    def systemPerformanceDataToJson(self, data: SystemPerformanceData = None) -> str:
        if not data:
            logging.warning("SystemPerformanceData is None, returning empty string")
            return ""
        return self._objectToJson(data)
    
    def jsonToActuatorData(self, jsonData: str = None) -> ActuatorData:
        if not jsonData:
            logging.warning("jsonData is None, returning None")
            return None
        dict = self._jsonToDict(jsonData)
        ad = ActuatorData()
        self._fillIotDataFromDict(ad, dict)
        return ad
    
    def jsonToSensorData(self, jsonData: str = None) -> SensorData:
        if not jsonData:
            logging.warning("jsonData is None, returning None")
            return None
        dict = self._jsonToDict(jsonData)
        sd = SensorData()
        self._fillIotDataFromDict(sd, dict)
        return sd
    
    def jsonToSystemPerformanceData(self, jsonData: str = None) -> SystemPerformanceData:
        if not jsonData:
            logging.warning("jsonData is None, returning None")
            return None
        dict = self._jsonToDict(jsonData)
        spd = SystemPerformanceData()
        self._fillIotDataFromDict(spd, dict)
        return spd
    
class JsonDataEncoder(JSONEncoder):
    """
    Convenience class to facilitate JSON encoding of an object that
    can be converted to a dict.
    
    """
    def default(self, o):
        return o.__dict__
    