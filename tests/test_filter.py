import unittest
import os
import tempfile
import filterweb.filter


class TestFilter(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_jinja2_file(self):
        with tempfile.NamedTemporaryFile("r+") as tf:
            tf.write("hello {{name}}")
            tf.flush()
            ifp = filterweb.filter.FilterJinja({
                "template_file": os.path.basename(tf.name),
                "template_basedir": os.path.dirname(tf.name),
            })
            res = ifp.apply({"name": "world"})
            self.assertEqual("hello world", res)

    def test_jinja2_str(self):
        ifp = filterweb.filter.FilterJinja({
            "template": "hello {{name}}"
        })
        res = ifp.apply({"name": "world"})
        self.assertEqual("hello world", res)

    def test_jinja2_invalid(self):
        with self.assertRaises(ValueError) as ex:
            filterweb.filter.FilterJinja({})
        self.assertIn("template or template_file", ex.exception.args[0])
