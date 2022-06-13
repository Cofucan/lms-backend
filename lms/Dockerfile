FROM python:3.10.1

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Only update packages
RUN apt-get update

# Set working directory
WORKDIR /lms

# copy requirements files
COPY ./requirements.txt /lms/requirements.txt

# install requirements
RUN pip install -r requirements.txt

# Copy codebase
COPY . /lms/

# create a new user
RUN adduser --disabled-password --gecos '' kodecamp

# Set user as the owner of directory
RUN chown -R kodecamp:kodecamp /lms

# Set user to be kodecamp
USER kodecamp
