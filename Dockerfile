FROM python:3.9-slim
WORKDIR /
COPY . /
RUN pip3 install -r requirements.txt
RUN apt-get update
RUN apt-get install nano
CMD ["python3", "converter.py"]
