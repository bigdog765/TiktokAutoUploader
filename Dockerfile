# syntax=docker/dockerfile:1

# Comments are provided throughout this file to help you get started.
# If you need more help, visit the Dockerfile reference guide at
# https://docs.docker.com/go/dockerfile-reference/

# Want to help us make this template better? Share your feedback here: https://forms.gle/ybq9Krt8jtBL3iCk7

ARG PYTHON_VERSION=3.13.1
FROM python:${PYTHON_VERSION}-slim as base

# Prevents Python from writing pyc files.
ENV PYTHONDONTWRITEBYTECODE=1

# Keeps Python from buffering stdout and stderr to avoid situations where
# the application crashes without emitting any logs due to buffering.
ENV PYTHONUNBUFFERED=1

# Install git, build tools, and wget
# Install git, build tools, wget, and curl
RUN apt-get update && apt-get install -y \
    git \
    build-essential \
    wget \
    gnupg \
    curl \
    unzip

#####################################
# Download and install Chrome for Testing
#####################################

# Download the Chrome zip from the provided endpoint.
RUN wget -O /tmp/chrome-linux64.zip "https://storage.googleapis.com/chrome-for-testing-public/132.0.6834.159/linux64/chrome-linux64.zip" && \
    unzip /tmp/chrome-linux64.zip -d /opt && \
    rm /tmp/chrome-linux64.zip

# The zip extracts to /opt/chrome-linux64.
# Optionally, create a symlink so that the chrome binary is available as "chrome".
RUN ln -s /opt/chrome-linux64/chrome /usr/bin/chrome

# Add Chrome's directory to the PATH.
ENV PATH="/opt/chrome-linux64:${PATH}"

#####################################
# Download and install ChromeDriver
#####################################

# Download the ChromeDriver zip from the provided endpoint.
RUN wget -O /tmp/chromedriver.zip "https://chromedriver.storage.googleapis.com/114.0.5735.90/chromedriver_linux64.zip" && \
    unzip /tmp/chromedriver.zip -d /usr/local/bin && \
    rm /tmp/chromedriver.zip && \
    chmod +x /usr/local/bin/chromedriver


# set display port to avoid crash
ENV DISPLAY=:99

WORKDIR /app

# Create a non-privileged user that the app will run under.
# See https://docs.docker.com/go/dockerfile-user-best-practices/
ARG UID=10001
RUN adduser \
    --disabled-password \
    --gecos "" \
    --home "/nonexistent" \
    --shell "/sbin/nologin" \
    --no-create-home \
    --uid "${UID}" \
    appuser

# Download dependencies as a separate step to take advantage of Docker's caching.
# Leverage a cache mount to /root/.cache/pip to speed up subsequent builds.
# Leverage a bind mount to requirements.txt to avoid having to copy them into
# into this layer.
RUN --mount=type=cache,target=/root/.cache/pip \
    --mount=type=bind,source=requirements.txt,target=requirements.txt \
    python -m pip install -r requirements.txt

# Switch to the non-privileged user to run the application.
USER appuser

# Copy the source code into the container.
COPY . .

# Expose the port that the application listens on.
EXPOSE 8000

# Run the application.
# Run Flask in debug mode
ENV FLASK_APP=main.py
# Run the application directly with Python
CMD ["python", "main.py"]
