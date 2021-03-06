# -*- coding: utf-8 -*-
# Copyright 2019 ICON Foundation
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

import hashlib
import unittest

from iconservice.base.address import AddressPrefix
from iconservice.iiss.reward_calc.ipc.message import *
from iconservice.iiss.reward_calc.ipc.message_unpacker import MessageUnpacker
from iconservice.utils import int_to_bytes


class TestMessageUnpacker(unittest.TestCase):
    def setUp(self):
        self.unpacker = MessageUnpacker()

    def test_iterator(self):
        version: int = 7
        msg_id: int = 1234
        block_height: int = 100
        state_hash: bytes = hashlib.sha3_256(b'').digest()
        block_hash: bytes = hashlib.sha3_256(b'block_hash').digest()
        tx_index: int = 1
        tx_hash: bytes = hashlib.sha3_256(b"tx_hash").digest()
        address = Address.from_data(AddressPrefix.EOA, b'')
        iscore: int = 5000
        success: bool = True

        status: int = 1

        messages = [
            (
                MessageType.VERSION,
                msg_id,
                (
                    version,
                    block_height
                )
            ),
            (
                MessageType.CALCULATE,
                msg_id,
                (
                    status,
                    block_height
                )
            ),
            (
                MessageType.QUERY,
                msg_id,
                (
                    address.to_bytes_including_prefix(),
                    int_to_bytes(iscore),
                    block_height
                )
            ),
            (
                MessageType.CLAIM,
                msg_id,
                (
                    address.to_bytes_including_prefix(),
                    block_height,
                    block_hash,
                    tx_index,
                    tx_hash,
                    int_to_bytes(iscore)
                )
            ),
            (
                MessageType.COMMIT_BLOCK,
                msg_id,
                (
                    success,
                    block_height,
                    block_hash
                )
            ),
            (
                MessageType.COMMIT_CLAIM,
                msg_id
            ),
            (
                MessageType.QUERY_CALCULATE_STATUS,
                msg_id,
                (
                    status,
                    block_height
                )
            ),
            (
                MessageType.QUERY_CALCULATE_RESULT,
                msg_id,
                (
                    status,
                    block_height,
                    int_to_bytes(iscore),
                    state_hash
                )
            ),
            (
                MessageType.READY,
                msg_id,
                (
                    version,
                    block_height,
                    block_hash
                )
            ),
            (
                MessageType.CALCULATE_DONE,
                msg_id,
                (
                    success,
                    block_height,
                    int_to_bytes(iscore),
                    state_hash
                )
            ),
            (
                MessageType.ROLLBACK,
                msg_id,
                (
                    success,
                    block_height,
                    block_hash
                )
            ),
            (
                MessageType.INIT,
                msg_id,
                (
                    success,
                    block_height
                )
            )
    ]

        for message in messages:
            data: bytes = msgpack.packb(message)
            self.unpacker.feed(data)

        it = iter(self.unpacker)
        version_response = next(it)
        self.assertIsInstance(version_response, VersionResponse)
        self.assertEqual(version, version_response.version)

        calculate_response = next(it)
        self.assertIsInstance(calculate_response, CalculateResponse)

        query_response = next(it)
        self.assertIsInstance(query_response, QueryResponse)
        self.assertEqual(iscore, query_response.iscore)
        self.assertEqual(block_height, query_response.block_height)

        claim_response = next(it)
        self.assertIsInstance(claim_response, ClaimResponse)
        self.assertEqual(iscore, claim_response.iscore)
        self.assertEqual(block_height, claim_response.block_height)
        self.assertEqual(tx_index, claim_response.tx_index)
        self.assertEqual(tx_hash, claim_response.tx_hash)

        commit_block_response = next(it)
        self.assertIsInstance(commit_block_response, CommitBlockResponse)
        self.assertEqual(block_height, commit_block_response.block_height)
        self.assertEqual(block_hash, commit_block_response.block_hash)

        commit_claim_response = next(it)
        self.assertIsInstance(commit_claim_response, CommitClaimResponse)

        query_calculate_status = next(it)
        self.assertIsInstance(query_calculate_status, QueryCalculateStatusResponse)
        self.assertEqual(status, query_calculate_status.status)
        self.assertEqual(block_height, query_calculate_status.block_height)

        query_calculate_result = next(it)
        self.assertIsInstance(query_calculate_result, QueryCalculateResultResponse)
        self.assertEqual(status, query_calculate_result.status)
        self.assertEqual(block_height, query_calculate_result.block_height)
        self.assertEqual(state_hash, query_calculate_result.state_hash)

        ready_notification = next(it)
        self.assertIsInstance(ready_notification, ReadyNotification)
        self.assertEqual(version, ready_notification.version)
        self.assertEqual(block_height, ready_notification.block_height)
        self.assertEqual(block_hash, ready_notification.block_hash)

        calculate_done_notification = next(it)
        self.assertIsInstance(calculate_done_notification, CalculateDoneNotification)
        self.assertTrue(calculate_done_notification.success)
        self.assertEqual(block_height, calculate_done_notification.block_height)
        self.assertEqual(state_hash, calculate_done_notification.state_hash)

        rollback_response = next(it)
        self.assertIsInstance(rollback_response, RollbackResponse)
        self.assertTrue(rollback_response.success)
        self.assertEqual(block_height, rollback_response.block_height)
        self.assertEqual(block_hash, rollback_response.block_hash)

        init_response = next(it)
        self.assertIsInstance(init_response, InitResponse)
        self.assertEqual(success, init_response.success)
        self.assertEqual(block_height, init_response.block_height)

        with self.assertRaises(StopIteration):
            next(it)

        for message in messages:
            data: bytes = msgpack.packb(message)
            self.unpacker.feed(data)

        expected = [
            version_response, calculate_response, query_response,
            claim_response, commit_block_response, commit_claim_response,
            query_calculate_status, query_calculate_result,
            ready_notification, calculate_done_notification, rollback_response
        ]
        for expected_response, response in zip(expected, self.unpacker):
            self.assertEqual(expected_response.MSG_TYPE, response.MSG_TYPE)
            self.assertEqual(msg_id, response.msg_id)
