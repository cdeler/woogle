FROM python:3

# Set the working directory to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
ADD . /app

# Install any needed packages specified in requirements.txt
RUN pip install --trusted-host pypi.python.org -r requirements.txt

#RUN pip install  -r requirements.txt

# Make port 9999 available to the world outside this container
EXPOSE 9999

# Run app.py when the container launches
CMD ["python", "app.py"]