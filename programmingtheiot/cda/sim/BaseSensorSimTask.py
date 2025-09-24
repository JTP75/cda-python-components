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

import logging
import random

import programmingtheiot.common.ConfigConst as ConfigConst
from programmingtheiot.data.SensorData import SensorData
from programmingtheiot.cda.sim.SensorDataGenerator import SensorDataSet

class BaseSensorSimTask():
    """
    Base sensor simulation task. This provides basic functionality for all sensor simulation tasks.
    
    """

    DEFAULT_MIN_VAL = ConfigConst.DEFAULT_VAL
    DEFAULT_MAX_VAL = 100.0
    
    def __init__(self, name = ConfigConst.NOT_SET, typeID: int = ConfigConst.DEFAULT_SENSOR_TYPE, dataSet: SensorDataSet = None, minVal: float = DEFAULT_MIN_VAL, maxVal: float = DEFAULT_MAX_VAL):
        self.dataSet = dataSet
        self.name = name
        self.typeID = typeID
        self.dataSetIndex = 0
        self.useRandom = False
        
        self.latestSensorData = None
        
        if not self.dataSet:
            self.useRandom = True
            if minVal >= maxVal:
                raise ValueError("minVal must be less than maxVal")
            self.minVal = minVal
            self.maxVal = maxVal
        
    def generateTelemetry(self) -> SensorData:
        """
        Implement basic logging and SensorData creation. Sensor-specific functionality
        should be implemented by sub-class.
        
        A local reference to SensorData can be contained in this base class.
        """
        sensorData = SensorData(typeID=self.getTypeID(), name=self.getName())
        sensorVal = ConfigConst.DEFAULT_VAL
        
        if self.useRandom:
            # NOTE this will be different when implemented with real sensors
            sensorVal = random.uniform(self.minVal, self.maxVal)
        else:
            sensorVal = self.dataSet.getDataEntry(self.dataSetIndex)
            self.dataSetIndex += 1
            if self.dataSetIndex >= self.dataSet.getDataEntryCount():
                self.dataSetIndex = 0
        sensorData.setValue(sensorVal)
        self.latestSensorData = sensorData
        return self.latestSensorData
    
    def getTelemetryValue(self) -> float:
        """
        If a local reference to SensorData is not None, simply return its current value.
        If SensorData hasn't yet been created, call self.generateTelemetry(), then return
        its current value.
        
        NOTE: This method is not const since it may call generateTelemetry()
        """
        if self.latestSensorData is None:
            self.generateTelemetry()
        return self.latestSensorData.getValue()
    
    def getLatestTelemetry(self) -> SensorData:
        """
        This can return the current SensorData instance or a copy.
        """
        pass
    
    def getName(self) -> str:
        return self.name
    
    def getTypeID(self) -> int:
        return self.typeID
    