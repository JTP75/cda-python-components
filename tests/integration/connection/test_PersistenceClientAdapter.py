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

import programmingtheiot.common.ConfigConst as ConfigConst

from programmingtheiot.common.ResourceNameEnum import ResourceNameEnum

from programmingtheiot.cda.connection.RedisPersistenceAdapter import RedisPersistenceAdapter

from programmingtheiot.data.DataUtil import DataUtil
from programmingtheiot.data.SensorData import SensorData

class PersistenceClientAdapterTest(unittest.TestCase):
    """
    This test case class contains very basic unit tests for
    RedisPersistenceAdapter. 
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
        
        self.assertTrue(self.rpa.storeSensorData(sData))
        
        self.rpa.disconnectClient()
    
if __name__ == "__main__":
    unittest.main()
    