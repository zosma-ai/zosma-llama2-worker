FROM nvidia/cuda:11.8.0-base-ubuntu22.04

# Remove any third-party apt sources to avoid issues with expiring keys.
RUN rm -f /etc/apt/sources.list.d/*.list

# Install some basic utilities.
RUN apt-get update && apt-get install -y \
    curl \
    ca-certificates \
    sudo \
    git \
    bzip2 \
    libx11-6 \
 && rm -rf /var/lib/apt/lists/*

# Create a working directory.
RUN mkdir /app
WORKDIR /app


RUN apt update
RUN apt-get install nvidia-cuda-toolkit -y
RUN apt install python3 python3-pip -y

COPY requirements.txt ./
RUN pip3 install -r requirements.txt
RUN pip3 install uvicorn fastapi configparser
COPY *.py ./
COPY config.ini ./

EXPOSE 3000

# Set the default command to python3.
ENTRYPOINT ["python3", "chat_api.py"]
