# ✅ Use a full Debian base with Python
FROM python:3.10-slim

# ✅ Install Chrome dependencies
RUN apt-get update && apt-get install -y \
    wget unzip gnupg curl \
    libglib2.0-0 libnss3 libgconf-2-4 libfontconfig1 libxss1 \
    libappindicator3-1 libasound2 libxtst6 xdg-utils fonts-liberation \
    libx11-xcb1 libxcomposite1 libxdamage1 libxrandr2 libgtk-3-0 \
    --no-install-recommends && apt-get clean

# ✅ Install Chrome
RUN wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb && \
    dpkg -i google-chrome-stable_current_amd64.deb || apt-get -fy install

# ✅ Set workdir
WORKDIR /app
COPY . .

# ✅ Install Python packages
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# ✅ Start script
CMD ["python", "news_collector.py"]
