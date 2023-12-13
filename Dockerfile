# syntax=docker/dockerfile:1
FROM python:3.9-slim
WORKDIR /app
COPY . /app
RUN pip install -r requirements.txt
EXPOSE 80
ENV NAME World
CMD ["python", "main.py"]