FROM python:3.11.1-slim

WORKDIR /

RUN pip install --no-cache-dir -r requirements.txt


# Command to run when the container starts
CMD ["python", "-u", "/handler.py"]