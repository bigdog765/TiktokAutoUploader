FROM selenium/standalone-chrome:131.0

USER root

# install Python3, pip, venv, Xvfb, and Node.js dependencies
RUN apt-get update && apt-get install -y \
    python3-pip \
    python3-venv \
    xvfb \
    build-essential \
    libffi-dev \
    python3-dev \
    curl && \
    # Install Node.js (here using Node 18.x)
    curl -fsSL https://deb.nodesource.com/setup_18.x | bash - && \
    apt-get install -y nodejs && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# set Python-related environment variables
ENV PYTHONUNBUFFERED=1
ENV DISPLAY=:99

# create and activate a virtual environment
RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# set up the working directory
WORKDIR /app

# copy and install requirements.txt
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && pip install --no-cache-dir -r requirements.txt

# copy the Python test script
COPY . .

RUN cd tiktok_uploader/tiktok-signature && npm install


# ensure correct permissions for /tmp/.X11-unix to prevent Xvfb from issuing warnings
RUN mkdir -p /tmp/.X11-unix && chmod 1777 /tmp/.X11-unix

# change ownership of venv to seluser and switch users
RUN chown -R seluser:seluser /opt/venv /app
USER seluser

ENV FLASK_APP=main.py
# # Expose the port that the application listens on.
EXPOSE 8000

# run Xvfb and the Python script
CMD ["sh", "-c", "Xvfb :99 -ac 2>/dev/null & python3 -u main.py"]

# # Expose the port that the application listens on.
# EXPOSE 8000

# # Run the application.
# # Run Flask in debug mode
# ENV FLASK_APP=main.py
# # Run the application directly with Python
# CMD ["python", "main.py"]
