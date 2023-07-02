import unittest
from unittest.mock import patch, MagicMock
import os
import json
import tempfile
import sqlite3
import filterweb.input


class TestInput(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_file(self):
        with tempfile.NamedTemporaryFile("r+") as tf:
            json.dump({"hello": ["world", "earth"]}, fp=tf)
            tf.flush()
            ifp = filterweb.input.InputFile({
                "filename": tf.name,
                "parse": "json",
                "select": "/hello/1",
            })
            res = ifp.process()
            self.assertEqual("earth", res)

    def test_process(self):
        ifp = filterweb.input.InputProcess({
            "command": ["jo", "hello=world"],
            "parse": "json",
        })
        res = ifp.process()
        self.assertEqual({"hello": "world"}, res)

    def test_jsonlines(self):
        with tempfile.NamedTemporaryFile("r+") as tf:
            json.dump({"hello": ["world", "earth"]}, fp=tf)
            json.dump({"hello": ["xyz"]}, fp=tf)
            tf.flush()
            ifp = filterweb.input.InputFile({
                "filename": tf.name,
                "parse": "jsonl",
                "select": "/1/hello/0",
            })
            res = ifp.process()
            self.assertEqual("xyz", res)

    def test_csv(self):
        with tempfile.NamedTemporaryFile("r+") as tf:
            tf.write("\n".join([
                "title,value",
                "hello,1",
                "world,2",
            ]))
            tf.flush()
            ifp = filterweb.input.InputFile({
                "filename": tf.name,
                "parse": "csv",
                "select": "/1/title",
            })
            res = ifp.process()
            self.assertEqual("world", res)

    def test_xml(self):
        with tempfile.NamedTemporaryFile("r+") as tf:
            tf.write("""<x><a hello="world">text1</a></x>""")
            tf.flush()
            ifp = filterweb.input.InputFile({
                "filename": tf.name,
                "parse": "xml",
                "select": "/x/a",
            })
            res = ifp.process()

            self.assertEqual({"@hello": "world", "#text": "text1"}, res)

    def test_sqlite3(self):
        with tempfile.NamedTemporaryFile("r+") as tf:
            db = sqlite3.connect(tf.name)
            cur = db.cursor()
            cur.execute("create table tbl1 (id int, val varchar)")
            ins = "insert into tbl1 (id, val) values (?, ?)"
            cur.executemany(ins, [(1, "hello"), (2, "world")])
            db.commit()
            db.close()
            conf = {"database": tf.name,
                    "query": "select * from tbl1", "select": "/1/val"}
            ifp = filterweb.input.InputSQLite3(conf)
            res = ifp.process()
            self.assertEqual("world", res)

    def test_sqlite3_ro(self):
        with tempfile.NamedTemporaryFile("r+") as tf:
            db = sqlite3.connect(tf.name)
            cur = db.cursor()
            cur.execute("create table tbl1 (id int, val varchar)")
            ins = "insert into tbl1 (id, val) values (?, ?)"
            cur.executemany(ins, [(1, "hello"), (2, "world")])
            db.commit()
            db.close()
            conf = {"database": tf.name,
                    "query": "update tbl1 set val='abc' where id==1"}
            with self.assertRaises(sqlite3.OperationalError) as e:
                ifp = filterweb.input.InputSQLite3(conf)
                ifp.process()
            self.assertIn("readonly database", e.exception.args[0])


ssh_host = os.getenv("INPUT_SSH_HOST", None)


@unittest.skipUnless(hasattr(filterweb.input, "InputSSH"), "no paramiko")
class TestInputSSH(unittest.TestCase):
    @unittest.skipUnless(ssh_host, "no ssh host")
    def test_ssh(self):
        conf = {
            "hostname": ssh_host,
            "command": """echo '{"hello": "world"}'""",
            "params": json.loads(os.getenv("INPUT_SSH_PARAMS", "{}")),
            "parse": "json",
        }
        ifp = filterweb.input.InputSSH(conf)
        res = ifp.process()
        self.assertEqual({"hello": "world"}, res)

    def test_ssh_mock(self):
        conf = {
            "hostname": "hello.world",
            "command": "hello world",
            "params": json.loads(os.getenv("INPUT_SSH_PARAMS", "{}")),
            "input": "test",
            "parse": "json",
        }
        with patch("paramiko.SSHClient") as cl:
            stdin = MagicMock()
            stdout = MagicMock()
            stdout.read.return_value = b'{"hello": "world"}\n'
            stderr = MagicMock()
            cl.return_value.exec_command.return_value = (stdin, stdout, stderr)
            ifp = filterweb.input.InputSSH(conf)
            res = ifp.process()
            self.assertEqual({"hello": "world"}, res)
            stdin.write.assert_called_once_with("test")
            stdin.close.assert_called_once_with()
            stdout.read.assert_called_once_with()
            cl.return_value.close.assert_called_once_with()
            cl.return_value.connect.assert_called_once_with(
                hostname="hello.world")
            cl.return_value.set_missing_host_key_policy.assert_called_once()
            cl.return_value.exec_command.assert_called_once_with(
                command="hello world", environment=None, get_pty=False, timeout=None)
