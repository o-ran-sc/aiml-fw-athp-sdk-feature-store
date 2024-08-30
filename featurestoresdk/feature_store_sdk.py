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

from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider
from featurestoresdk.sdk_exception import SdkException
from featurestoresdk.singleton_manager import SingletonManager
import pandas as pd
import traceback
from kubernetes import client, config
import base64


class FeatureStoreSdk:
    def __init__(self):
        sm_object = SingletonManager.get_instance()
        self.logger = sm_object.logger
        self.config = sm_object.config["feature_store_config"]

        self.feature_store_ip = self.config["feature_store_ip"]
        self.feature_store_port = self.config["feature_store_port"]
        self.feature_store_username = self.config["feature_store_username"]
        self.feature_store_password = self.get_feature_store_pwd()
        self.feature_store_db_name = self.config["feature_store_db_name"]
        self.clust = Cluster(
            [self.feature_store_ip],
            port=self.feature_store_port,
            auth_provider=PlainTextAuthProvider(
                username=self.feature_store_username,
                password=self.feature_store_password,
            ),
        )
        self.session = self.clust.connect(self.feature_store_db_name)

    def get_feature_store_pwd(self):
        """
            This function would retrieve feature-store-password from kubernetes secrets
        """
        config.load_incluster_config()
        v1 = client.CoreV1Api()
        sec = v1.read_namespaced_secret("cassandra", 'traininghost').data
        fs_pwd = base64.b64decode(sec.get("cassandra-password")).decode('utf-8')
        return fs_pwd

    def get_features(self, trainingjob_name, features):
        """
        This function returns pandas dataframe containing data.
                    Special handle for features containing empty spaces and special character
                    The db driver replaces empty spaces with _ and removes special characters in
                    the result dataset, So we query those spaced features in different db query and
                    maintain the original feature name
        args:
            trainingjob_name: collection name from where we take data in feature store
            features: list of strings indicating features
        return value:
            panda dataframe containing data
        """
        try:
            merged_df = pd.DataFrame()
            nospaced_feat = []
            spaced_feat = []
            nospaced_feat.append('"__Id"')
            if len(features) > 0:
                for feature in features:
                    # FS maintains case sensitivity of feature, hence wrapping search inside ""
                    feature = '"' + feature + '"'
                    if feature.find(" ") > 0:
                        self.logger.debug(feature + " has empty space")
                        spaced_feat.append(feature)
                    else:
                        self.logger.debug(feature + " does not have empty space")
                        nospaced_feat.append(feature)

            # Fetch all non spaced features in one query
            nospace_q = self.build_fetch_query(trainingjob_name, nospaced_feat)
            response_nonspace = self.session.execute(nospace_q, timeout=None)
            merged_df = pd.DataFrame(response_nonspace)

            self.logger.debug("Non spaced pd" + str(merged_df.head()))
            # Fetch all spaced feature data one by one and merge with non spaced dataframe
            if len(spaced_feat) > 0:
                for feature in spaced_feat:
                    space_q = self.build_fetch_query_single(trainingjob_name, feature)
                    response_nonspace = self.session.execute(space_q, timeout=None)
                    space_pd = pd.DataFrame(response_nonspace)
                    feature = feature.replace('"', "")
                    space_pd.columns = [
                        feature
                    ]  # Rename the column as supplied in function parameter
                    # Check null or pd size
                    merged_df = pd.merge(merged_df, space_pd, left_index=True, right_index=True)

            if "Id" in merged_df.columns:
                merged_df = merged_df.sort_values(by="Id")
                merged_df = merged_df.set_index("Id", drop=True)
                merged_df.index.name = None

            # Test if pipeline can access this result
            self.logger.debug(
                "Select pipeline merged_df --> \n" + str(merged_df.head())
            )
            return merged_df

        except Exception as exc:
            self.logger.error(traceback.format_exc())
            raise SdkException("error while getting data from feature store") from None

    def build_fetch_query(self, trainingjob_name, features):
        """
        Builds simple sql query for given table and features list
        """
        col = ""
        for feature in features:
            col = col + feature + ", "

        col = col[:-2]
        query = "select " + col + " from " + trainingjob_name + " ;"
        self.logger.debug("Check Select query--> " + query)
        return query

    def build_fetch_query_single(self, trainingjob_name, feature):
        """
        Builds simple sql query for given table and single feature
        """
        return "select " + feature + " from " + trainingjob_name + " ;"
