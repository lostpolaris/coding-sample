from flask import Flask, request, Response
from google.cloud import vision
import os
from pymongo import MongoClient
from PIL import Image
from PIL.ExifTags import TAGS

app = Flask("HEB Coding Challenge")
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "secrets.env"
client = vision.ImageAnnotatorClient()


@app.route("/")
def hello_world():
    return "hello world!"


@app.route("/images", methods=["GET"])
@app.route("/images/", methods=["GET", "POST"])
@app.route("/images/<string:imageId>", methods=["GET"])
def get_images(imageId: str = None):
    if request.method == "POST":
        if "file" not in request.files:
            return Response("file not provided", 400)
        # get opt args label and bObjDet
        label = request.form.get("label", request.files["file"].filename)
        bObjDet = request.form.get("bObjDet", False)
        request.get_json()
        # get file from body
        files = request.files["file"]
        # get exif metadata
        # extracting the exif metadata
        img = Image.open(files)
        exifdata = img.getexif()

        # looping through all the tags present in exifdata
        for tagid in exifdata:

            # getting the tag name instead of tag id
            tagname = TAGS.get(tagid, tagid)

            # passing the tagid to get its respective value
            value = exifdata.get(tagid)

            # printing the final result
            print(f"{tagname:25}: {value}")

        if bObjDet:
            # send bytestream to for annotation
            image = vision.Image(content=files.read())
            # performs label detection on the image file
            response = client.label_detection(image=image)
            # debugging to see response
            labels = response.label_annotations
            for label in labels:
                # objects detected
                print(label.description)
        return "ok"
    elif request.method == "GET":
        # return 200 with metadata of selected image
        if imageId:
            return "hiya"
        # return 200 with images of detect objects
        elif request.args.get("objects"):
            return "hello"
        # return 200 with image metadata of all images
        else:
            return "howdy2"

    return 200


if __name__ == "__main__":
    app.run(port=5000, host="0.0.0.0", debug=True)
