from python:3

copy app.py requirements.txt ./

run pip3 install -r requirements.txt

expose 8000

cmd gunicorn app:app --bind 0.0.0.0 --log-file=-
