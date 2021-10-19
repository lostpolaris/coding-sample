FROM docker.io/python

WORKDIR /app
COPY . /app/

RUN pip install -r requirements.txt

EXPOSE 9999
CMD [ "python", "api.py" ]
