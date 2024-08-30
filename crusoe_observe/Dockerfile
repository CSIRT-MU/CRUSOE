# Use Debian 10 as the base image
FROM debian:10

# Install necessary packages
RUN apt-get update && apt-get install -y \
  ruby-full \
  nmap \
  git \
  python2 \
  software-properties-common \
  && rm -rf /var/lib/apt/lists/*

# Install specific Ruby gems
RUN gem install public_suffix -v 4.0.7 \
  && gem install addressable

# Clone the WhatWeb repository
RUN git clone https://github.com/urbanadventurer/WhatWeb.git /opt/whatweb

# Configure WhatWeb
RUN sed -i '/matches/a { :text=>''<script src="https://cdn.muni.cz/DependencyHandler'' },' /opt/whatweb/plugins/umbraco.rb

# Create necessary directories
RUN mkdir -p /root/.ssh /data/flow /opt/celery/config

# Configure apt sources to avoid bugs with updates
RUN sed -i '/https:\/\/deb.debian.org\/debian buster-backports main/d' /etc/apt/sources.list

# Copy private key for Flowmon -- necessary only when connecting to real Flowmon appliance
# COPY <path_to_private_key_on_host> /root/.ssh/id_rsa_crusoe
# RUN chmod 600 /root/.ssh/id_rsa_crusoe

# Install Python and PIP
RUN apt-get update && apt-get install -y python3-pip \
  && rm -rf /var/lib/apt/lists/*

# Copy Crusoe components
COPY . /tmp

# Prerequisites for Crusoe components
RUN apt-get update && apt-get install -y ruby-full nmap git software-properties-common ansible python3-pip
RUN apt-get install zlib1g-dev libxml2-dev libxslt-dev python-dev -y
RUN update-alternatives --install /usr/bin/python python /usr/bin/python3.7 2 && \
  update-alternatives --install /usr/bin/python python /usr/bin/python2 1

# Install Crusoe components
RUN pip3 install --force-reinstall /tmp/cms-component 
RUN pip3 install --force-reinstall /tmp/criticality-estimator
RUN pip3 install --force-reinstall /tmp/cve-connector

RUN apt-get install libffi-dev
RUN python -m pip install --upgrade pip
RUN pip3 install --force-reinstall /tmp/flowmon-connector
RUN pip3 install --force-reinstall /tmp/flowmon-rest-client
RUN pip3 install --force-reinstall /tmp/neo4j-client

RUN pip3 install --force-reinstall /tmp/NETlist-connector
RUN pip3 install --force-reinstall /tmp/nmap-topology-scanner
RUN pip3 install --force-reinstall /tmp/OS-parser-component
RUN pip3 install --force-reinstall /tmp/RTIR-connector
RUN pip3 install --force-reinstall /tmp/sabu-connector
RUN pip3 install --force-reinstall /tmp/services-component
RUN pip3 install --force-reinstall /tmp/vulnerability-component
RUN pip3 install --force-reinstall /tmp/webchecker-component

# Reload Celery configuration by removing and recreating the directory, and copying new content
RUN rm -rf /opt/celery/ \
  && mkdir /opt/celery/ \
  && cp -r /tmp/filler-orchestration-service/* /opt/celery/

# Point neo4j-client to the correct Neo4j address
RUN sed -i 's/bolt,/"bolt:\/\/localhost:7687",/' /usr/local/lib/python3.7/dist-packages/neo4jclient/AbsClient.py

# Install Apache and mod-wsgi
RUN apt-get update && apt-get install -y apache2 libapache2-mod-wsgi-py3 \
  && a2enmod wsgi \
  && a2enmod proxy_http

# Install Java and Neo4j
RUN mkdir -p /usr/share/man/man1 \
  && apt-get install -y default-jre default-jdk \
  && wget -O /etc/apt/trusted.gpg.d/neotechnology.gpg.key https://debian.neo4j.com/neotechnology.gpg.key \
  && echo 'deb [arch=amd64 signed-by=/etc/apt/trusted.gpg.d/neotechnology.gpg.key] https://debian.neo4j.com stable 3.5' > /etc/apt/sources.list.d/neo4j.list \
  && apt-get update && apt-get install -y neo4j=1:3.5.3

# Install additional Python packages
RUN pip3 install requests structlog django djangorestframework

COPY docker-config/*.csv /tmp/local_flows/

# Template and copy configurations
COPY ansible/roles/neo4j/templates/neo4j-rest-wrapper.conf /etc/apache2/sites-available/

ARG NEO4J_REST_PORT=8080
ARG SERVER_NAME="neo4j-rest"
ARG NEO4J_PASSWORD="password"

# neo4j-rest component apache configuration
RUN sed -i \
  -e "s/{{ neo4jrest_port }}/"$NEO4J_REST_PORT"/" \
  -e "s/{{ server_name }}/"$SERVER_NAME"/" \
  /etc/apache2/sites-available/neo4j-rest-wrapper.conf

RUN sed -i "/<\/VirtualHost>/i \\\tProxyPass /rest http://127.0.0.1:"$NEO4J_REST_PORT"/rest\n\tProxyPassReverse /rest http://127.0.0.1:"$NEO4J_REST_PORT"/rest" /etc/apache2/sites-available/000-default.conf

COPY docker-config/neo4j-rest_conf.ini /tmp/neo4j-rest/django/crusoe_django/conf.ini

RUN sed -i "s|^.*neo4j_password =.*$|neo4j_password = "$NEO4J_PASSWORD"|" /tmp/neo4j-rest/django/crusoe_django/conf.ini

RUN cp -r /tmp/neo4j-rest/django /var/www/ \
  && chgrp -R www-data /var/www/django \
  && echo "LISTEN "$NEO4J_REST_PORT"" >> /etc/apache2/ports.conf \
  && a2ensite neo4j-rest-wrapper.conf

# Neo4j Database configuration

COPY ansible/roles/neo4j/files/apoc-3.5.0.2-all.jar /var/lib/neo4j/plugins/

RUN echo "dbms.security.procedures.unrestricted=apoc.load.json, algo.*, apoc.convert.*" >> /etc/neo4j/neo4j.conf \
  && echo "apoc.import.file.use_neo4j_config=true" >> /etc/neo4j/neo4j.conf \
  && echo "apoc.import.file.enabled=true" >> /etc/neo4j/neo4j.conf \
  && echo "dbms.connector.http.listen_address=0.0.0.0:7474" >> /etc/neo4j/neo4j.conf \
  && echo "dbms.connector.bolt.listen_address=0.0.0.0:7687" >> /etc/neo4j/neo4j.conf

# Set Python3.7 as the default Python version
RUN update-alternatives --install /usr/bin/python python /usr/bin/python3.7 2 \
  && update-alternatives --install /usr/bin/python python /usr/bin/python2 1

# Update pip and install dependencies from requirements.txt
COPY ansible/roles/pythonPackages/files/requirements.txt /tmp/
RUN pip3 install --upgrade pip \
  && pip3 install -r /tmp/requirements.txt \
  && rm /tmp/requirements.txt

# Install Redis and configure
RUN apt-get update && apt-get install -y redis-server \
  && mkdir -p /etc/redis /var/redis/6379 /var/log/celery /var/log/crusoe \
  && cp /etc/redis/redis.conf /etc/redis/6379.conf \
  && sed -i "s|daemonize no|daemonize yes|" /etc/redis/6379.conf \
  && sed -i 's|^pidfile|pidfile /var/run/redis_6379.pid|' /etc/redis/6379.conf \
  && sed -i 's|^port 6379|port 6379|' /etc/redis/6379.conf \
  && sed -i 's|^logfile|logfile /var/log/redis_6379.log|' /etc/redis/6379.conf \
  && sed -i 's|^dir|dir /var/redis/6379|' /etc/redis/6379.conf

# Install Supervisor
RUN apt-get update && apt-get install -y supervisor

# Create and configure celery config from template (assuming conf.ini is prepared and available at build context)
COPY docker-config/celery_conf.ini /opt/celery/config/conf.ini

# Configure Supervisor for Celery
COPY docker-config/celeryd.conf /etc/supervisor/conf.d/

# # Fix kombu issues with Python 3.7
RUN sed -i "s|^.*for ep in importlib_metadata.entry_points.*$|\tfor ep in entry_points|" /usr/local/lib/python3.7/dist-packages/kombu/utils/compat.py \
  && sed -i "/^def entrypoints/a     entry_points = importlib_metadata.entry_points()\n    try:\n        entry_points = entry_points.get(namespace, [])\n    except AttributeError:\n        entry_points = entry_points.select(group=namespace)" /usr/local/lib/python3.7/dist-packages/kombu/utils/compat.py \
  && sed -i "s|^.*entry_points = importlib_metadata.*$|    entry_points = importlib_metadata.entry_points()|" /usr/local/lib/python3.7/dist-packages/kombu/utils/compat.py

# Install netcat and curl for neo4j start check, vim just for debug
RUN apt install netcat curl vim -y

COPY ./docker-config/entrypoint.sh /
RUN chmod +x /entrypoint.sh

CMD /entrypoint.sh