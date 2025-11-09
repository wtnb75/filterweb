import unittest
import tempfile
import yaml
from click.testing import CliRunner
from filterweb._cli import cli


class TestCLI(unittest.TestCase):
    def setUp(self):
        pass

    def test_help(self):
        res = CliRunner().invoke(cli, ["--help"])
        self.assertIn("filter", res.output)
        self.assertIn("input", res.output)

    def test_empty(self):
        res = CliRunner().invoke(cli, [])
        self.assertIn("filter", res.output)
        self.assertIn("input", res.output)

    def test_input(self):
        data = {
            "hello": "world",
        }
        with tempfile.NamedTemporaryFile("r+") as tf1:
            with tempfile.NamedTemporaryFile("r+") as tf2:
                yaml.dump(data, tf1)
                tf1.flush()
                conf = {
                    "filename": tf1.name,
                    "parse": "yaml",
                    "select": "/hello",
                }
                yaml.dump(conf, tf2)
                tf2.flush()
                res = CliRunner().invoke(cli, ["input", "file", tf2.name])
                self.assertEqual("world", res.output.strip())

    def test_filter(self):
        data = {
            "name": "world",
        }
        with tempfile.NamedTemporaryFile("r+") as tf1:
            with tempfile.NamedTemporaryFile("r+") as tf2:
                yaml.dump(data, tf1)
                tf1.flush()
                conf = {
                    "template": "hello {{name}}",
                }
                yaml.dump(conf, tf2)
                tf2.flush()
                res = CliRunner().invoke(cli, ["filter", "jinja", tf2.name, tf1.name])
                self.assertEqual("hello world", res.output.strip())
