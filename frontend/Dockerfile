FROM python:3.10-slim

# dir
WORKDIR .

# copy
COPY . .

# install
RUN pip install -r requirements.txt

# run
 CMD gunicorn --bind 0.0.0.0:4321 app:app
# CMD gunicorn --bind 0.0.0.0:4321 --limit-request-line 8190 --limit-request-field_size 2147483648 app:app

