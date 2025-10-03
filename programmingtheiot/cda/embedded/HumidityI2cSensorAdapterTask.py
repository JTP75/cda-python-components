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

import smbus
import logging

from programmingtheiot.data.SensorData import SensorData
from programmingtheiot.cda.sim.SensorDataGenerator import SensorDataGenerator


import programmingtheiot.common.ConfigConst as ConfigConst
from programmingtheiot.cda.sim.BaseSensorSimTask import BaseSensorSimTask

class HumidityI2cSensorAdapterTask(BaseSensorSimTask):
    """
    TODO desc
    """

    def __init__(self):
        super(HumidityI2cSensorAdapterTask, self).__init__(
            name=ConfigConst.HUMIDITY_SENSOR_NAME,
            typeID=ConfigConst.HUMIDITY_SENSOR_TYPE,
            minVal=SensorDataGenerator.LOW_NORMAL_ENV_HUMIDITY,
            maxVal=SensorDataGenerator.HI_NORMAL_ENV_HUMIDITY
        )
        
        self.hts221addr = 0x5F # this is the addr for humid/temp sensor HTS221
        self.i2cbus = smbus.SMBus(1)
        
        # init the sensor
        # self.i2cbus.write_byte_data(self.hts221addr, 0, 0)
    
    def generateTelemetry(self) -> SensorData:
        sensorData = SensorData(name=self.getName(), typeID=self.getTypeID())
        logging.debug(f"who am i: {self.i2cbus.read_byte_data(self.hts221addr, 0x0F)}")
        sensorData.setValue(0)
        self.latestSensorData = sensorData
        return sensorData
    