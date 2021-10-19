FROM docker.io/python

COPY . .

RUN pip install -r requirements.txt

EXPOSE 9999
CMD [ "python", "api.py" ]
