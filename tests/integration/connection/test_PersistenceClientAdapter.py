#####
# 
# This class is part of the Programming the Internet of Things
# project, and is available via the MIT License, which can be
# found in the LICENSE file at the top level of this repository.
# 
# Copyright (c) 2020 - 2025 by Andrew D. King
# 

import logging
import unittest
import time

import redis

import programmingtheiot.common.ConfigConst as ConfigConst

from programmingtheiot.common.ResourceNameEnum import ResourceNameEnum

from programmingtheiot.cda.connection.RedisPersistenceAdapter import RedisPersistenceAdapter

from programmingtheiot.data.DataUtil import DataUtil
from programmingtheiot.data.SensorData import SensorData

class PersistenceClientAdapterTest(unittest.TestCase):
    """
    This test case class contains very basic unit tests for
    RedisPersistenceAdapter. 
    
    NOTE all the tests here require a running Redis server
    instance on localhost:6379 unless otherwise configured.
    For Ubuntu, you can install Redis via snap using
    
    ```
    sudo snap install redis
    ```
    
    and start/stop the server using
    
    ```
    sudo snap start redis
    sudo snap stop redis
    ```
    """
    
    @classmethod
    def setUpClass(self):
        logging.basicConfig(format = '%(asctime)s:%(module)s:%(levelname)s:%(message)s', level = logging.DEBUG)
        
    def setUp(self):
        self.rpa = RedisPersistenceAdapter()

    def tearDown(self):
        if self.rpa.connected:
            self.rpa.disconnectClient()

    def testConnectClient(self):
        self.assertTrue(self.rpa.connectClient())
        self.assertTrue(self.rpa.connected)
        
    def testDisconnectClient(self):
        self.rpa.connectClient()
        self.assertTrue(self.rpa.disconnectClient())
        self.assertFalse(self.rpa.connected)
        
    def testStoreSensorData(self):
        self.rpa.connectClient()
        
        sData = SensorData()
        sData.setName(ConfigConst.HUMIDITY_SENSOR_NAME)
        sData.setTypeID(ConfigConst.HUMIDITY_SENSOR_TYPE)
        sData.setValue(55.0)
        
        self.assertTrue(self.rpa.storeSensorData(ResourceNameEnum.CDA_SENSOR_MSG_RESOURCE, sData))
        
        # check the server manually to see if the data is there
        time.sleep(1)
        sDataOut = None
        with redis.Redis(host=self.rpa.host, port=self.rpa.port) as testCli:
            sDataJsonOut = testCli.get(ResourceNameEnum.CDA_SENSOR_MSG_RESOURCE.value)
            sDataOut = DataUtil().jsonToSensorData(sDataJsonOut)
            
        self.assertIsNotNone(sDataOut)
        self.assertDictEqual(sData.__dict__, sDataOut.__dict__)
        
        self.rpa.disconnectClient()
    
if __name__ == "__main__":
    unittest.main()
    