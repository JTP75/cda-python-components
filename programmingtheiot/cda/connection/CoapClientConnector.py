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
import socket

from coapthon import defines
from coapthon.client.helperclient import HelperClient
from coapthon.messages.option import Option
from coapthon.utils import parse_uri
from coapthon.utils import generate_random_token

import programmingtheiot.common.ConfigConst as ConfigConst

from programmingtheiot.common.ConfigUtil import ConfigUtil
from programmingtheiot.data.DataUtil import DataUtil

from programmingtheiot.common.ResourceNameEnum import ResourceNameEnum

from programmingtheiot.common.IDataMessageListener import IDataMessageListener
from programmingtheiot.cda.connection.IRequestResponseClient import IRequestResponseClient

logging.basicConfig(format = '%(asctime)s:%(filename)s:%(levelname)s:%(message)s', level = logging.DEBUG)

class CoapClientConnector(IRequestResponseClient):
    """
    Shell representation of class for student implementation.
    
    """
    
    def __init__(self, dataMsgListener: IDataMessageListener = None):
        
        config = ConfigUtil()
        self.dataMsgListener = dataMsgListener
        self.enableConfirmedMsgs = False
        self.coapClient = None
        self.observeRequests = { }
        
        self.host = config.getProperty( \
            ConfigConst.COAP_GATEWAY_SERVICE, ConfigConst.HOST_KEY, ConfigConst.DEFAULT_HOST)
        self.port = config.getInteger( \
            ConfigConst.COAP_GATEWAY_SERVICE, ConfigConst.PORT_KEY, ConfigConst.DEFAULT_COAP_PORT)
                
        self.includeDebugLogDetail = True
  
        try:
            tmp = socket.gethostbyname(self.host)
            if tmp:
                self.host = tmp
                self.uriPath = f"coap://{self.host}:{self.port}/"
                logging.info(f"CoAP client will connect to {self.host}")
                self._initClient()
            else:
                logging.error(f"Could not resolve host {self.host}")
                raise
            
        except socket.gaierror:
            logging.error(f"Failed to resolve host {self.host}")
    
    def sendDiscoveryRequest(self, timeout: int = IRequestResponseClient.DEFAULT_TIMEOUT) -> bool:
        
        path = self._createResourcePath(None, '.well-known/core')
        logging.info(f"DISCOVER {path}")
        
        request = self.coapClient.mk_request(defines.Codes.GET, path=path)
        request.token = generate_random_token(2)
        try:
            self.coapClient.send_request(request=request, timeout=timeout, callback=self._onDiscoveryResponse)
        except Exception as e:
            logging.error("CoAP server response failed")
            raise e
        
        return True

    def sendDeleteRequest(
        self, 
        resource: ResourceNameEnum = None, 
        name: str = None, 
        enableCON: bool = False, 
        timeout: int = IRequestResponseClient.DEFAULT_TIMEOUT
    ) -> bool:
        return False

    def sendGetRequest(
        self, 
        resource: ResourceNameEnum = None, 
        name: str = None, 
        enableCON: bool = False, 
        timeout: int = IRequestResponseClient.DEFAULT_TIMEOUT
    ) -> bool:
        
        if resource or name:
            path = self._createResourcePath(resource, name)
            logging.info(f"GET {path}")
            
            request = self.coapClient.mk_request(defines.Codes.GET, path=path)
            request.token = generate_random_token(2)
            
            try:
                if enableCON:
                    self.coapClient.send_request(request=request, timeout=timeout, \
                        callback=lambda resp: self._onGetResponse(resp, path))
                
                else:
                    request.type = defines.Types["NON"]
                    response = self.coapClient.send_request(request=request, timeout=timeout)
                    self._onGetResponse(response=response, resourcePath=path)
                    
            except Exception as e:
                logging.error("CoAP server response failed")
                raise e
            
            return True
            
        else:
            logging.warning(f"GET: No path or list provided")
        
        return False

    def sendPostRequest(
        self, 
        resource: ResourceNameEnum = None, 
        name: str = None, 
        enableCON: bool = False, 
        payload: str = None, 
        timeout: int = IRequestResponseClient.DEFAULT_TIMEOUT
    ) -> bool:
        return False

    def sendPutRequest(
        self, 
        resource: ResourceNameEnum = None, 
        name: str = None, 
        enableCON: bool = False, 
        payload: str = None, 
        timeout: int = IRequestResponseClient.DEFAULT_TIMEOUT
    ) -> bool:
        
        if resource or name:
            path = self._createResourcePath(resource, name)
            logging.info(f"PUT {path}")
            
            request = self.coapClient.mk_request(defines.Codes.PUT, path=path)
            request.token = generate_random_token(2)
            request.payload = payload
            
            try:
                if enableCON:
                    self.coapClient.send_request(request=request, timeout=timeout, \
                        callback=self._onPutResponse)
                
                else:
                    request.type = defines.Types["NON"]
                    response = self.coapClient.send_request(request=request, timeout=timeout)
                    self._onPutResponse(response=response)
                    
            except Exception as e:
                logging.error("CoAP server response failed")
                raise e
            
            return True
            
        else:
            logging.warning(f"PUT: No path or list provided")
        
        return False

    def setDataMessageListener(self, listener: IDataMessageListener = None) -> bool:
        if listener: 
            self.dataMsgListener = listener
            return True
        return False

    def startObserver(self, resource: ResourceNameEnum = None, name: str = None, ttl: int = IRequestResponseClient.DEFAULT_TTL) -> bool:
        return False

    def stopObserver(self, resource: ResourceNameEnum = None, \
        name: str = None, timeout: int = IRequestResponseClient.DEFAULT_TIMEOUT) -> bool:
        return False
    
    def _initClient(self):
        
        try:
            self.coapClient = HelperClient(server=(self.host, self.port))
            logging.info(f"Client created. Will invoke resources at {self.uriPath}")
        except Exception as e:
            logging.error(f"Failed to create CoAP client to {self.uriPath}")
            raise e # just throw
        
    def _createResourcePath(self, resource: ResourceNameEnum, name: str = None) -> str:
        
        path = ""
        hasResource = False
        if resource:
            path += resource.value
            hasResource = True
        if name:
            if hasResource:
                path += "/"
            path += name
            
        return path
    
    def _onDiscoveryResponse(self, response):
        if not response:
            logging.warning("Invalid DISCOVERY response")
            return
        logging.info(f"DISCOVERY response: {response.payload}")
        
    def _onDeleteResponse(self, response):
        pass
    
    def _onGetResponse(self, response, resourcePath: str = None):
        if not response: 
            logging.warning("Invalid GET response")
            return
        
        logging.info("Received GET response")
        
        locationPath = resourcePath.split('/')
		
        if len(locationPath) > 2:
            dataType = locationPath[2]

            if dataType == ConfigConst.ACTUATOR_CMD:
                logging.info(f"ActuatorData received: {response.payload}")

                try:
                    ad = DataUtil().jsonToActuatorData(response.payload)
                    if self.dataMsgListener:
                        self.dataMsgListener.handleActuatorCommandMessage(ad)
                        
                except:
                    logging.warning(f"Failed to decode actuator data. Ignoring {response.payload}")
                    return
            else:
                logging.info(f"Response data received. Payload {response.payload}")

        else:
            logging.info(f"Response data received. Payload {response.payload}")
        
    
    def _onPostResponse(self, response):
        pass
    
    def _onPutResponse(self, response):
        if not response: 
            logging.warning("Invalid PUT response")
            return
        
        logging.info(f"Received PUT response: {response.payload}")