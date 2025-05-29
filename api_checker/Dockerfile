FROM python:3.8-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
COPY ../config/api_config.json ./config/
CMD ["python", "api_checker.py"]