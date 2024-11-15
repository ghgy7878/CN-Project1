# setting the base image.
FROM python:2.7

# setting a key-value label for the Docker image
LABEL maintainer="kapi"

# copy files from the host to the container filesystem. 
COPY . /app

#  defines the working directory within the container
WORKDIR /app

# run commands within the container.
RUN pip install -r requirements.txt
RUN python init_db.py

#Expose the application port 3111
EXPOSE 3111

# provide a command to run on container start.
CMD [ "python", "app.py" ]
