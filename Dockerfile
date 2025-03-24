# ✅ Use official Python base
FROM python:3.10-slim

# ✅ Install Chrome dependencies
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    unzip \
    curl \
    fonts-liberation \
    libappindicator3-1 \
    libasound2 \
    libatk-bridge2.0-0 \
    libatk1.0-0 \
    libcups2 \
    libdbus-1-3 \
    libgdk-pixbuf2.0-0 \
    libnspr4 \
    libnss3 \
    libx11-xcb1 \
    libxcomposite1 \
    libxdamage1 \
    libxrandr2 \
    xdg-utils \
    --no-install-recommends && apt-get clean

# ✅ Install Chrome (headless)
RUN wget -q https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb && \
    apt install ./google-chrome-stable_current_amd64.deb -y

# ✅ Create app folder
WORKDIR /app
COPY . /app

# ✅ Install dependencies
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# ✅ Start app
CMD ["python", "news_collector.py"]
