FROM python:3.10.14-slim-bullseye
WORKDIR /app
COPY requirements.txt ./
RUN pip install -r requirements.txt
COPY src /app
CMD [ "python", "main.py" ]