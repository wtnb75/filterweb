import unittest
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
