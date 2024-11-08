FROM python:3.12

COPY . .

RUN pip install --no-cache-dir -r requirements.txt

# Make port 8080 available to the world outside this container
EXPOSE 8080

CMD ["python", "src/main.py"]
