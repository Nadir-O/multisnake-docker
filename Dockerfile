FROM python:3.10

WORKDIR /app

RUN apt-get update && apt-get install -y \
    xvfb \
    x11vnc \
    git \
    fluxbox \
    wget \
    net-tools \
    && rm -rf /var/lib/apt/lists/*

# installer noVNC
RUN git clone https://github.com/novnc/noVNC.git /opt/novnc \
    && git clone https://github.com/novnc/websockify /opt/novnc/utils/websockify

COPY . .

RUN pip install -r requirements.txt

EXPOSE 6080

CMD ["bash", "start.sh"]