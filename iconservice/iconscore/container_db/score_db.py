from typing import Optional, TYPE_CHECKING

from ...database.score_db.utils import KeyElement, DICT_DB_ID

if TYPE_CHECKING:
    from ...base.address import Address
    from ...database.db import ScoreSubDatabase


class IconScoreDatabase:
    def __init__(self, db: 'ScoreSubDatabase'):
        self._db: 'ScoreSubDatabase' = db

    @property
    def address(self) -> 'Address':
        return self._db.address

    def get(self, key: bytes) -> Optional[bytes]:

        """
        Gets the value for the specified key

        :param key: key to retrieve
        :return: value for the specified key, or None if not found
        """

        key: 'KeyElement' = self._make_key_element(key=key)
        return self._db.get(key=key)

    def put(self, key: bytes, value: bytes):
        """
        Sets a value for the specified key.

        :param key: key to set
        :param value: value to set
        """
        key: 'KeyElement' = self._make_key_element(key=key)
        self._db.put(key=key, value=value)

    def delete(self, key: bytes):
        """
        Deletes the key/value pair for the specified key.

        :param key: key to delete
        """
        key: 'KeyElement' = self._make_key_element(key=key)
        self._db.delete(key)

    def get_sub_db(self, prefix: bytes) -> 'IconScoreDatabase':
        key: 'KeyElement' = self._make_key_element(key=prefix)
        db: 'ScoreSubDatabase' = self._db.get_sub_db(key=key)
        return IconScoreDatabase(db=db)

    @classmethod
    def _make_key_element(cls, key: bytes) -> 'KeyElement':
        return KeyElement(keys=[key], container_id=DICT_DB_ID)
