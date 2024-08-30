# Use Debian 10 as the base image
FROM debian:10

# SHELL ["/bin/bash", "-c"]

# Install Apache, Python, and other dependencies
RUN apt-get update && \
  apt-get install -y netcat vim apache2 libapache2-mod-wsgi-py3 python3-pip python2 curl software-properties-common && \
  a2enmod wsgi proxy_http && \
  update-alternatives --install /usr/bin/python python /usr/bin/python3.7 2 && \
  update-alternatives --install /usr/bin/python python /usr/bin/python2 1 && \
  apt-get clean && \
  rm -rf /var/lib/apt/lists/*

# Update Debian repository URLs to support archive backports
RUN sed -i 's|deb https://deb.debian.org/debian buster-backports main|deb https://archive.debian.org/debian buster-backports main|g' /etc/apt/sources.list \
  && sed -i 's|deb-src https://deb.debian.org/debian buster-backports main|deb-src https://archive.debian.org/debian buster-backports main|g' /etc/apt/sources.list

# Set Python3.7 as the default Python
RUN update-alternatives --install /usr/bin/python python /usr/bin/python3.7 2 \
  && update-alternatives --install /usr/bin/python python /usr/bin/python2 1

# Define build argument and environment variable
ARG PROXY_URL="http://127.0.0.1"
ARG PORT_NUMBER="8086"
ARG URL_PATH="firewall"
ARG DST_WRAPPER="simulated-pao-firewall"
ARG WRAPPER="firewall_wrapper"
ARG SERVER_NAME="simulated-pao-firewall.local"
ARG EXTERNAL_IP="127.0.0.1"
ARG VAULT_NEO4J_PASSWORD="password"
ARG PAO_IP="localhost"
ARG PAO_NAME="firewall"
ARG PORTNUMBER="8080"
ARG MAXCAPACITY="0"
ARG USEDCAPACITY="0"
ARG FREECAPACITY="0"

RUN pip3 install requests structlog django djangorestframework

# Copy the application component
COPY ./${DST_WRAPPER} /tmp/act-component/${DST_WRAPPER}

# Configure Apache site
COPY ./docker-config/generic_wrapper.conf /tmp/generic_wrapper.conf

# Rename generic_wrapper to wrapper by component
RUN mv /tmp/generic_wrapper.conf /etc/apache2/sites-available/$WRAPPER.conf

RUN sed -i \
  -e "s/{{portnumber}}/"$PORT_NUMBER"/g" \
  -e "s/{{server_name}}/"$SERVER_NAME"/g" \
  -e "s/{{dst_wrapper}}/"$DST_WRAPPER"/g" \
  -e "s/{{wrapper}}/"$WRAPPER"/g" \
  /etc/apache2/sites-available/"$WRAPPER".conf

RUN echo "LISTEN "$PORT_NUMBER"" >> /etc/apache2/ports.conf \
  && sed -i "/<\/VirtualHost>/i \\\tProxyPass /"$URL_PATH" "$PROXY_URL":"$PORT_NUMBER"/"$URL_PATH"\n\tProxyPassReverse /"$URL_PATH" "$PROXY_URL":"$PORT_NUMBER"/"$URL_PATH"" /etc/apache2/sites-available/000-default.conf

RUN a2ensite $WRAPPER.conf

RUN a2enmod proxy proxy_http

#Copy directory to /var/www and set permissions
RUN cp -r /tmp/act-component/"$DST_WRAPPER" /var/www/ \
  && chown -R www-data:www-data /var/www/"$DST_WRAPPER" \
  && chmod -R 755 /var/www/"$DST_WRAPPER"

# Install neo4j package
RUN pip3 install neo4j_driver==1.7.1

# Add the Neo4j script
COPY ./docker-config/neo4j_update.py /tmp/

RUN sed -i \
  -e "s/{{ external_ip }}/"$EXTERNAL_IP"/g" \
  -e "s/{{ vault_neo4j_password }}/"$VAULT_NEO4J_PASSWORD"/g" \
  -e "s/{{ ip }}/"$PAO_IP"/g" \
  -e "s/{{ pao_name }}/"$PAO_NAME"/g" \
  -e "s/{{ portnumber }}/"$PORTNUMBER"/g" \
  -e "s/{{ maxCapacity }}/"$MAXCAPACITY"/g" \
  -e "s/{{ usedCapacity }}/"$USEDCAPACITY"/g" \
  -e "s/{{ freeCapacity }}/"$FREECAPACITY"/g" \
  /tmp/neo4j_update.py
  
# Expose port on which act component listens
EXPOSE 80
EXPOSE 8086

COPY ./docker-config/entrypoint.sh /
RUN chmod +x /entrypoint.sh

CMD /entrypoint.sh
