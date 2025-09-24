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

from programmingtheiot.common.ConfigConst import ConfigConst

from programmingtheiot.cda.sim.BaseSensorSimTask import BaseSensorSimTask
from programmingtheiot.cda.sim.SensorDataGenerator import SensorDataGenerator, SensorDataSet

from programmingtheiot.data.SensorData import SensorData

class PressureSensorSimTask(BaseSensorSimTask):
    """
    Sensor simulation task for pressure. This object simulates a digital barometer for testing and development purposes.
    
    """

    def __init__(self, dataSet: SensorDataSet = None):
        super(PressureSensorSimTask, self).__init__(
            name=ConfigConst.PRESSURE_SENSOR_NAME,
            typeID=ConfigConst.PRESSURE_SENSOR_TYPE,
            dataSet=dataSet,
            minVal=SensorDataGenerator.LOW_NORMAL_ENV_PRESSURE,
            maxVal=SensorDataGenerator.HI_NORMAL_ENV_PRESSURE
        )
    