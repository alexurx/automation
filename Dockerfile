FROM jenkins/ssh-agent:latest

# Install PHP-CLI and dependencies
RUN apt-get update && \
    apt-get install -y \
    php-cli \
    php-curl \
    php-json \
    php-mbstring \
    php-xml \
    composer \
    git \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Create agent directory
RUN mkdir -p /home/jenkins/agent
WORKDIR /home/jenkins/agent