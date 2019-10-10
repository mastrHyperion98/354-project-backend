FROM python:3.7.4-alpine3.10

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD [ "gunicorn", "-b", "0.0.0.0:8000", "flaskr:create_app()" ]