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

from programmingtheiot.data.ActuatorData import ActuatorData

class BaseActuatorSimTask():
    """
    Base actuator simulation task. This provides basic functionality for all actuator simulation tasks.
    
    """

    def __init__(self, name: str = ConfigConst.NOT_SET, typeID: int = ConfigConst.DEFAULT_ACTUATOR_TYPE, simpleName: str = "Actuator"):
        self.latestActuatorResponse = ActuatorData(typeID=typeID, name=name)
        self.latestActuatorResponse.setAsResponse()
        
        self.name = name
        self.typeID = typeID
        self.simpleName = simpleName
        self.lastKnownCommand = ConfigConst.DEFAULT_COMMAND
        self.lastKnownValue = ConfigConst.DEFAULT_VAL
        self.lastKnownState = ""
        
    def getLatestActuatorResponse(self) -> ActuatorData:
        """
        This can return the current ActuatorData response instance or a copy.
        """
        return self.latestActuatorResponse
    
    def getSimpleName(self) -> str:
        return self.simpleName
    
    def updateActuator(self, data: ActuatorData) -> ActuatorData:
        """
        NOTE: If 'data' is valid, the actuator-specific work can be delegated
        as follows:
         - if command is ON: call self._activateActuator()
         - if command is OFF: call self._deactivateActuator()
        
        Both of these methods will have a generic implementation (logging only) within
        this base class, although the sub-class may override if preferable.
        """
        if data and self.typeID==data.getTypeID():
            
            # check for repeat command with same command, value, and state
            if (self.lastKnownCommand==data.getCommand() and
                self.lastKnownValue==data.getValue() and
                self.lastKnownState==data.getStateData()):
                logging.debug(f"Received duplicate command for {self.name} actuator: {data.getCommand()}, {data.getValue()}, {data.getStateData()}")
                return None
            
            responseCode = ConfigConst.DEFAULT_STATUS
            
            if data.getCommand()==ConfigConst.COMMAND_ON:
                responseCode = self._activateActuator(data.getValue(), data.getStateData())
            elif data.getCommand()==ConfigConst.COMMAND_OFF:
                responseCode = self._deactivateActuator(data.getValue(), data.getStateData())
            else:
                logging.error(f"Invalid command for {self.name} actuator: {data.getCommand()}")
                responseCode = -1
                
            self.lastKnownCommand = data.getCommand()
            self.lastKnownValue = data.getValue()
            self.lastKnownState = data.getStateData()
            
            actuatorResponse = ActuatorData()
            actuatorResponse.updateData(data)
            actuatorResponse.setStatusCode(responseCode)
            actuatorResponse.setAsResponse()
            
            self.latestActuatorResponse.updateData(actuatorResponse)
            
            return actuatorResponse
            
        return None
        
    def _activateActuator(self, val: float = ConfigConst.DEFAULT_VAL, stateData: str = None) -> int:
        """
        Implement basic logging. Actuator-specific functionality should be implemented by sub-class.
        
        @param val The actuation activation value to process.
        @param stateData The string state data to use in processing the command.
        """
        msg = f"""
*******
* O N *
*******
{self.name} VALUE -> {val}
=======
        """
        
        logging.info(f"Simulating {self.name} actuator ON: {msg}")
        
        return 0
        
    def _deactivateActuator(self, val: float = ConfigConst.DEFAULT_VAL, stateData: str = None) -> int:
        """
        Implement basic logging. Actuator-specific functionality should be implemented by sub-class.
        
        @param val The actuation activation value to process.
        @param stateData The string state data to use in processing the command.
        """
        msg = f"""
*******
* OFF *
*******
        """
        
        logging.info(f"Simulating {self.name} actuator OFF: {msg}")
        
        return 0
        