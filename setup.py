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

from setuptools import setup
setup(
    name='featurestoresdk',
    version='0.3.2',
    description='feature store SDK for Training Host',
    url='https://gerrit.o-ran-sc.org/r/admin/repos/aiml-fw/athp/sdk/feature-store,general',
    author='O-RAN Software Community',
    author_email='discuss@lists.o-ran-sc.org',
    license='Apache 2.0',
    packages=['featurestoresdk'],
    package_data={"featurestoresdk": ['config/config.json']},
    install_requires=[
        "pandas==1.4.4",
        "cassandra-driver==3.25.0",
        "kubernetes",
    ],
    zip_safe=False,
)
