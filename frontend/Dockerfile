FROM python:3.10-slim

# dir
WORKDIR .

# copy
COPY . .

# install
RUN pip install -r requirements.txt

# run
CMD gunicorn --bind 0.0.0.0:4321 app:app