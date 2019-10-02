# -*- coding:utf-8 -*-
import urllib3
import json
import base64

def recognize(URL, Key, FilePath, languageCode):
    data = {}

    file = open(FilePath, "rb")
    audioContents = base64.b64encode(file.read()).decode("utf8")
    file.close()

    requestJson = {
        "access_key": Key,
        "argument": {
            "language_code": languageCode,
            "audio": audioContents
        }
    }

    http = urllib3.PoolManager()
    response = http.request(
        "POST",
        URL,
        headers={"Content-Type": "application/json; charset=UTF-8"},
        body=json.dumps(requestJson)
    )

    data = response.data
    data = data.decode("utf-8")

    data = data[43:-4]
    return data
