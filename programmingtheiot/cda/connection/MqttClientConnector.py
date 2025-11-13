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
import ssl

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
        
        self.enableCrypt = self.config.getBoolean(
            ConfigConst.MQTT_GATEWAY_SERVICE,
            ConfigConst.ENABLE_CRYPT_KEY
        )
        
        self.caFileName = self.config.getProperty(
            ConfigConst.MQTT_GATEWAY_SERVICE,
            ConfigConst.CERT_FILE_KEY,
            ConfigConst.DEFAULT_CRED_FILE_NAME
        )
        
        self.mqttClient = None
        
        logging.info(
f"""
    MQTT Client ID:     {self.clientID}
    MQTT Broker Host:   {self.host}
    MQTT Broker Port:   {self.port}
    MQTT Keep Alive:    {self.keepAlive}                     
    MQTT Encryption:    {self.enableCrypt}
    MQTT CA File Name:  {self.caFileName}     
"""
        )
        
        self.dataMessageListener = None

    def connectClient(self, cleanSession: bool = True) -> bool:
        if not self.mqttClient:
            self.mqttClient = mqttClient.Client(client_id=self.clientID, clean_session=cleanSession)
            
            try:
                if self.enableCrypt:
                    logging.info("Enabling TLS Encryption...")
                    self.port = self.config.getInteger(
                        ConfigConst.MQTT_GATEWAY_SERVICE,
                        ConfigConst.SECURE_PORT_KEY,
                        ConfigConst.DEFAULT_MQTT_SECURE_PORT
                    )
                    self.mqttClient.tls_set(self.caFileName, tls_version=ssl.PROTOCOL_TLS_CLIENT)
                    
            except Exception as e:
                logging.error("TLS Encryption failed.")
                raise e
            
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
        logging.debug(f"Client connected to broker: {str(client)}")
        
    def onDisconnect(self, client, userdata, rc):
        logging.debug(f"Client disconnected from broker: {str(client)}")
        
    def onMessage(self, client, userdata, msg):
        if msg.payload:
            logging.debug(f"Message received with payload: {str(msg.payload.decode('utf-8'))}")
        else:
            logging.debug(f"Message received with no payload: {str(msg)}")
            
    def onPublish(self, client, userdata, mid):
        # logging.debug(f"Message published: {str(client)}")
        pass
    
    def onSubscribe(self, client, userdata, mid, granted_qos):
        logging.debug(f"Client subscribed: {str(client)}")
    
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
    
    def publishMessage(self, resource: ResourceNameEnum = None, msg: str = None, qos: int = ConfigConst.DEFAULT_QOS) -> bool:
        
        # validations
        if not resource:
            # logging.warning("No topic specified to publish to.")
            return False
        if not msg:
            # logging.warning(f"Cannot publish empty message to topic {resource}")
            return False
        if not 0 <= qos <= 2:
            qos = ConfigConst.DEFAULT_QOS
            
        # publish
        try:
            info = self.mqttClient.publish(topic=resource.value, payload=msg, qos=qos)
            info.wait_for_publish()
            return True
        except Exception as e:
            # logging.error(f"Publish failed: {str(e)}")
            return False
    
    def subscribeToTopic(self, resource: ResourceNameEnum = None, callback = None, qos: int = ConfigConst.DEFAULT_QOS) -> bool:
        
        # validations
        if not resource:
            logging.warning("No topic specified to subscribe to.")
            return False
            return False
        if not 0 <= qos <= 2:
            qos = ConfigConst.DEFAULT_QOS
        
        # subscribe
        try:
            logging.debug(f"Subscribing to {resource.value}")
            self.mqttClient.subscribe(topic=resource.value, qos=qos)
            return True
        except Exception as e:
            logging.error(f"Publish failed: {str(e)}")
            return False
            
    def unsubscribeFromTopic(self, resource: ResourceNameEnum = None) -> bool:
        
        # validations
        if not resource:
            logging.warning("No topic specified to subscribe to.")
            return False
        
        # unsubscribe
        logging.debug(f"Unsubscribing from {resource.value}")
        self.mqttClient.unsubscribe(resource.value)
        return True

    def setDataMessageListener(self, listener: IDataMessageListener = None) -> bool:
        # TODO there arent any notifications to the listener yet
        if not self.dataMessageListener:
            self.dataMessageListener = listener
            return True
        return False
