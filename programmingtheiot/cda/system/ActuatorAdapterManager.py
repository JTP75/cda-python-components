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

from importlib import import_module

import programmingtheiot.common.ConfigConst as ConfigConst
from programmingtheiot.common.ConfigUtil import ConfigUtil
from programmingtheiot.common.IDataMessageListener import IDataMessageListener

from programmingtheiot.data.ActuatorData import ActuatorData

from programmingtheiot.cda.sim.HvacActuatorSimTask import HvacActuatorSimTask
from programmingtheiot.cda.sim.HumidifierActuatorSimTask import HumidifierActuatorSimTask

class ActuatorAdapterManager(object):
    """
    TODO add a desc pls	
    """
    
    def __init__(self, dml: IDataMessageListener = None):
        self.configUtil = ConfigUtil()		
  
        self.useEmulator = self.configUtil.getBoolean(
            section=ConfigConst.CONSTRAINED_DEVICE,
            key=ConfigConst.ENABLE_EMULATOR_KEY
        )
        self.locationID = self.configUtil.getProperty(
            section=ConfigConst.CONSTRAINED_DEVICE,
            key=ConfigConst.DEVICE_LOCATION_ID_KEY,
            defaultVal=ConfigConst.NOT_SET
        )
        
        self.dataMessageListener = dml
        
        logging.info(f"The ActuatorAdapaterManager is configured to use {'emulators' if self.useEmulator else 'simulators'}.")
         
        self._initEnvironmentalActuationTasks()
        
    def _initEnvironmentalActuationTasks(self):
        self.humidifierActuator = HumidifierActuatorSimTask()
        self.hvacActuator = HvacActuatorSimTask()
        self.ledActuator = None

    def sendActuatorCommand(self, data: ActuatorData) -> ActuatorData:
        responseData = None
        
        if data and not data.isResponseFlagEnabled():
            if data.getLocationID()==self.locationID:
                
                if data.getTypeID() == ConfigConst.HUMIDIFIER_ACTUATOR_TYPE and self.humidifierActuator:
                    responseData = self.humidifierActuator.updateActuator(data)
                elif data.getTypeID() == ConfigConst.HVAC_ACTUATOR_TYPE and self.hvacActuator:
                    responseData = self.hvacActuator.updateActuator(data)
                elif data.getTypeID() == ConfigConst.LED_ACTUATOR_TYPE and self.ledActuator:
                    responseData = self.ledActuator.updateActuator(data)
                else:
                    logging.warning(f"No valid actuator type. Ignoring actuation for type: {data.getTypeID()}")
                    
                # TODO dml callback for DeviceDataManager will go here
            else:
                logging.warning(f"Location ID doesn't match. Ignoring actuation: (me) {self.locationID} != (you) {data.getLocationID()}")
        else:
            logging.warning("Actuator request received. Message is empty or response. Ignoring.")
            
        return responseData
    
    def setDataMessageListener(self, listener: IDataMessageListener) -> bool:
        if listener:
            self.dataMessageListener = listener
            return True
        return False
