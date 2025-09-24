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
from programmingtheiot.cda.sim.BaseActuatorSimTask import BaseActuatorSimTask

class HvacActuatorSimTask(BaseActuatorSimTask):
    """
    Actuator simulation task for HVAC system. Simulation for testing and development purposes.
    """

    def __init__(self):
        super(HvacActuatorSimTask, self).__init__(
            name=ConfigConst.HVAC_ACTUATOR_NAME,
            typeID=ConfigConst.HVAC_ACTUATOR_TYPE,
            simpleName="HVAC"
        )
        