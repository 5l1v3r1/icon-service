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

import hashlib
import random
import unittest

from iconservice.base.address import Address, AddressPrefix, ICON_EOA_ADDRESS_PREFIX, ICON_CONTRACT_ADDRESS_PREFIX, \
    SYSTEM_SCORE_ADDRESS, GOVERNANCE_SCORE_ADDRESS, is_icon_address_valid, split_icon_address, MalformedAddress
from iconservice.base.exception import ExceptionCode
from tests import create_address


class TestAddress(unittest.TestCase):
    def test_get_prefix_EOA(self):
        addr = create_address()
        self.assertEqual(str(addr.prefix), ICON_EOA_ADDRESS_PREFIX)
        self.assertTrue(addr.prefix == AddressPrefix.EOA)

    def test_get_prefix_CONTRACT(self):
        addr = create_address(1)
        self.assertEqual(str(addr.prefix), ICON_CONTRACT_ADDRESS_PREFIX)
        self.assertTrue(addr.prefix == AddressPrefix.CONTRACT)

    def test_eq_EOA(self):
        addr1 = create_address(data=b'addr')
        addr2 = create_address(data=b'addr')
        self.assertTrue(addr1 == addr2)

    def test_eq_CONTRACT(self):
        addr1 = create_address(prefix=1, data=b'addr')
        addr2 = create_address(prefix=1, data=b'addr')
        self.assertTrue(addr1 == addr2)

    def test_ne_EOA(self):
        addr1 = create_address(data=b'addr1')
        addr2 = create_address(data=b'addr2')
        self.assertTrue(addr1 != addr2)

    def test_ne_CONTRACT(self):
        addr1 = create_address(prefix=1, data=b'addr1')
        addr2 = create_address(prefix=1, data=b'addr2')
        self.assertTrue(addr1 != addr2)

    def test_hash_EOA(self):
        addr1 = create_address(data=b'addr')
        addr2 = create_address(data=b'addr')
        self.assertEqual(addr1, addr2)
        self.assertEqual(hash(addr1), hash(addr2))
        self.assertTrue(addr1 is not addr2)

        table = {addr1: 100}
        self.assertEqual(table[addr1], table[addr2])

    def test_hash_CONTRACT(self):
        addr1 = create_address(prefix=1, data=b'addr')
        addr2 = create_address(prefix=1, data=b'addr')
        self.assertEqual(addr1, addr2)
        self.assertEqual(hash(addr1), hash(addr2))
        self.assertTrue(addr1 is not addr2)

        table = {addr1: 100}
        self.assertEqual(table[addr1], table[addr2])

    def test_address_from_to_bytes_EOA(self):
        addr1 = create_address()
        buf = addr1.to_bytes()
        addr2 = Address.from_bytes(buf)
        self.assertEqual(addr1, addr2)

    def test_address_from_to_bytes_CONTRACT(self):
        addr1 = create_address(prefix=1)
        buf = addr1.to_bytes()
        addr2 = Address.from_bytes(buf)
        self.assertEqual(addr1, addr2)

    def test_address_from_to_bytes_OTHER(self):
        addr1 = create_address()
        buf = addr1.to_bytes()
        prefix: int = 0
        prefix_buf: bytes = prefix.to_bytes(1, 'big')
        buf = prefix_buf + buf
        addr2 = Address.from_bytes(buf)
        self.assertEqual(addr1, addr2)

    def test_address_from_to_string_EOA(self):
        addr1 = create_address()
        buf = str(addr1)
        addr2 = Address.from_string(buf)
        self.assertEqual(addr1, addr2)

    def test_address_from_to_string_EOA2(self):
        addr1 = create_address()
        buf = bytes.hex(addr1.body)
        with self.assertRaises(BaseException) as e:
            Address.from_string(buf)
        self.assertEqual(e.exception.code, ExceptionCode.INVALID_PARAMETER)
        self.assertEqual(e.exception.message, 'Invalid address')

    def test_address_from_to_string_CONTRACT(self):
        addr1 = create_address(prefix=1)
        buf = str(addr1)
        addr2 = Address.from_string(buf)
        self.assertEqual(addr1, addr2)

    def test_is_icon_address_valid(self):
        address: str = str(create_address())
        self.assertTrue(is_icon_address_valid(address))

        # Remove prefix 'hx'
        a = address[2:]
        self.assertFalse(is_icon_address_valid(a))

        # short address
        a = address[:-1]
        self.assertFalse(is_icon_address_valid(a))

        # wrong param prefix
        self.assertFalse(is_icon_address_valid(1234))

        # wrong hexadecimal format
        self.assertFalse(is_icon_address_valid(
            "0x00c3f694d84074f9145cd0bfa497290ce2d8052f"))

    def test_split_icon_address(self):
        address = create_address()
        prefix, body = split_icon_address(str(address))
        self.assertEqual(prefix, str(address.prefix))
        self.assertEqual(body, bytes.hex(address.body))

    def test_prefix_and_int(self):
        self.assertEqual(Address.from_prefix_and_int(AddressPrefix.CONTRACT, 0), SYSTEM_SCORE_ADDRESS)
        self.assertEqual(Address.from_prefix_and_int(AddressPrefix.CONTRACT, 1), GOVERNANCE_SCORE_ADDRESS)
        self.assertEqual(str(Address.from_prefix_and_int(AddressPrefix.EOA, 10)),
                         "hx000000000000000000000000000000000000000a")
        self.assertEqual(str(Address.from_prefix_and_int(AddressPrefix.CONTRACT, 1024)),
                         "cx0000000000000000000000000000000000000400")

    def test_malformed_address(self):
        address: str = "hx123456"
        addr = MalformedAddress.from_string(address)
        self.assertEqual(str(addr), address)

    def test_invalid_address(self):
        address: str = "hx123456"
        with self.assertRaises(BaseException) as e:
            Address.from_string(address)
        self.assertEqual(e.exception.code, ExceptionCode.INVALID_PARAMETER)
        self.assertEqual(e.exception.message, "Invalid address")

    def test_from_bytes_including_prefix(self):
        address_prefixes = [AddressPrefix.EOA, AddressPrefix.CONTRACT]

        value: int = random.randint(0, 0xffffffff)
        input_data: bytes = value.to_bytes(4, 'big')
        data: bytes = hashlib.sha3_256(input_data).digest()

        for prefix in address_prefixes:
            body: bytes = data[-20:]
            self.assertEqual(20, len(body))

            address_bytes: bytes = prefix.to_bytes(1, 'big') + body
            address = Address.from_bytes_including_prefix(address_bytes)

            self.assertEqual(prefix, address.prefix)
            self.assertEqual(body, address.body)

        for prefix in address_prefixes:
            size = random.randint(1, 32)
            if size == 20:
                size += 1

            body: bytes = data[-size:]
            self.assertEqual(size, len(body))

            address_bytes: bytes = prefix.to_bytes(1, 'big') + body
            address = Address.from_bytes_including_prefix(address_bytes)
            self.assertIsNone(address)

            address = Address.from_bytes_including_prefix(body)
            self.assertIsNone(address)

    def test_to_bytes_including_prefix(self):
        value: int = random.randint(0, 0xffffffff)
        input_data: bytes = value.to_bytes(4, 'big')
        data: bytes = hashlib.sha3_256(input_data).digest()
        body: bytes = data[-20:]

        for prefix in [AddressPrefix.EOA, AddressPrefix.CONTRACT]:
            address = Address(prefix, body)
            address_bytes: bytes = address.to_bytes_including_prefix()

            expected_bytes: bytes = prefix.to_bytes(1, 'big') + body
            self.assertIsInstance(address_bytes, bytes)
            self.assertEqual(21, len(address_bytes))
            self.assertEqual(expected_bytes, address_bytes)


if __name__ == '__main__':
    unittest.main()
