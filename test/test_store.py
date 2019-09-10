from unittest import mock
from unittest.mock import patch, Mock
import unittest
import sys

sys.path.append('../')
import store
import redis
from store import RedisStore


class TestStoreWithRedisServer(unittest.TestCase):

    def test_set_get(self):
        ping = False
        try:
            ping = redis.StrictRedis(host='localhost', port=6379).ping()
        except redis.exceptions.ConnectionError:
            pass
        if ping:
            self.assertTrue(store.Store().set('test_key', 'test_val'))
            self.assertEqual(store.Store().get('test_key'), b'test_val')


class TestStoreMock(unittest.TestCase):

    @mock.patch('store.RedisStore')
    def test_set(self, MockRedisStore):
        red = MockRedisStore()
        red.set.return_value = True
        response = store.Store().set('test_key_2', 'test_val_2')
        self.assertIsNotNone(response)
        self.assertTrue(response)

    @mock.patch('store.RedisStore')
    def test_get(self, MockRedisStore):
        red = MockRedisStore()
        red.get.return_value = 'some_val'

        response = store.Store().get('test_key_2')

        self.assertIsNotNone(response)

    @mock.patch('store.RedisStore')
    def test_set(self, MockRedisStore):
        red = MockRedisStore()
        red.set.side_effect = ConnectionError
        store.Store().set('test_key_3', 'test_val_3')
        self.assertTrue(red.set.call_count > 0)

    @mock.patch('store.RedisStore')
    def test_get(self, MockRedisStore):
        red = MockRedisStore()
        red.get.side_effect = ConnectionError
        store.Store().get('test_key_3')
        self.assertTrue(red.get.call_count > 0)


if __name__ == '__main__':
    unittest.main()