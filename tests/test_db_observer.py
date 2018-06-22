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

"""IconScoreEngine testcase
"""

import unittest
from unittest.mock import Mock

from iconservice import IconScoreDatabase, \
    DatabaseObserver
from iconservice.database.db import ContextDatabase
from iconservice.utils import sha3_256


class TestDatabaseObserver(unittest.TestCase):

    def setUp(self):
        self.mem_db = {}
        self.key_ = b"key1"
        self.last_value = None
        context_db = Mock(spec=ContextDatabase)
        context_db.attach_mock(Mock(return_value=self.last_value), "get", )
        self._observer = Mock(spec=DatabaseObserver)
        self._icon_score_database = IconScoreDatabase(context_db)
        self._icon_score_database.set_observer(self._observer)

    def test_set(self):
        value = b"value1"
        self._icon_score_database.put(self.key_, value)
        self._observer.on_put.assert_called()
        args, _ = self._observer.on_put.call_args
        self.assertEqual(sha3_256(self.key_), args[1])
        self.assertEqual(None, args[2])
        self.assertEqual(value, args[3])
        self.last_value = value

    def test_replace(self):
        value = b"value2"
        self._icon_score_database.put(self.key_, value)
        self._observer.on_put.assert_called()
        args, _ = self._observer.on_put.call_args
        self.assertEqual(sha3_256(self.key_), args[1])
        self.assertEqual(self.last_value, args[2])
        self.assertEqual(value, args[3])
        self.last_value = value

    def test_delete(self):
        self._icon_score_database.delete(self.key_)
        self._observer.on_delete.assert_called()
        args, _ = self._observer.on_delete.call_args
        self.assertEqual(sha3_256(self.key_), args[1])
        self.assertEqual(self.last_value, args[2])
