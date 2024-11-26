import unittest
from unittest.mock import Mock
from unittest.mock import patch, PropertyMock

import mock.GPIO as GPIO
from mock.adafruit_bmp280 import Adafruit_BMP280_I2C
from mock.senseair_s8 import SenseairS8
from src.smart_room import SmartRoom


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
    def test_manage_light_level_not_enough_light_and_person_in_the_room(self,
                                                                        lightbulb_mock: Mock,
                                                                        check_room_occupancy_mock: Mock,
                                                                        check_enough_light_mock: Mock):
        check_room_occupancy_mock.return_value = True
        check_enough_light_mock.return_value = False

        smart_room = SmartRoom()

        smart_room.manage_light_level()
        lightbulb_mock.assert_called_with(smart_room.LED_PIN, True)
        self.assertTrue(smart_room.light_on)

    @patch.object(SmartRoom, "check_enough_light")
    @patch.object(SmartRoom, "check_room_occupancy")
    @patch.object(GPIO, "output")
    def test_manage_light_level_turn_off_otherwise(self, lightbulb_mock: Mock,
                                                   check_room_occupancy_mock: Mock,
                                                   check_enough_light_mock: Mock):
        check_room_occupancy_mock.return_value = False
        check_enough_light_mock.return_value = False

        smart_room = SmartRoom()

        smart_room.manage_light_level()
        lightbulb_mock.assert_called_with(smart_room.LED_PIN, False)
        self.assertFalse(smart_room.light_on)

    @patch.object(SmartRoom, "change_servo_angle")
    def test_manage_window_open_window_scenario(self, change_servo_angle: Mock):
        with patch("mock.adafruit_bmp280.Adafruit_BMP280_I2C.temperature",
                   new_callable=PropertyMock) as mock_temperature:
            mock_temperature.side_effect = [18, 21]

            smart_room = SmartRoom()

            smart_room.manage_window()
            change_servo_angle.assert_called_with(2)  # duty_cycle = (0/18) + 2
            self.assertTrue(smart_room.window_open)

    @patch.object(SmartRoom, "change_servo_angle")
    def test_manage_window_close_window_scenario(self, change_servo_angle: Mock):
        with patch("mock.adafruit_bmp280.Adafruit_BMP280_I2C.temperature",
                   new_callable=PropertyMock) as mock_temperature:
            mock_temperature.side_effect = [19, 21]

            smart_room = SmartRoom()

            smart_room.manage_window()
            change_servo_angle.assert_called_with(12)  # duty_cycle = (180/18) + 2
            self.assertFalse(smart_room.window_open)

    @patch.object(Adafruit_BMP280_I2C, "temperature", new_callable=PropertyMock)
    @patch.object(SmartRoom, "change_servo_angle")
    def test_manage_window_temp_out_range_scenario(self, change_servo_angle: Mock,
                                                   mock_temperature: PropertyMock):
        mock_temperature.side_effect = [16, 31]

        smart_room = SmartRoom()

        smart_room.manage_window()
        change_servo_angle.assert_called_with(12)  # duty_cycle = (180/18) + 2
        self.assertFalse(smart_room.window_open)

    @patch.object(SenseairS8, "co2")
    @patch.object(GPIO, "output")
    def test_monitor_air_quality_poor_quality(self, mock_fan_output: Mock,
                                              mock_co2_sensor: Mock):
        mock_co2_sensor.return_value = 801
        smart_room = SmartRoom()
        smart_room.monitor_air_quality()

        mock_fan_output.assert_called_with(smart_room.FAN_PIN, True)
        self.assertTrue(smart_room.fan_on)

    @patch.object(SenseairS8, "co2")
    @patch.object(GPIO, "output")
    def test_monitor_air_quality_good_quality(self, mock_fan_output: Mock,
                                              mock_co2_sensor: Mock):
        mock_co2_sensor.return_value = 499
        smart_room = SmartRoom()
        smart_room.monitor_air_quality()

        mock_fan_output.assert_called_with(smart_room.FAN_PIN, False)
        self.assertFalse(smart_room.fan_on)
