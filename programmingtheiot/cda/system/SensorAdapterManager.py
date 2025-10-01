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

from apscheduler.schedulers.background import BackgroundScheduler

import programmingtheiot.common.ConfigConst as ConfigConst

from programmingtheiot.common.ConfigUtil import ConfigUtil
from programmingtheiot.common.IDataMessageListener import IDataMessageListener

from programmingtheiot.cda.sim.SensorDataGenerator import SensorDataGenerator
from programmingtheiot.cda.sim.HumiditySensorSimTask import HumiditySensorSimTask
from programmingtheiot.cda.sim.TemperatureSensorSimTask import TemperatureSensorSimTask
from programmingtheiot.cda.sim.PressureSensorSimTask import PressureSensorSimTask

class SensorAdapterManager(object):
    """
    TODO write a desc pls
    """

    def __init__(self, dml: IDataMessageListener = None):
        self.configUtil = ConfigUtil()
        
        self.useSimulator = not self.configUtil.getBoolean(
            section=ConfigConst.CONSTRAINED_DEVICE,
            key=ConfigConst.ENABLE_EMULATOR_KEY
        )
        
        self.useEmulator = self.configUtil.getUseEmulator(
        )
        
        self.pollRate = self.configUtil.getInteger(
            section=ConfigConst.CONSTRAINED_DEVICE,
            key=ConfigConst.POLL_CYCLES_KEY,
            defaultVal=ConfigConst.DEFAULT_POLL_CYCLES
        )
        if self.pollRate <= 0: # just in case
            self.pollRate = ConfigConst.DEFAULT_POLL_CYCLES
        
        self.locationID = self.configUtil.getProperty(
            section=ConfigConst.CONSTRAINED_DEVICE,
            key=ConfigConst.DEVICE_LOCATION_ID_KEY,
            defaultVal = ConfigConst.NOT_SET
        )
        
            
        self.scheduler = BackgroundScheduler()
        self.scheduler.add_job(
            self.handleTelemetry,
            'interval',
            seconds=self.pollRate,
            max_instances=2,
            coalesce=True,
            misfire_grace_time=15,
        )
        
        self.dataMessageListener = dml
        self.humidityAdapter = None
        self.pressureAdapter = None
        self.temperatureAdapter = None
        
        self._initEnvironmentalSensorTasks()
        
    def _initEnvironmentalSensorTasks(self):
        humidityFloor = self.configUtil.getFloat(
            section=ConfigConst.CONSTRAINED_DEVICE, 
            key=ConfigConst.HUMIDITY_SIM_FLOOR_KEY, 
            defaultVal=SensorDataGenerator.LOW_NORMAL_ENV_HUMIDITY
        )
        humidityCeiling = self.configUtil.getFloat(
            section=ConfigConst.CONSTRAINED_DEVICE, 
            key=ConfigConst.HUMIDITY_SIM_CEILING_KEY, 
            defaultVal=SensorDataGenerator.HI_NORMAL_ENV_HUMIDITY
        )
        
        pressureFloor = self.configUtil.getFloat(
            section=ConfigConst.CONSTRAINED_DEVICE, 
            key=ConfigConst.PRESSURE_SIM_FLOOR_KEY, 
            defaultVal=SensorDataGenerator.LOW_NORMAL_ENV_PRESSURE
        )
        pressureCeiling = self.configUtil.getFloat(
            section=ConfigConst.CONSTRAINED_DEVICE, 
            key=ConfigConst.PRESSURE_SIM_CEILING_KEY, 
            defaultVal=SensorDataGenerator.HI_NORMAL_ENV_PRESSURE
        )
        
        temperatureFloor = self.configUtil.getFloat(
            section=ConfigConst.CONSTRAINED_DEVICE, 
            key=ConfigConst.TEMP_SIM_FLOOR_KEY, 
            defaultVal=SensorDataGenerator.LOW_NORMAL_INDOOR_TEMP
        )
        temperatureCeiling = self.configUtil.getFloat(
            section=ConfigConst.CONSTRAINED_DEVICE, 
            key=ConfigConst.TEMP_SIM_CEILING_KEY, 
            defaultVal=SensorDataGenerator.HI_NORMAL_INDOOR_TEMP
        )
        
        if self.useSimulator:
            self.dataGenerator = SensorDataGenerator()
            
            humidityData = self.dataGenerator.generateDailyEnvironmentHumidityDataSet(
                minValue=humidityFloor, 
                maxValue=humidityCeiling,
                useSeconds=False
            )
            pressureData = self.dataGenerator.generateDailyEnvironmentPressureDataSet(
                minValue=pressureFloor, 
                maxValue=pressureCeiling,
                useSeconds=False
            )
            temperatureData = self.dataGenerator.generateDailyIndoorTemperatureDataSet(
                minValue=temperatureFloor, 
                maxValue=temperatureCeiling,
                useSeconds=False
            )
            
            self.humidityAdapter = HumiditySensorSimTask(dataSet=humidityData)
            self.pressureAdapter = PressureSensorSimTask(dataSet=pressureData)
            self.temperatureAdapter = TemperatureSensorSimTask(dataSet=temperatureData)
            
        elif self.useEmulator:
            
            heModule = import_module('programmingtheiot.cda.emulated.HumiditySensorEmulatorTask', 'HumiditySensorEmulatorTask')
            heClazz = getattr(heModule, 'HumiditySensorEmulatorTask')
            self.humidityAdapter = heClazz()
            
            peModule = import_module('programmingtheiot.cda.emulated.PressureSensorEmulatorTask', 'PressureSensorEmulatorTask')
            peClazz = getattr(peModule, 'PressureSensorEmulatorTask')
            self.pressureAdapter = peClazz()
            
            teModule = import_module('programmingtheiot.cda.emulated.TemperatureSensorEmulatorTask', 'TemperatureSensorEmulatorTask')
            teClazz = getattr(teModule, 'TemperatureSensorEmulatorTask')
            self.temperatureAdapter = teClazz()
        
        else:
            
            heModule = import_module('programmingtheiot.cda.emulated.HumiditySensorEmulatorTask', 'HumiditySensorEmulatorTask')
            heClazz = getattr(heModule, 'HumiditySensorEmulatorTask')
            self.humidityAdapter = heClazz()
            
            peModule = import_module('programmingtheiot.cda.emulated.PressureSensorEmulatorTask', 'PressureSensorEmulatorTask')
            peClazz = getattr(peModule, 'PressureSensorEmulatorTask')
            self.pressureAdapter = peClazz()
            
            teModule = import_module('programmingtheiot.cda.emulated.TemperatureSensorEmulatorTask', 'TemperatureSensorEmulatorTask')
            teClazz = getattr(teModule, 'TemperatureSensorEmulatorTask')
            self.temperatureAdapter = teClazz()
            
        

    def handleTelemetry(self):
        humidityData = self.humidityAdapter.generateTelemetry()
        pressureData = self.pressureAdapter.generateTelemetry()
        temperatureData = self.temperatureAdapter.generateTelemetry()
        
        humidityData.setLocationID(self.locationID)
        pressureData.setLocationID(self.locationID)
        temperatureData.setLocationID(self.locationID)
        
        logging.debug(f"Generated Humidity Data: {humidityData}")
        logging.debug(f"Generated Pressure Data: {pressureData}")
        logging.debug(f"Generated Temperature Data: {temperatureData}")
        
        if self.dataMessageListener:
            self.dataMessageListener.handleSensorMessage(humidityData)
            self.dataMessageListener.handleSensorMessage(pressureData)
            self.dataMessageListener.handleSensorMessage(temperatureData)
        
    def setDataMessageListener(self, listener: IDataMessageListener) -> bool:
        if listener:
            self.dataMessageListener = listener
            return True
        return False
    
    def startManager(self) -> bool:
        logging.info("Started SensorAdapterManager.")
        
        if not self.scheduler.running:
            self.scheduler.start()
            return True
        else:
            logging.info("SensorAdapterManager scheduler already started. Ignoring.")
            return False
        
    def stopManager(self) -> bool:
        logging.info("Stopped SensorAdapterManager.")
        
        try:
            self.scheduler.shutdown()
            return True
        except:
            logging.info("SensorAdapterManager scheduler already stopped. Ignoring.")
            return False
