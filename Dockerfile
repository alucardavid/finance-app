FROM python:3.10-bullseye


# Install Java
RUN apt-get update && \
    apt-get install -y openjdk-11-jdk && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Set JAVA_HOME environment variable
ENV JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64
ENV PATH=$JAVA_HOME/bin:$PATH
ENV FINANCEENV="prd"

# Set the working directory
WORKDIR /app

# Copy the requirements file into the container
COPY ./requirements.txt /app/requirements.txt

# Install the dependencies
RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt

COPY . .

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]