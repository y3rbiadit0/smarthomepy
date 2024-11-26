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

    @patch.object(GPIO, "input")
    def test_check_room_occupancy_free(self, infrared_sensor_mock: Mock):
        infrared_sensor_mock.return_value = False
        smart_room = SmartRoom()

        is_room_occupied = smart_room.check_room_occupancy()

        infrared_sensor_mock.assert_called_with(smart_room.INFRARED_PIN)
        self.assertFalse(is_room_occupied)

    @patch.object(GPIO, "input")
    def test_check_enough_light(self, photoresistor_mock: Mock):
        photoresistor_mock.return_value = True
        smart_room = SmartRoom()

        is_there_enough_light = smart_room.check_enough_light()

        photoresistor_mock.assert_called_with(smart_room.PHOTO_PIN)
        self.assertTrue(is_there_enough_light)

    @patch.object(GPIO, "input")
    def test_check_enough_light_not_enough(self, photoresistor_mock: Mock):
        photoresistor_mock.return_value = False
        smart_room = SmartRoom()

        is_there_enough_light = smart_room.check_enough_light()

        photoresistor_mock.assert_called_with(smart_room.PHOTO_PIN)
        self.assertFalse(is_there_enough_light)

    @patch.object(SmartRoom, "check_enough_light")
    @patch.object(SmartRoom, "check_room_occupancy")
    @patch.object(GPIO, "output")
    def test_manage_light_level(self, lightbulb_mock: Mock, check_room_occupancy_mock: Mock, check_enough_light_mock: Mock):
        check_room_occupancy_mock.return_value = True
        check_enough_light_mock.return_value = False

        smart_room = SmartRoom()

        smart_room.manage_light_level()
        lightbulb_mock.assert_called_with(smart_room.LED_PIN, True)



