FROM ubuntu:jammy
LABEL maintainer=ChangwooLim

ENV TZ="Asia/Seoul"
ENV DEBIAN_FRONTEND=noninteractive

# Install Python 3.12
RUN apt-get update && apt-get install -y python3-full python3-pip \
    libreoffice language-pack-ko fonts-nanum-* fontconfig \
    wget

RUN fc-cache -f -v

# Libreoffice hwp dependency
RUN wget https://github.com/ebandal/H2Orestart/releases/latest/download/H2Orestart.oxt
RUN unopkg add --shared H2Orestart.oxt

WORKDIR /app

COPY requirements.txt .

RUN pip3 install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

ENTRYPOINT ["uvicorn", "main:app", "--host=0.0.0.0", "--reload"]