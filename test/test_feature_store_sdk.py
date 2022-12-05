# ==================================================================================
#
#       Copyright (c) 2022 Samsung Electronics Co., Ltd. All Rights Reserved.
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#          http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#
# ==================================================================================

from featurestoresdk.feature_store_sdk import FeatureStoreSdk
from mock import patch
import base64
import pytest
import logging
import logging.handlers

class pwd_helper():
    def __init__(self):
        self.data = self
    
    def read_namespaced_secret(self, secret_name, namespace):
        return self
    
    def get(self, pwd):
        return  base64.b64encode(bytes("dummy_password", 'utf-8'))


class db_helper():
    '''
        Mimics as feature-store
    '''
    def __init__(self):
        self.trainingjob_name = None
        

    def connect(self, trainingjob_name):
        self.trainingjob_name = trainingjob_name
        return self
    
    def execute(self, query, timeout = None):
        if ('Enb' in query) and ('DLPRB' in query):
            return {'Enb' : ['enb_4563', 'enb_6547'], 'DLPRB' : [4, 6]}
        elif 'Cell Identity' in query:
            return {'Cell Identity' : [2, 5]}
        else: 
            raise Exception("Invalid Query")
        

class Test_feature_store_sdk():
    @patch('featurestoresdk.feature_store_sdk.config.load_incluster_config')
    @patch('featurestoresdk.feature_store_sdk.client.CoreV1Api', return_value= pwd_helper())
    @patch('featurestoresdk.feature_store_sdk.Cluster', return_value = db_helper())
    @patch('featurestoresdk.singleton_manager.open', return_value=open("test/config/config.json", encoding="utf-8"))
    @patch('featurestoresdk.singleton_manager.logging.handlers.RotatingFileHandler', return_value = logging.handlers.RotatingFileHandler('test_featurestoresdk.log',
                    maxBytes=10485760, backupCount=20, encoding='utf-8'))
    def setup_method(self, mock1, mock2, mock3, mock4, mock5, mock6):
        self.obj = FeatureStoreSdk()
    
    def test_init(self):
        assert self.obj != None, 'Feature Store Sdk Object Creation Failed'
    
    def test_get_features(self):
        features = ['Enb' ,'Cell Identity', 'DLPRB']
        features.sort()
        out = self.obj.get_features('my_network', features)
        assert out is not  None, 'Get Features fails the return the features'
    
    def test_negative_get_features(self):
        with pytest.raises(Exception) as exc:
            self.obj.get_features('my_network', ['Invalid Column'])
        assert "error while getting data from feature store" in str(exc.value)