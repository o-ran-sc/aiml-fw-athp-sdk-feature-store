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

"""
This module is used to get sdk configuration and logger.
"""
import logging
import logging.handlers
import json
import sys
from featurestoresdk.sdk_exception import SdkException

class SingletonManager:
    """
    This class is used to get sdk configuration and logger.
    Simplified Singleton implementation.
    Thread safety not considered, only reading from the instance after creation.
    """

    __instance = None

    @staticmethod
    def get_instance():
        """
        This function creates SingletonManager instance if not present and return it.
        """
        if not SingletonManager.__instance:
            SingletonManager()
        return SingletonManager.__instance

    def __init__(self):

        if not SingletonManager.__instance:
            
            prefix_sdk = ''            
            self.__logger = logging.getLogger('featurestoresdk')
            self.__logger.setLevel(logging.DEBUG)

            log_format = logging.Formatter('%(asctime)s | %(filename)s %(lineno)s %(funcName)s()'+\
                                           ' |  %(levelname)s | %(message)s')

            rotating_file_handler = logging.handlers.RotatingFileHandler('/var/log/featurestoresdk.log',
                    maxBytes=10485760, backupCount=20, encoding='utf-8')
            rotating_file_handler.setFormatter(log_format)
            rotating_file_handler.setLevel(logging.DEBUG)
            self.__logger.addHandler(rotating_file_handler)


            stream_handler = logging.StreamHandler(sys.stdout)
            stream_handler.setFormatter(log_format)
            stream_handler.setLevel(logging.DEBUG)
            self.__logger.addHandler(stream_handler)

            self.__logger.propagate = False

            with open(prefix_sdk + '/SDK/featurestoresdk_main/config/config.json', encoding="utf-8") as config:
                self.__config = json.load(config)

            SingletonManager.__instance = self
        else:
            raise SdkException("This class is a singleton!")

    @property
    def logger(self):
        """
        This function returns logger.
        """
        return self.__logger

    @property
    def config(self):
        """
        This functions returns sdk configuration in dictionary.
        """
        return self.__config
