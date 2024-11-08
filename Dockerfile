FROM python:3.12

WORKDIR /app

COPY . .

RUN pip install -r requirements.txt

CMD ["ls"]


# # Make port 8080 available to the world outside this container
# EXPOSE 8080

# CMD ["python", "src/main.py"]
