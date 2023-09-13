FROM python:3.10-slim

# dir
WORKDIR /disbot_v2

# copy
COPY . .

# install
RUN pip install -r requirements.txt

# port
EXPOSE 4321

# run
CMD gunicorn --bind 0.0.0.0:4321 webapp2:app