# -*- coding: utf-8 -*-

# Copyright 2017-2018 theloop Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


class Block(object):
    """Block Information included in IconScoreContext
    """
    def __init__(self, height: int, hash: str, timestamp: int) -> None:
        """Constructor

        :param height: block height
        :param hash: block hash
        """
        self.height = height
        self.hash = hash
        # unit: microsecond
        self.timestamp = timestamp