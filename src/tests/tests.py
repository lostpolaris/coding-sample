import requests
import unittest
import os
from pymongo import MongoClient
from bson.objectid import ObjectId
from bson.json_util import dumps
import json

"""
run this file inside the test docker container
"""


class TestRequests(unittest.TestCase):
    # TODO: mock google vision responses to not add to budget
    def setUp(self):
        mc = MongoClient(os.getenv("ME_CONFIG_MONGODB_URL"))["heb-interview"]["images"]
        self.document = {
            "_id": ObjectId("61774a6aff5273fc3e8e12ed"),
            "descriptions": [
                "tableware",
                "drinkware",
                "dishware",
                "coffee cup",
                "cup",
                "serveware",
                "flowerpot",
                "porcelain",
                "teacup",
                "pottery",
            ],
            "hash": "61614d0f05f1ededf549ff58d5e8008c",
            "label": "1870_2024x.jpg?v=1613168778",
        }
        mc.insert_one(self.document)

    def tearDown(self):
        mc = MongoClient(os.getenv("ME_CONFIG_MONGODB_URL"))["heb-interview"]["images"]
        mc.delete_many({})

    def test_get_all(self):
        # get all images
        r = requests.get("http://localhost:5000/images")
        # we get success
        self.assertEqual(r.status_code, 200)
        self.assertDictEqual(r.json(), {"ok": [json.loads(dumps(self.document))]})

    def test_get_tags(self):
        # get only certain images
        # response with cat tags
        r = requests.get("http://localhost:5000/images?objects=cup")
        self.assertEqual(r.status_code, 200)
        self.assertDictEqual(r.json(), {"ok": [json.loads(dumps(self.document))]})
        # empty response, no tags of that name
        r = requests.get("http://localhost:5000/images?objects=ubuntu")
        self.assertEqual(r.status_code, 200)
        self.assertDictEqual(r.json(), {"ok": []})

    def test_get_image_id(self):
        # get certain image id
        # response with that image_id
        # TODO: this is getting passed in as ObjectId, but it's a string | postman will send as string
        r = requests.get("http://localhost:5000/images/61774a6aff5273fc3e8e12ed")
        self.assertEqual(r.status_code, 200)
        self.assertDictEqual(r.json(), {"ok": [json.loads(dumps(self.document))]})
        # bad response, id is not valid ObjectId
        r = requests.get("http://localhost:5000/images/asdf")
        self.assertEqual(r.status_code, 400)

    def test_post_image(self):
        # post a new image
        with open("./test_data/rawImage.jpg", "rb") as t_file:
            files = {"file": t_file}
            # we get success
            r = requests.post("http://localhost:5000/images/", files=files)
            self.assertEqual(r.status_code, 200)
            self.assertTrue(r.json()["ok"]["id"])
        # post a new image with object detection
        with open("./test_data/DOG-2-superJumbo.jpg", "rb") as t_file:
            files = {"file": t_file}
            # we get success
            r = requests.post(
                "http://localhost:5000/images/", data={"bObjDet": "True"}, files=files
            )
            self.assertEqual(r.status_code, 200)
            self.assertTrue(r.json()["ok"]["id"])
        # post a new image using a URL
        r = requests.post(
            "http://localhost:5000/images/", data={"file": "https://picsum.photos/200"}
        )
        self.assertEqual(r.status_code, 200)
        self.assertTrue(r.json()["ok"]["id"])
        with open("./test_data/rawImage.jpg", "rb") as t_file:
            files = {"file": t_file}
            # we get error, because we already have an image with that hash
            r = requests.post("http://localhost:5000/images/", files=files)
            self.assertEqual(r.status_code, 400)
        # post with no image attached
        r = requests.post("http://localhost:5000/images/")
        self.assertEqual(r.status_code, 400)

    def test_delete_image(self):
        # delete an image
        r = requests.delete("http://localhost:5000/images/61774a6aff5273fc3e8e12ed")
        self.assertEqual(r.status_code, 200)
        self.assertDictEqual(r.json(), {"ok": {"n": 1, "ok": 1.0}})
        # delete an image that doesn't exist
        r = requests.delete("http://localhost:5000/images/61774a6aff5273fc3e8e12ed")
        self.assertEqual(r.status_code, 200)
        self.assertDictEqual(r.json(), {"ok": {"n": 0, "ok": 1.0}})


def getSuite():
    suite = unittest.TestSuite()
    suite.addTest(TestRequests("test_get_all"))
    suite.addTest(TestRequests("test_get_tags"))
    suite.addTest(TestRequests("test_get_image_id"))
    return suite


def postSuite():
    suite = unittest.TestSuite()
    suite.addTest(TestRequests("test_post_image"))
    return suite


def deleteSuite():
    suite = unittest.TestSuite()
    suite.addTest(TestRequests("test_delete_image"))
    return suite


if __name__ == "__main__":
    runner = unittest.TextTestRunner()
    runner.run(getSuite())
    runner.run(postSuite())
    runner.run(deleteSuite())
