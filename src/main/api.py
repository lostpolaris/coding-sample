from typing import Any
from flask import Flask, request, Response
from google.cloud import vision
import os
from pymongo import MongoClient
from bson.objectid import ObjectId
from bson.json_util import dumps
import hashlib
import json
import requests
import logging

app = Flask("HEB Coding Challenge")
mc = MongoClient(os.getenv("ME_CONFIG_MONGODB_URL"))["heb-interview"]["images"]
client = vision.ImageAnnotatorClient()
logger = logging.getLogger(__name__)


@app.route("/images", methods=["GET"])
@app.route("/images/", methods=["GET", "POST"])
@app.route("/images/<string:imageId>", methods=["GET", "DELETE"])
def images(imageId: str = None):
    if request.method == "POST":
        if "file" in request.files:
            # get file and file_name from body
            im_file = request.files["file"].read()
            t_label = request.files["file"].filename
            image = vision.Image(content=im_file)
        elif "file" in request.form:
            # file exists as url, get file and get filename
            url = request.form.get("file")
            t_label = os.path.basename(url)
            im_file = requests.get(url).content
            image = vision.Image(source=vision.ImageSource(image_uri=url))
        else:
            return Response("file not provided", 400)

        # get opt args label and bObjDet
        label = request.form.get("label", t_label)
        bObjDet = request.form.get("bObjDet", False)
        # create basic metadata
        obj = {
            "label": label,
            "hash": hashlib.md5(im_file).hexdigest(),
        }

        # return error if file_hash is in db
        if mc.find_one({"hash": obj.get("hash")}):
            return Response("file already exists", 400)
        # if object det is enabled
        if bObjDet:
            # send bytestream to for annotation
            response = client.label_detection(image=image)
            if response.error.message:
                return Response(
                    "{}\nFor more info on error messages, check: "
                    "https://cloud.google.com/apis/design/errors".format(
                        response.error.message
                    ),
                    500,
                )
            # fill out descriptions
            obj["descriptions"] = [
                description.description.lower()
                for description in response.label_annotations
            ]

        # insert document to mongo
        _id = mc.insert_one(obj)
        return {
            "ok": {
                "label": label,
                "id": str(_id.inserted_id),
                "descriptions": obj.get("descriptions", None),
            }
        }
    elif request.method == "GET":
        # return 200 with metadata of selected image
        if imageId:
            if not ObjectId.is_valid(imageId):
                return Response("invalid id", 400)
            return {"ok": json.loads(dumps(mc.find({"_id": ObjectId(imageId)})))}
        # return 200 with images of detect objects
        elif request.args.get("objects"):
            l_obj = request.args.get("objects").lower().split(",")
            return {
                "ok": json.loads(dumps((mc.find({"descriptions": {"$in": l_obj}}))))
            }
        # return 200 with image metadata of all images
        else:
            return {"ok": json.loads(dumps((mc.find())))}
            # lol

    elif request.method == "DELETE":
        if not mc.find_one({"_id": ObjectId(imageId)}):
            return Response("file does not exist", 400)
        # delete image from db
        return {"ok": mc.remove({"_id": ObjectId(imageId)})}

    return 200


if __name__ == "__main__":
    app.run(port=5000, host="0.0.0.0", debug=True)
