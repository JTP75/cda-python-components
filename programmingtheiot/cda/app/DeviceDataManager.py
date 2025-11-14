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

from programmingtheiot.cda.connection.CoapClientConnector import CoapClientConnector
from programmingtheiot.cda.connection.MqttClientConnector import MqttClientConnector
from programmingtheiot.cda.connection.RedisPersistenceAdapter import RedisPersistenceAdapter

from programmingtheiot.cda.system.ActuatorAdapterManager import ActuatorAdapterManager
from programmingtheiot.cda.system.SensorAdapterManager import SensorAdapterManager
from programmingtheiot.cda.system.SystemPerformanceManager import SystemPerformanceManager

import programmingtheiot.common.ConfigConst as ConfigConst
from programmingtheiot.common.ConfigUtil import ConfigUtil

from programmingtheiot.common.IDataMessageListener import IDataMessageListener
from programmingtheiot.common.ISystemPerformanceDataListener import ISystemPerformanceDataListener
from programmingtheiot.common.ITelemetryDataListener import ITelemetryDataListener
from programmingtheiot.common.ResourceNameEnum import ResourceNameEnum

from programmingtheiot.data.DataUtil import DataUtil
from programmingtheiot.data.ActuatorData import ActuatorData
from programmingtheiot.data.SensorData import SensorData
from programmingtheiot.data.SystemPerformanceData import SystemPerformanceData

logging.basicConfig(format = '%(asctime)s:%(filename)s:%(levelname)s:%(message)s', level = logging.DEBUG)

