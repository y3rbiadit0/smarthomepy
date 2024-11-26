import unittest
import mock.GPIO as GPIO
from unittest.mock import patch, PropertyMock
from unittest.mock import Mock

from mock.adafruit_bmp280 import Adafruit_BMP280_I2C
from src.smart_room import SmartRoom
from mock.senseair_s8 import SenseairS8


class TestSmartRoom(unittest.TestCase):

    @patch.object(GPIO, "input")
    def test_check_room_occupancy_occupied(self, infrared_sensor_mock: Mock):
        infrared_sensor_mock.return_value = True
        smart_room = SmartRoom()

        is_room_occupied = smart_room.check_room_occupancy()

        infrared_sensor_mock.assert_called_with(smart_room.INFRARED_PIN)
        self.assertTrue(is_room_occupied)


