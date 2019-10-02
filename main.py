import json
import base64
import logging
import telegram
import requests
import subprocess
from telegram.ext import Updater
from speech_recognition import recognize

# ETRI Speech Recognition Init
ETRI_URL = "http://aiopen.etri.re.kr:8000/WiseASR/Recognition"
ETRI_Key = '' # Enter your ETRI API Key
ogaFilePath = '' # oga File Path
wavFilePath = '' # wav File Path
jsonFilePath = './interview.json'
languageCode = "korean"

TOKEN = '' # Enter your HTTP API Token
FILEURL = 'https://api.telegram.org/file/bot{}/'.format(TOKEN)
URL = 'https://api.telegram.org/bot{}/'.format(TOKEN)

def get_url(url):
  response = requests.get(url)
  content = response.content.decode("utf8")
  return content

def get_json_from_url(url):
  content = get_url(url)
  js = json.loads(content)
  return js

def get_updates():
  url = URL + "getUpdates"
  js = get_json_from_url(url)
  return js

def get_file_updates(file_id):
  url = URL + "getFile?file_id={}".format(file_id)
  js = get_json_from_url(url)
  return js

def get_chat_id(updates):
  num_updates = len(updates["result"])
  last_update = num_updates - 1
  chat_id = updates["result"][last_update]["message"]["chat"]["id"]
  return chat_id

def get_last_text(updates):
  num_updates = len(updates["result"])
  last_update = num_updates - 1
  text = updates["result"][last_update]["message"]["text"]
  return text

def get_file_id(updates):
  num_updates = len(updates["result"])
  last_update = num_updates - 1
  file_id = updates["result"][last_update]["message"]["voice"]["file_id"]
  return file_id

def get_file_path(updates):
  file_path = updates["result"]["file_path"]
  return file_path

def download_file(file_path):
  url = FILEURL + file_path
  r = requests.get(url)
  with open(ogaFilePath, 'wb') as f:
    f.write(r.content)

def send_message(text, chat_id):
  url = URL + "sendMessage?text={}&chat_id={}".format(text, chat_id)
  get_url(url)

def response_message(text, chat_id):
  json_data = open(jsonFilePath).read()
  data = json.loads(json_data)

  try:
    text = data[str(text)]
  except:
    text = "제 한계를 넘어섰습니다. 죄송합니다."
  url = URL + "sendMessage?text={}&chat_id={}".format(text, chat_id)
  get_url(url)

def start_new_section():
  updater = Updater(TOKEN, use_context=True)
  updater.start_polling()
  updater.dispatcher.stop()
  updater.job_queue.stop()
  updater.stop()

#def send_file(chat_id, file_id):

def main():
  start_new_section()
  pre_file_id = "None"
  file_id = "None"

  while True:
    # get File id and user id
    try:
      chat_id = get_chat_id(get_updates())
      try:
        file_id = get_file_id(get_updates())
        file_path = get_file_path(get_file_updates(file_id))
        state = 1
      except:
        file_id = "None"
        file_path = "None"
        state = 2
    except:
      chat_id = "None"
      state = 0

    # Download New voice
    if state == 1:
      download_file(file_path)
      subprocess.call(['ffmpeg', '-loglevel', 'quiet', '-y', '-i', ogaFilePath, '-ar', '16000', wavFilePath])
      recognized = recognize(ETRI_URL, ETRI_Key, wavFilePath, languageCode)
      # Add Speech Synthesis Part
      print("Recognized String :", recognized)
      response_message(recognized, chat_id)
      start_new_section()
    elif state == 2:
      useage = "DSP봇은 음성 인식으로 동작합니다. 음성을 입력해 주세요."
      send_message(useage, chat_id)
      start_new_section()
    state = 0


if __name__ == '__main__':
  main()