class DeviceDataManager(IDataMessageListener):
    """
    TODO add desc pls
    """
    
    def __init__(self, noComms: bool = False):
        self.configUtil = ConfigUtil()
        
        # data collection config
        self.enableSystemPerformanceData = self.configUtil.getBoolean(
            section=ConfigConst.CONSTRAINED_DEVICE,
            key=ConfigConst.ENABLE_SYSTEM_PERF_KEY
        )
        self.enableSensing = self.configUtil.getBoolean(
            section=ConfigConst.CONSTRAINED_DEVICE,
            key=ConfigConst.ENABLE_SENSING_KEY
        )
        self.enableActuation = self.configUtil.getBoolean(
            section=ConfigConst.CONSTRAINED_DEVICE,
            key=ConfigConst.ENABLE_ACTUATION_KEY
        )
        
        # communication config
        self.enableMqttClient = self.configUtil.getBoolean(
            section=ConfigConst.CONSTRAINED_DEVICE,
            key=ConfigConst.ENABLE_MQTT_CLIENT_KEY
        ) and not noComms
        self.enableCoapClient = self.configUtil.getBoolean(
            section=ConfigConst.CONSTRAINED_DEVICE,
            key=ConfigConst.ENABLE_COAP_CLIENT_KEY
        ) and not noComms
        self.enableRedis = self.configUtil.getBoolean(
            section=ConfigConst.CONSTRAINED_DEVICE,
            key=ConfigConst.ENABLE_REDIS_KEY
        ) and not noComms
        
        # data range config
        self.handleTemperatureChangeOnDevice = self.configUtil.getBoolean(
            section=ConfigConst.CONSTRAINED_DEVICE,
            key=ConfigConst.HANDLE_TEMP_CHANGE_ON_DEVICE_KEY
        )
        self.triggerHvacTemperatureFloor = self.configUtil.getFloat(
            section=ConfigConst.CONSTRAINED_DEVICE,
            key=ConfigConst.TRIGGER_HVAC_TEMP_FLOOR_KEY
        )
        self.triggerHvacTemperatureCeiling = self.configUtil.getFloat(
            section=ConfigConst.CONSTRAINED_DEVICE,
            key=ConfigConst.TRIGGER_HVAC_TEMP_CEILING_KEY
        )
        
        self.systemPerformanceManager   = None
        self.sensorAdapterManager       = None
        self.actuatorAdapterManager     = None
        
        self.actuatorResponseCache = {}
        
        self.mqttClient     = None
        self.coapClient     = None
        self.coapServer     = None
        self.redisClient    = None
        
        if self.enableMqttClient:
            self.mqttClient = MqttClientConnector()
            self.mqttClient.setDataMessageListener(self)
        if self.enableCoapClient:
            self.coapClient = CoapClientConnector()
            self.coapClient.setDataMessageListener(self)
        if self.enableRedis:
            self.redisClient = RedisPersistenceAdapter()
        
        if self.enableSystemPerformanceData:
            self.systemPerformanceManager = SystemPerformanceManager()
            self.systemPerformanceManager.setDataMessageListener(self)
            logging.info("SystemPerformanceManager enabled.")
        
        if self.enableSensing:
            self.sensorAdapterManager = SensorAdapterManager(self)
            self.sensorAdapterManager.setDataMessageListener(self)
            logging.info("SensorAdapterManager enabled.")
            
        if self.enableActuation:
            self.actuatorAdapterManager = ActuatorAdapterManager(self)
            logging.info("ActuatorAdapterManager enabled.")
        
    def getLatestActuatorDataResponseFromCache(self, name: str = None) -> ActuatorData:
        """
        Retrieves the named actuator data (response) item from the internal data cache.
        
        @param name
        @return ActuatorData
        """
        pass
        
    def getLatestSensorDataFromCache(self, name: str = None) -> SensorData:
        """
        Retrieves the named sensor data item from the internal data cache.
        
        @param name
        @return SensorData
        """
        pass
    
    def getLatestSystemPerformanceDataFromCache(self, name: str = None) -> SystemPerformanceData:
        """
        Retrieves the named system performance data from the internal data cache.
        
        @param name
        @return SystemPerformanceData
        """
        pass
    
    def handleActuatorCommandMessage(self, data: ActuatorData) -> ActuatorData:
        """
        This callback method will be invoked by the connection that's handling
        an incoming ActuatorData command message.
        
        @param data The incoming ActuatorData command message.
        @return new ActuatorData object
        """
        logging.debug(f"Handling actuator command message: {data}")
        
        if data:
            logging.debug(f"Processing actuator command...")
            # TODO something here
            return self.actuatorAdapterManager.sendActuatorCommand(data)
        else:
            logging.warning("Incoming actuator command is invalid (None). Ignoring.")
            return None
    
    def handleActuatorCommandResponse(self, data: ActuatorData) -> bool:
        """
        This callback method will be invoked by the actuator manager that just
        processed an ActuatorData command, which creates a new ActuatorData
        instance and sets it as a response before calling this method.
        
        @param data The incoming ActuatorData response message.
        @return boolean
        """
        logging.debug(f"Handling actuator command response: {data}")
        
        if data:
            logging.debug(f"Processing actuator response...")
            self.actuatorResponseCache[data.getName()] = data
            self._handleUpstreamTransmission(
                resourceName=ResourceNameEnum.CDA_ACTUATOR_RESPONSE_RESOURCE,
                msg=DataUtil().actuatorDataToJson(data)
            )
            return True
        else:
            logging.warning("Incoming actuator response is invalid (None). Ignoring.")
            return False
    
    def handleIncomingMessage(self, resourceEnum: ResourceNameEnum, msg: str) -> bool:
        """
        This callback method is generic and designed to handle any incoming string-based
        message, which will likely be JSON-formatted and need to be converted to the appropriate
        data type. You may not need to use this callback at all.
        
        @param data The incoming JSON message.
        @return boolean
        """
        logging.debug(f"Handling incoming message: {msg}")
        if msg:
            logging.debug("Processing incoming message...")
            self._handleIncomingDataAnalysis(msg)
            return True
        else:
            logging.warning("Incoming message is invalid (None). Ignoring.")
            return False
    
    def handleSensorMessage(self, data: SensorData) -> bool:
        """
        This callback method will be invoked by the sensor manager that just processed
        a new sensor reading, which creates a new SensorData instance that will be
        passed to this method.
        
        @param data The incoming SensorData message.
        @return boolean
        """
        logging.info(f"Handling sensor message: {data}")
        if data:
            logging.debug("Processing sensor data...")
            
            if self.redisClient:
                self.redisClient.storeSensorData(ResourceNameEnum.CDA_SENSOR_MSG_RESOURCE, data)
            self._handleSensorDataAnalysis(data=data)
            
            jsonData = DataUtil().sensorDataToJson(data)
            self._handleUpstreamTransmission(
                resourceName=ResourceNameEnum.CDA_SENSOR_MSG_RESOURCE, 
                msg=jsonData
            )
            
            return True
        
        else:
            logging.warning("Incoming sensor data is invalid (None). Ignoring.")
            return False
            
    def handleSystemPerformanceMessage(self, data: SystemPerformanceData) -> bool:
        """
        This callback method will be invoked by the system performance manager that just
        processed a new sensor reading, which creates a new SystemPerformanceData instance
        that will be passed to this method.
        
        @param data The incoming SystemPerformanceData message.
        @return boolean
        """
        
        logging.debug(f"Handling system performance message: {data}")
        if data:
            logging.debug("System performance data OK.")
            return True
        else:
            logging.warning("Incoming system performance data is invalid (None). Ignoring.")
            return False
    
    def setSystemPerformanceDataListener(self, listener: ISystemPerformanceDataListener = None):
        self.systemPerformanceManager.setDataMessageListener(listener)
            
    def setTelemetryDataListener(self, name: str = None, listener: ITelemetryDataListener = None):
        self.sensorAdapterManager.setDataMessageListener(name, listener)
            
    def startManager(self):
        logging.info("Starting DeviceDataManager...")
        
        if self.systemPerformanceManager:
            self.systemPerformanceManager.startManager()
        
        if self.sensorAdapterManager:
            self.sensorAdapterManager.startManager()
            
        if self.redisClient:
            self.redisClient.connectClient()
            
        if self.mqttClient:
            self.mqttClient.connectClient()
            self.mqttClient.subscribeToTopic(
                resource=ResourceNameEnum.CDA_ACTUATOR_CMD_RESOURCE, 
                callback=None,
                qos=ConfigConst.DEFAULT_QOS
            )
            
        logging.info("DeviceDataManager started.")
        
    def stopManager(self):
        logging.info("Stopping DeviceDataManager...")
	
        if self.systemPerformanceManager:
            self.systemPerformanceManager.stopManager()
        
        if self.sensorAdapterManager:	
            self.sensorAdapterManager.stopManager()
            
        if self.redisClient:
            self.redisClient.disconnectClient()
            
        if self.mqttClient:
            self.mqttClient.unsubscribeFromTopic(ResourceNameEnum.CDA_ACTUATOR_CMD_RESOURCE)
            self.mqttClient.disconnectClient()
            
        logging.info("Stopped DeviceDataManager.")
        
    def _handleIncomingDataAnalysis(self, msg: str):
        """
        Call this from handleIncomeMessage() to determine if there's
        any action to take on the message. Steps to take:
        1) Validate msg: Most will be ActuatorData, but you may pass other info as well.
        2) Convert msg: Use DataUtil to convert if appropriate.
        3) Act on msg: Determine what - if any - action is required, and execute.
        """
        logging.warning("Not implemented yet.")
        
    def _handleSensorDataAnalysis(self, resource = None, data: SensorData = None):
        """
        Call this from handleSensorMessage() to determine if there's
        any action to take on the message. Steps to take:
        1) Check config: Is there a rule or flag that requires immediate processing of data?
        2) Act on data: If # 1 is true, determine what - if any - action is required, and execute.
        """
        
        # this is the current 'model' step
        # right now, we only handle temperature changes and print warning for other sensor types
        # should be more later
        
        logging.debug(f"Handling sensor data analysis: {data}")
        if data and data.getTypeID()==ConfigConst.TEMP_SENSOR_TYPE:
            logging.debug("Analyzing sensor data...")
            if self.handleTemperatureChangeOnDevice:
                actuatorData = ActuatorData(typeID=ConfigConst.HVAC_ACTUATOR_TYPE)
                
                if data.getValue() > self.triggerHvacTemperatureCeiling:
                    actuatorData.setCommand(ConfigConst.COMMAND_ON)
                    actuatorData.setValue(self.triggerHvacTemperatureCeiling)
                elif data.getValue() < self.triggerHvacTemperatureFloor:
                    actuatorData.setCommand(ConfigConst.COMMAND_ON)
                    actuatorData.setValue(self.triggerHvacTemperatureFloor)
                else:
                    actuatorData.setCommand(ConfigConst.COMMAND_OFF)
                    
                self.handleActuatorCommandMessage(actuatorData)
            else:
                logging.debug("Device is not configured to handle locally. Ignoring.")
        else:
            logging.warning("Sensor data is invalid (null or type mismatch). Ignoring.")
        
    def _handleUpstreamTransmission(self, resourceName: ResourceNameEnum, msg: str):
        """
        Call this from handleActuatorCommandResponse(), handlesensorMessage(), and handleSystemPerformanceMessage()
        to determine if the message should be sent upstream. Steps to take:
        1) Check connection: Is there a client connection configured (and valid) to a remote MQTT or CoAP server?
        2) Act on msg: If # 1 is true, send message upstream using one (or both) client connections.
        """
        logging.info(f"Handling upstream transmission: {resourceName}")
        if self.mqttClient:
            if self.mqttClient.publishMessage(resource=resourceName, msg=msg):
                logging.debug("Published to MQTT")
            else:
                logging.error("Failed to publish to MQTT")
        if self.coapClient:
            if self.coapClient.sendPutRequest(resource=resourceName, payload=msg):
                logging.debug("PUT to CoAP")
            else:
                logging.error("Failed to PUT to CoAP")
        
