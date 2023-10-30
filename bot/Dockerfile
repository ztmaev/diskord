FROM python:3.10-slim

# dir
WORKDIR /bot

# copy
COPY . .

# install
RUN pip install -r requirements.txt

# run
CMD ["python", "main.py"]