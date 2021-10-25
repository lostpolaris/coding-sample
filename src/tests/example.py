import requests
import unittest

"""
run this file inside the test docker container (you can run this locally just make sure requirements are installed)
"""


class TestRequests(unittest.TestCase):
    def test_get_all(self):
        response = requests.get("http://localhost:5000/")
        # get all images
        r = requests.get("http://localhost:5000/images")
        # we get success
        self.assertEqual(r.status_code, 200)
        print(r.text)

    def test_get_tags(self):
        # get only certain images
        # response with cat tags
        r = requests.get("http://localhost:5000/images?name=cat")
        self.assertEqual(r.status_code, 200)
        # no response, no tags of that name
        r = requests.get("http://localhost:5000/images?name=ubuntu")
        self.assertEqual(r.status_code, 200)

    def test_get_image_id(self):
        # get certain image id
        # response with that image_id
        r = requests.get("http://localhost:5000/images/<image_id>")
        self.assertEqual(r.status_code, 200)
        # no response, no image with that id
        r = requests.get("http://localhost:5000/images/<image_id>")
        self.assertEqual(r.status_code, 200)

    def test_post_image(self):
        # post a new image
        file = {"file": open("test_data/rawImage.jpg", "rb")}
        # we get success
        r = requests.post("http://localhost:5000/images", files=file)
        self.assertEqual(r.status_code, 200)
        # we get error, because we already have an image with that hash
        r = requests.post("http://localhost:5000/images", files=file)
        self.assertEqual(r.status_code, 200)


def getSuite():
    suite = unittest.TestSuite()
    suite.addTest(TestRequests("test_get"))
    suite.addTest(TestRequests("test_get_tags"))
    suite.addTest(TestRequests("test_get_image_id"))
    return suite


if __name__ == "__main__":
    runner = unittest.TextTestRunner()
    runner.run(getSuite())
