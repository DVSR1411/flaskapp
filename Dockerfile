FROM python:3.9-slim
MAINTAINER sathwik
WORKDIR /app
COPY . /app
RUN pip install -r requirements.txt
COPY . .
EXPOSE 5000
CMD ["flask", "run", "--host=0.0.0.0"]