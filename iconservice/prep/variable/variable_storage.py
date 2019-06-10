# Copyright 2019 ICON Foundation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from typing import TYPE_CHECKING, Optional, List

from ...base.type_converter_templates import ConstantKeys
from ...utils.msgpack_for_db import MsgPackForDB

if TYPE_CHECKING:
    from ...database.db import ContextDatabase
    from ...iconscore.icon_score_context import IconScoreContext
    from ...base.address import Address


class VariableStorage(object):
    PREFIX: bytes = b'prep'
    GOVERNANCE_VARIABLE_KEY: bytes = PREFIX + b'gv'
    PREPS_KEY: bytes = PREFIX + b'preps'
    PREP_PERIOD_KEY: bytes = PREFIX + b'period'
    PREP_NEXT_BLOCK_HEIGHT_KEY: bytes = PREFIX + b'pnbh'

    def __init__(self, db: 'ContextDatabase'):
        """Constructor

        :param db: (Database) state db wrapper
        """
        self._db: 'ContextDatabase' = db

    def close(self):
        """Close the embedded database.
        """
        if self._db:
            self._db = None

    def put_gv(self, context: 'IconScoreContext', gv: 'GovernanceVariable'):
        self._db.put(context, self.GOVERNANCE_VARIABLE_KEY, gv.to_bytes())

    def get_gv(self, context: 'IconScoreContext') -> Optional['GovernanceVariable']:
        value: bytes = self._db.get(context, self.GOVERNANCE_VARIABLE_KEY)
        if value:
            return GovernanceVariable.from_bytes(value)
        return None

    def put_preps(self, context: 'IconScoreContext', preps: 'PReps'):
        self._db.put(context, self.PREPS_KEY, preps.to_bytes())

    def get_preps(self, context: 'IconScoreContext') -> Optional['PReps']:
        value: bytes = self._db.get(context, self.PREPS_KEY)
        if value:
            return PReps.from_bytes(value)
        return None

    def put_prep_period(self, context: 'IconScoreContext', prep_period: int):
        self._db.put(context, self.PREP_PERIOD_KEY, PrepPeriod(prep_period).to_bytes())

    def get_prep_period(self, context: 'IconScoreContext') -> int:
        value: bytes = self._db.get(context, self.PREP_PERIOD_KEY)
        if value:
            return PrepPeriod.from_bytes(value)
        return 0

    def put_prep_next_block_height(self, context: 'IconScoreContext', prep_block_height: int):
        self._db.put(context, self.PREP_NEXT_BLOCK_HEIGHT_KEY, PrepPeriod(prep_block_height).to_bytes())

    def get_prep_next_block_height(self, context: 'IconScoreContext') -> int:
        value: bytes = self._db.get(context, self.PREP_NEXT_BLOCK_HEIGHT_KEY)
        if value:
            return PrepPeriod.from_bytes(value)
        return 0


class GovernanceVariable(object):
    _VERSION = 0

    def __init__(self):
        self.incentive_rep: int = 0

    @staticmethod
    def from_bytes(buf: bytes) -> 'GovernanceVariable':
        data: list = MsgPackForDB.loads(buf)
        version = data[0]

        obj = GovernanceVariable()
        obj.incentive_rep: int = data[1]
        return obj

    @staticmethod
    def from_config_data(data: dict) -> 'GovernanceVariable':
        obj = GovernanceVariable()
        obj.incentive_rep: int = data[ConstantKeys.INCENTIVE_REP]
        return obj

    def to_bytes(self) -> bytes:
        """Convert GovernanceVariable object to bytes

        :return: data including information of GovernanceVariable object
        """

        data = [
            self._VERSION,
            self.incentive_rep
        ]
        return MsgPackForDB.dumps(data)


class PReps(object):
    _VERSION = 0

    def __init__(self):
        self.preps: List['PRep'] = []

    @staticmethod
    def from_bytes(buf: bytes) -> 'PReps':
        data: list = MsgPackForDB.loads(buf)
        version = data[0]

        obj = PReps()
        for prep in data[1:]:
            obj.preps.append(PRep.from_list(prep))
        return obj

    @staticmethod
    def from_list(preps: list) -> 'PReps':
        obj = PReps()

        for p in preps:
            prep: 'PRep' = PRep(p.address, p.total_delegated)
            obj.preps.append(prep)
        return obj

    def to_bytes(self) -> bytes:
        data = [
            self._VERSION
        ]
        for prep in self.preps:
            data.append(prep.to_list())
        return MsgPackForDB.dumps(data)


class PRep(object):
    _VERSION = 0

    def __init__(self, address: 'Address', total_delegated: int):
        self.address: 'Address' = address
        self.total_delegated: int = total_delegated

    @staticmethod
    def from_list(data: list) -> 'PRep':
        version = data[0]

        obj = PRep(data[1], data[2])
        return obj

    def to_list(self) -> list:
        data = [
            self._VERSION,
            self.address,
            self.total_delegated
        ]
        return data


class PrepPeriod(object):
    _VERSION = 0

    def __init__(self, prep_period: int):
        self.prep_period = prep_period

    @staticmethod
    def from_bytes(buf: bytes) -> int:
        data: list = MsgPackForDB.loads(buf)
        version: int = data[0]
        prep_period: int = data[1]
        return prep_period

    def to_bytes(self) -> bytes:
        data: list = [
            self._VERSION,
            self.prep_period
        ]
        return MsgPackForDB.dumps(data)
