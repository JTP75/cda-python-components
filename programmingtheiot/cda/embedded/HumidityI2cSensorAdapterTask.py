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
        
        status = self.i2cbus.read_byte_data(self.hts221addr, 0x27)
        logging.debug(f"status {status}")
        
        if status & 0x01:
            # get humidity regs
            h_out_l = self.i2cbus.read_byte_data(self.hts221addr, 0x28)
            h_out_h = self.i2cbus.read_byte_data(self.hts221addr, 0x29)
            h_out = (h_out_h << 8) | h_out_l
            
            # get calibration regs
            h0_t0_out_l = self.i2cbus.read_byte_data(self.hts221addr, 0x36)
            h0_t0_out_h = self.i2cbus.read_byte_data(self.hts221addr, 0x37)
            h0_t0_out = (h0_t0_out_h << 8) | h0_t0_out_l
            
            h1_t0_out_l = self.i2cbus.read_byte_data(self.hts221addr, 0x3A)
            h1_t0_out_h = self.i2cbus.read_byte_data(self.hts221addr, 0x3B)
            h1_t0_out = (h1_t0_out_h << 8) | h1_t0_out_l
            
            h0_rh = self.i2cbus.read_byte_data(self.hts221addr, 0x30) / 2
            h1_rh = self.i2cbus.read_byte_data(self.hts221addr, 0x31) / 2
            
            h_rh = ((h_out - h0_t0_out) * (h1_rh - h0_rh)) / (h1_t0_out - h0_t0_out) + h0_rh
            logging.debug(f"Humidity: {h_rh} %")
            sensorData.setValue(h_rh)
            
        else:
            logging.warning("Humidity data not ready")
            return None
        
        self.latestSensorData = sensorData
        return sensorData
    