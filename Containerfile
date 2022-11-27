FROM python:3.9-alpine as builder

WORKDIR /opt

COPY ["bot.py", "/opt/"]
COPY requirements.txt requirements.txt

RUN pip3 install --no-cache-dir -r requirements.txt

FROM builder

CMD ["python3", "/opt/bot.py"]