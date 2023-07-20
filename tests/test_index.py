import unittest
import filterweb
import dacite


class TestIndex(unittest.TestCase):
    @unittest.skipUnless(hasattr(filterweb.input, "InputSSH"), "no paramiko")
    def test_input_ssh(self):
        res = filterweb.open_input(
            "ssh", {"hostname": "example", "command": "echo hello"})
        self.assertTrue(isinstance(res, filterweb.input.InputSSH))

    def test_input_validate(self):
        with self.assertRaises(dacite.exceptions.WrongTypeError):
            filterweb.open_input(
                "http", {"url": {"hello": "world"}})

    def test_input_notfound(self):
        with self.assertRaises(ModuleNotFoundError):
            filterweb.open_input("nonexistent", {})
