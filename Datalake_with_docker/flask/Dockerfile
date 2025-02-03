FROM python:3.8-slim-buster

RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# RUN apt-get install -y fuse

# RUN apt-get install pkg-config
# RUN brew install pkg-config
# RUN apt-get update
# RUN build-essential

 
WORKDIR /code   


RUN python -m pip install --upgrade pip
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
# RUN pip install mysql-connector-python
EXPOSE 7007
COPY . .
# CMD [ "python", "datalake/app.py" ]