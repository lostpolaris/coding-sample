from flask import Flask, request
from google.cloud import vision
import os

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
        request.get_json()
        # get file from body
        files = request.files["file"]
        # send bytestream to for annotation
        image = vision.Image(content=files.read())
        # performs label detection on the image file
        response = client.label_detection(image=image)
        # debugging to see response
        labels = response.label_annotations
        print(labels)
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
            return "howdy"

    return 200


if __name__ == "__main__":
    app.run(port=5000, host="0.0.0.0", debug=True)
