FROM python:3.11.1-slim

WORKDIR /app

# install dependencies
COPY builder/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# copy ALL source files (important)
COPY src/ /app/

# start runpod worker
CMD ["python", "-u", "handler.py"]