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
import paho.mqtt.client as mqttClient

import programmingtheiot.common.ConfigConst as ConfigConst

from programmingtheiot.common.ConfigUtil import ConfigUtil
from programmingtheiot.common.IDataMessageListener import IDataMessageListener
from programmingtheiot.common.ResourceNameEnum import ResourceNameEnum

from programmingtheiot.cda.connection.IPubSubClient import IPubSubClient

class MqttClientConnector(IPubSubClient):
    """
    Shell representation of class for student implementation.
    
    """
    
    @property
    def connected(self) -> bool:
        if self.mqttClient:
            return self.mqttClient.is_connected()
        return False

    def __init__(self, clientID: str = None):
        """
        Default constructor. This will set remote broker information and client connection
        information based on the default configuration file contents.
        
        @param clientID Defaults to None. Can be set by caller. If this is used, it's
        critically important that a unique, non-conflicting name be used so to avoid
        causing the MQTT broker to disconnect any client using the same name. With
        auto-reconnect enabled, this can cause a race condition where each client with
        the same clientID continuously attempts to re-connect, causing the broker to
        disconnect the previous instance.
        """
  
        self.config = ConfigUtil() 
                
        self.host = self.config.getProperty(
            ConfigConst.MQTT_GATEWAY_SERVICE,
            ConfigConst.HOST_KEY,
            ConfigConst.DEFAULT_HOST
        )
        
        self.port = self.config.getInteger(
            ConfigConst.MQTT_GATEWAY_SERVICE,
            ConfigConst.PORT_KEY,
            ConfigConst.DEFAULT_MQTT_PORT
        )
        
        self.keepAlive = self.config.getInteger(
            ConfigConst.MQTT_GATEWAY_SERVICE,
            ConfigConst.KEEP_ALIVE_KEY,
            ConfigConst.DEFAULT_KEEP_ALIVE
        )
        
        self.defaultQos = self.config.getInteger(
            ConfigConst.MQTT_GATEWAY_SERVICE,
            ConfigConst.DEFAULT_QOS_KEY,
            ConfigConst.DEFAULT_QOS
        )
        
        self.clientID = self.config.getProperty(
            ConfigConst.CONSTRAINED_DEVICE,
            ConfigConst.DEVICE_LOCATION_ID_KEY,
            clientID if clientID else "CDA_MQTT_CLIENT_ID_001"
        )
        
        self.mqttClient = None
        
        logging.info(
f"""
    MQTT Client ID:     {self.clientID}
    MQTT Broker Host:   {self.host}
    MQTT Broker Port:   {self.port}
    MQTT Keep Alive:    {self.keepAlive}                     
"""
        )
        
        self.dataMessageListener = None

    def connectClient(self, cleanSession: bool = True) -> bool:
        if not self.mqttClient:
            self.mqttClient = mqttClient.Client(client_id=self.clientID, clean_session=cleanSession)
            
            self.mqttClient.on_connect = self.onConnect
            self.mqttClient.on_disconnect = self.onDisconnect
            self.mqttClient.on_message = self.onMessage
            self.mqttClient.on_publish = self.onPublish
            self.mqttClient.on_subscribe = self.onSubscribe
            
        if not self.mqttClient.is_connected():
            logging.info(f"MQTT client connecting to broker (host={self.host}, port={self.port})")
            self.mqttClient.connect(self.host, self.port, self.keepAlive)
            self.mqttClient.loop_start()
            return True
            
        else:
            logging.warning(f"MQTT client already connected to broker (host={self.host}, port={self.port}), ignoring request.")
            return False
        
    def disconnectClient(self) -> bool:
        if self.mqttClient.is_connected():
            logging.info(f"MQTT client disconnecting from broker (host={self.host}, port={self.port})")
            self.mqttClient.loop_stop()
            self.mqttClient.disconnect()
            return True
        else:
            logging.warning(f"MQTT client already disconnected from broker (host={self.host}, port={self.port}), ignoring.")
            return False
        
    def onConnect(self, client, userdata, flags, rc):
        logging.debug(f"Client connected (id={client._client_id})")
        
    def onDisconnect(self, client, userdata, rc):
        logging.debug(f"Client disconnected (id={client._client_id})")
        
    def onMessage(self, client, userdata, msg):
        logging.debug(f"Someone posted a message: {msg}")
            
    def onPublish(self, client, userdata, mid):
        logging.debug("Someone published!")
    
    def onSubscribe(self, client, userdata, mid, granted_qos):
        logging.debug("Someone subscribed!")
    
    def onActuatorCommandMessage(self, client, userdata, msg):
        """
        This callback is defined as a convenience, but does not
        need to be used and can be ignored.
        
        It's simply an example for how you can create your own
        custom callback for incoming messages from a specific
        topic subscription (such as for actuator commands).
        
        @param client The client reference context.
        @param userdata The user reference context.
        @param msg The message context, including the embedded payload.
        """
        pass
    
    def publishMessage(self, resource: ResourceNameEnum = None, msg: str = None, qos: int = ConfigConst.DEFAULT_QOS):
        pass
    
    def subscribeToTopic(self, resource: ResourceNameEnum = None, callback = None, qos: int = ConfigConst.DEFAULT_QOS):
        pass
    
    def unsubscribeFromTopic(self, resource: ResourceNameEnum = None):
        pass

    def setDataMessageListener(self, listener: IDataMessageListener = None) -> bool:
        pass
