#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright 2018 ICON Foundation
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


from unittest.mock import Mock

import pytest

from iconservice import Address
from iconservice.base.exception import InvalidParamsException, OutOfBalanceException
from iconservice.icon_constant import Revision
from iconservice.iconscore.icon_score_context import IconScoreContext
from iconservice.icx.coin_part import CoinPart
from iconservice.icx.delegation_part import DelegationPart
from iconservice.icx.icx_account import Account
from iconservice.icx.stake_part import StakePart
from tests import create_address


class TestAccount:
    def test_account_flag(self):
        address: 'Address' = create_address()

        account: 'Account' = Account(address, 0, Revision.IISS.value)
        assert account.coin_part is None
        assert account.stake_part is None
        assert account.delegation_part is None

        coin_part: 'CoinPart' = CoinPart()
        account: 'Account' = Account(address, 0, Revision.IISS.value, coin_part=coin_part)
        assert account.coin_part is not None
        assert account.stake_part is None
        assert account.delegation_part is None

        stake_part: 'StakePart' = StakePart()
        account: 'Account' = Account(address, 0, Revision.IISS.value, stake_part=stake_part)
        assert account.coin_part is None
        assert account.stake_part is not None
        assert account.delegation_part is None

        delegation_part: 'DelegationPart' = DelegationPart()
        account: 'Account' = Account(address, 0, Revision.IISS.value, delegation_part=delegation_part)
        assert account.coin_part is None
        assert account.stake_part is None
        assert account.delegation_part is not None

        account: 'Account' = Account(address, 0, Revision.IISS.value,
                                     coin_part=coin_part,
                                     stake_part=stake_part,
                                     delegation_part=delegation_part)
        assert account.coin_part is not None
        assert account.stake_part is not None
        assert account.delegation_part is not None

    def test_coin_part(self):
        address: 'Address' = create_address()

        coin_part: 'CoinPart' = CoinPart()
        account: 'Account' = Account(address, 0, Revision.IISS.value, coin_part=coin_part)
        assert account.address == address
        assert account.balance == 0

        account.deposit(100)
        assert account.balance == 100

        account.withdraw(100)
        assert account.balance == 0

        # wrong value
        with pytest.raises(InvalidParamsException):
            account.deposit(-10)

        # 0 transfer is possible
        old = account.balance
        account.deposit(0)
        assert account.balance == old

        with pytest.raises(InvalidParamsException):
            account.withdraw(-11234)

        with pytest.raises(OutOfBalanceException):
            account.withdraw(1)

        old = account.balance
        account.withdraw(0)
        assert account.balance == old

    def test_account_for_stake(self):
        address: 'Address' = create_address()
        context: 'IconScoreContext' = IconScoreContext()

        coin_part: 'CoinPart' = CoinPart()
        stake_part: 'StakePart' = StakePart()
        account = Account(address, 0, Revision.IISS.value, coin_part=coin_part, stake_part=stake_part)

        balance = 1000
        account.deposit(balance)

        stake1 = 500
        unstake_block_height = 0
        remain_balance = balance - stake1

        account.set_stake(context, stake1, 0)

        assert account.stake == stake1
        assert account.unstake == 0
        assert account.unstake_block_height == unstake_block_height
        assert account.balance == remain_balance

        stake2 = 100
        block_height = 10
        unstake = stake1 - stake2
        remain_balance = balance - stake1
        account.set_stake(context, stake2, block_height)

        assert account.stake == stake2
        assert account.unstake == unstake
        assert account.unstake_block_height == block_height
        assert account.balance == remain_balance

        remain_balance = remain_balance + unstake
        account._current_block_height += 11
        account.normalize(Revision.IISS.value)
        assert account.balance == remain_balance

    def test_account_for_stake_rev_multiple_unstake1(self):
        address: 'Address' = create_address()
        context: 'IconScoreContext' = Mock(spec=IconScoreContext)
        unstake_slot_max = 10
        current_block_height = 7
        unstake_lock_period = 100

        context.configure_mock(unstake_slot_max=unstake_slot_max)
        context.configure_mock(revision=Revision.MULTIPLE_UNSTAKE.value)

        coin_part: 'CoinPart' = CoinPart()
        stake_part: 'StakePart' = StakePart()
        account = Account(
            address, current_block_height,
            Revision.MULTIPLE_UNSTAKE.value,
            coin_part=coin_part, stake_part=stake_part
        )

        balance = 1000
        account.deposit(balance)
        assert account.balance == balance

        # stake: 0 -> 500
        # unstake: 0 -> 0
        # balance: 1000 -> 500
        stake1 = 500
        remain_balance = balance - stake1

        account.set_stake(context, stake1, unstake_lock_period)
        assert account.stake == stake1
        assert account.unstake == 0
        assert account.unstake_block_height == 0
        assert account.balance == remain_balance
        assert account.balance + account.total_stake == balance

        # stake: 500 -> 100
        # unstake: 0 -> 400
        # balance: 500 -> 500
        stake2 = 100
        unstake = stake1 - stake2
        remain_balance = balance - stake1
        expected_unstake_info = [[unstake, current_block_height + unstake_lock_period]]
        account.set_stake(context, stake2, unstake_lock_period)
        assert account.stake == stake2
        assert account.unstake == 0
        assert account.unstake_block_height == 0
        assert account.unstakes_info == expected_unstake_info
        assert account.balance == remain_balance
        assert account.balance + account.total_stake == balance

        # stake: 100 -> 300
        # unstake: 400 -> 200
        # balance: 500 -> 500
        stake = 300
        account.set_stake(context, stake, unstake_lock_period)
        expected_unstake_info = [[200, current_block_height + unstake_lock_period]]
        assert account.stake == stake
        assert account.unstakes_info == expected_unstake_info
        assert account.balance == 500
        assert account.balance + account.total_stake == balance

        # stake: 300 -> 1000
        # unstake: 200 -> 0
        # balance: 500 -> 0
        stake = 1000
        account.set_stake(context, stake, unstake_lock_period)
        assert account.stake == stake
        assert account.balance == 0
        assert account.unstakes_info == []
        assert account.balance + account.total_stake == balance

    def test_account_for_unstake_slot_max_case_1(self):
        address: 'Address' = create_address()
        context: 'IconScoreContext' = Mock(spec=IconScoreContext)
        unstake_slot_max = 10
        context.configure_mock(unstake_slot_max=unstake_slot_max)
        context.configure_mock(revision=Revision.MULTIPLE_UNSTAKE.value)

        coin_part: 'CoinPart' = CoinPart()
        stake_part: 'StakePart' = StakePart()
        account = Account(address, 0, Revision.MULTIPLE_UNSTAKE.value, coin_part=coin_part, stake_part=stake_part)

        balance = 2000
        account.deposit(balance)

        stake = 2000
        unstake_block_height = 0
        remain_balance = balance - stake

        account.set_stake(context, stake, 0)

        assert account.stake == stake
        assert account.unstake == 0
        assert account.unstake_block_height == unstake_block_height
        assert account.balance == remain_balance

        unstake = 1
        total_unstake = 0
        expected_unstake_info = []
        for i in range(unstake_slot_max):
            expected_unstake_info.append([unstake, unstake_slot_max + i])
            stake -= unstake
            total_unstake += unstake
            account.set_stake(context, account.stake - unstake, unstake_slot_max + i)
            assert account.stake == stake
            assert account.stake_part.total_unstake == total_unstake
            assert account.balance == remain_balance
            assert account.unstakes_info == expected_unstake_info
        last_unstake = 100
        account.set_stake(context, account.stake - last_unstake, unstake_slot_max + 2)
        expected_unstake_info[-1] = [101, unstake_slot_max*2 - 1]
        assert account.unstakes_info == expected_unstake_info

    def test_account_for_delegation(self):
        target_accounts = []

        src_delegation_part: 'DelegationPart' = DelegationPart()
        src_account = Account(create_address(), 0, Revision.IISS.value, delegation_part=src_delegation_part)
        preps: list = []

        for _ in range(0, 10):
            address: 'Address' = create_address()
            target_delegation_part: 'DelegationPart' = DelegationPart()
            target_account: 'Account' = \
                Account(address, 0, Revision.IISS.value, delegation_part=target_delegation_part)

            target_accounts.append(target_account)
            target_account.update_delegated_amount(10)
            preps.append((address, 10))

        src_account.set_delegations(preps)
        assert len(src_account.delegation_part.delegations) == 10

        for i in range(10):
            assert target_accounts[i].delegation_part.delegated_amount == 10

    def test_account_balance(self):
        value: int = 0
        coin_part = Mock(spec=CoinPart, balance=value)
        account = Account(create_address(), 0, Revision.IISS.value, coin_part=coin_part)
        assert account.balance == value

        value: int = 100
        coin_part = Mock(spec=CoinPart, balance=value)
        account = Account(create_address(), 0, Revision.IISS.value, coin_part=coin_part)
        assert account.balance == value

    def test_account_stake(self):
        value: int = 0
        stake_part = StakePart(stake=value)
        stake_part.set_complete(True)
        account = Account(create_address(), 0, Revision.IISS.value, stake_part=stake_part)
        assert account.stake == value

        value: int = 100
        stake_part = StakePart(stake=value)
        stake_part.set_complete(True)
        account = Account(create_address(), 0, Revision.IISS.value, stake_part=stake_part)
        assert account.stake == value

    def test_account_unstake(self):
        value: int = 0
        stake_part = StakePart(unstake=value)
        stake_part.set_complete(True)
        account = Account(create_address(), 0, Revision.IISS.value, stake_part=stake_part)
        assert account.unstake == 0

        value: int = 200
        stake_part = StakePart(unstake=value)
        stake_part.set_complete(True)
        account = Account(create_address(), 0, Revision.IISS.value, stake_part=stake_part)
        assert account.unstake == value

    def test_account_unstake_block_height(self):
        value: int = 0
        stake_part = StakePart(unstake_block_height=value)
        stake_part.set_complete(True)
        account = Account(create_address(), 0, Revision.IISS.value, stake_part=stake_part)
        assert account.unstake_block_height == 0

        value: int = 300
        stake_part = StakePart(unstake_block_height=value)
        stake_part.set_complete(True)
        account = Account(create_address(), 0, Revision.IISS.value, stake_part=stake_part)
        assert account.unstake_block_height == value

    def test_account_unstakes_info(self):
        value: int = 0
        stake_part = StakePart(unstake=value)
        stake_part.set_complete(True)
        account = Account(create_address(), 0, Revision.MULTIPLE_UNSTAKE.value, stake_part=stake_part)
        assert account.unstakes_info == []

        info = [(10, 1), (20, 5)]
        stake_part = StakePart(unstakes_info=info)
        stake_part.set_complete(True)
        account = Account(create_address(), 0, Revision.MULTIPLE_UNSTAKE.value, stake_part=stake_part)
        assert account.unstakes_info == info

    def test_account_delegated_amount(self):
        value: int = 0
        delegation_part = DelegationPart(delegated_amount=value)
        account = Account(create_address(), 0, Revision.IISS.value, delegation_part=delegation_part)
        assert account.delegated_amount == value

        value: int = 100
        delegation_part = DelegationPart(delegated_amount=value)
        account = Account(create_address(), 0, Revision.IISS.value, delegation_part=delegation_part)
        assert account.delegated_amount == value

    def test_account_delegations(self):
        value: list = []
        delegation_part = DelegationPart(delegations=value)
        account = Account(create_address(), 0, Revision.IISS.value, delegation_part=delegation_part)
        assert account.delegations == value

        delegations = [
            (create_address(), 100),
            (create_address(), 200),
            (create_address(), 300)
        ]
        delegation_part = DelegationPart(delegations=delegations)
        account = Account(create_address(), 0, Revision.IISS.value, delegation_part=delegation_part)
        assert account.delegations == delegations
        assert account.delegations_amount == 600
