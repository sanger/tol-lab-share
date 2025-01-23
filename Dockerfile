FROM python:3.13-slim

# Setting PYTHONUNBUFFERED to a non-empty value ensures that the python output is sent straight to
# terminal (e.g. your container log) without being first buffered and that you can see the output
# of your application (e.g. django logs) in real time.
ENV PYTHONUNBUFFERED 1

# Install required libs
RUN apt-get update && \
    apt-get install -y \
    build-essential \
    curl \
    netcat-openbsd \
    git \
    unixodbc-dev \
    libsnappy-dev && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Install Rust and Cargo
RUN curl https://sh.rustup.rs -sSf | sh -s -- -y
ENV PATH="/root/.cargo/bin:${PATH}"

# Install the package manager - pipenv
RUN pip install --upgrade pip && \
    pip install --no-cache-dir pipenv

# Change the working directory for all proceeding operations
WORKDIR /code

# Copy Pipfile and Pipfile.lock
COPY Pipfile .
COPY Pipfile.lock .

# Install both default and dev packages so that we can run the tests against this image
RUN pipenv sync --dev --system && \
    pipenv --clear

# Copy all the source to the image
COPY . .

# Install development dependencies
RUN pipenv install --dev

# Set the entrypoint
ENTRYPOINT ["pipenv", "run", "python", "main.py"]

# Optional: Uncomment and configure the healthcheck if needed
# HEALTHCHECK --interval=1m --timeout=3s \
#     CMD curl -f http://localhost:8000/health || exit 1
