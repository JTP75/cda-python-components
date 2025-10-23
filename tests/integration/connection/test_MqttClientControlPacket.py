import logging
import unittest

from time import sleep

import programmingtheiot.common.ConfigConst as ConfigConst

from programmingtheiot.cda.connection.MqttClientConnector import MqttClientConnector
from programmingtheiot.common.ConfigUtil import ConfigUtil
from programmingtheiot.common.ResourceNameEnum import ResourceNameEnum
from programmingtheiot.common.DefaultDataMessageListener import DefaultDataMessageListener
from programmingtheiot.data.ActuatorData import ActuatorData
from programmingtheiot.data.SensorData import SensorData 
from programmingtheiot.data.SystemPerformanceData import SystemPerformanceData 
from programmingtheiot.data.DataUtil import DataUtil

class MqttClientControlPacketTest(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        logging.basicConfig(format = '%(asctime)s:%(module)s:%(levelname)s:%(message)s', level = logging.DEBUG)
        logging.info("Executing the MqttClientControlPacketTest class...")
        
        self.cfg = ConfigUtil()
        
        # NOTE: Be sure to use a DIFFERENT clientID than that which is used
        # for your CDA when running separately from this test
        # 
        # The clientID shown below is an example only - please use your own
        # unique value for this test
        self.mcc = MqttClientConnector(clientID = "MyTestMqttClient")
        
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def testConnectAndDisconnect(self):
        self.mcc.connectClient()
        sleep(2)
        self.assertTrue(self.mcc.connected)
        
        self.mcc.disconnectClient()
        sleep(2)
        self.assertFalse(self.mcc.connected)
    
    def testServerPing(self):
        self.mcc.connectClient()
        sleep(2)
        
        sleep(60)
        
        self.mcc.disconnectClient()
        sleep(2)
    
    def testPubSubQos1(self):
        qos = 1
        
        self.mcc.connectClient()
        sleep(2)
        
        self.mcc.subscribeToTopic(
            resource=ResourceNameEnum.CDA_ACTUATOR_CMD_RESOURCE,
            callback=None,
            qos=qos
        )
        sleep(2)
        
        self.mcc.publishMessage(
            resource=ResourceNameEnum.CDA_ACTUATOR_CMD_RESOURCE,
            msg="ground control to major tom",
            qos=qos
        )
        sleep(2)
        
        self.mcc.unsubscribeFromTopic(ResourceNameEnum.CDA_ACTUATOR_CMD_RESOURCE)
        sleep(2)
        
        self.mcc.disconnectClient()
        sleep(2)
        
    def testPubSubQos2(self):
        # seprate case for Qos = 2
        qos = 2
        
        self.mcc.connectClient()
        sleep(2)
        
        self.mcc.subscribeToTopic(
            resource=ResourceNameEnum.CDA_ACTUATOR_CMD_RESOURCE,
            callback=None,
            qos=qos
        )
        sleep(2)
        
        self.mcc.publishMessage(
            resource=ResourceNameEnum.CDA_ACTUATOR_CMD_RESOURCE,
            msg="major tom to ground control",
            qos=qos
        )
        sleep(2)
        
        self.mcc.unsubscribeFromTopic(ResourceNameEnum.CDA_ACTUATOR_CMD_RESOURCE)
        sleep(2)
        
        self.mcc.disconnectClient()
        sleep(2)