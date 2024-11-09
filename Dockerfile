FROM image-requirements

WORKDIR /app

COPY src/ /app/src

CMD ["ECHO 'Listing files'"]
CMD ["ls"]

CMD ["fastapi", "run", "src/main.py", "--port", "80"]

# # Make port 8080 available to the world outside this container
# EXPOSE 8080

# CMD ["python", "src/main.py"]
