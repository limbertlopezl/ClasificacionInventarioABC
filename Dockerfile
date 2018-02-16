FROM vevende/python3:latest

COPY requirements.txt /requirements.txt

RUN gosu app pip install --no-cache-dir -r /requirements.txt

COPY . /app
RUN make static
CMD ["uwsgi", "--show-config", "--ini", "/app/uwsgi.ini"]
#CMD ["python", "src/manage.py", "runserver", "0.0.0.0:8000"]
