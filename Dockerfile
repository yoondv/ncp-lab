FROM python:3.14.7-slim

WORKDIR /app

RUN python -m pip install --no-cache-dir fastapi uvicorn

COPY main.py .

USER 10001

EXPOSE 8000

CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
