# Use an official Debian image as a base
FROM debian:10

# Set environment variables (placeholders to be replaced by actual values when running the container)
ARG VAULT_ACT_OVERSEER_PASSWORD="default_password"
ARG EXTERNAL_IP="127.0.0.1"
ARG LOCALHOST="127.0.0.1"
# ARG PORT_NUMBER_NEO4J_REST="7687"
ARG PORT_NUMBER="8080"
ARG SERVER_NAME="crusoe.act-overseer.local"

# Install Apache, Python, and other dependencies
RUN apt-get update && \
  apt-get install -y apache2 libapache2-mod-wsgi-py3 python3-pip python2 curl && \
  a2enmod wsgi proxy_http && \
  update-alternatives --install /usr/bin/python python /usr/bin/python3.7 2 && \
  update-alternatives --install /usr/bin/python python /usr/bin/python2 1 && \
  apt-get clean && \
  rm -rf /var/lib/apt/lists/*

# Copy act overseer source codes
COPY . /tmp/act-overseer

# Install Python dependencies
RUN pip3 install --no-cache-dir --force-reinstall /tmp/act-overseer

# Configure Apache and application settings
COPY ./docker-config/act_overseer.conf /etc/apache2/sites-available/

RUN sed -i \
  -e "s/{{ portnumber }}/"$PORT_NUMBER"/" \
  -e "s/{{ server_name }}/"$SERVER_NAME"/" \
  /etc/apache2/sites-available/act_overseer.conf

RUN a2ensite act_overseer.conf && \
  echo "LISTEN "$PORT_NUMBER"" >> /etc/apache2/ports.conf

# Configure endpoint /act to apache2 reverse proxy
RUN sed -i "/<\/VirtualHost>/i \\\tProxyPass /act http://${LOCALHOST}:${PORT_NUMBER}/act\n\tProxyPassReverse /act http://${LOCALHOST}:${PORT_NUMBER}/act" /etc/apache2/sites-available/000-default.conf  

# Replace username, password and server_url that overseer makes calls to
RUN sed -i 's/"user",/"crusoe",/' /usr/local/lib/python3.7/dist-packages/act_overseer/data/act_overseer_config
RUN sed -i 's/"pass",/"'"$VAULT_ACT_OVERSEER_PASSWORD"'",/' /usr/local/lib/python3.7/dist-packages/act_overseer/data/act_overseer_config
RUN sed -i 's/"https:\/\/crusoe.csirt.muni.cz"/"'"$EXTERNAL_IP"'"/' /usr/local/lib/python3.7/dist-packages/act_overseer/data/act_overseer_config

# Setup file permissions and log directories
RUN mkdir -p /var/log/crusoe && \
  touch /var/log/crusoe/act_overseer_rest_api.log /var/log/crusoe/act_decide_to_act.log && \
  chmod 0666 /var/log/crusoe/*.log && \
  cp -r /tmp/act-overseer/act_overseer_rest_api /var/www/ && \
  chown -R www-data:www-data /var/www/act_overseer_rest_api

### CRUSOE DECIDE INSTALL - ACT OVERSEER IS DEPENDENT

# Install neo4j-client needed by Crusoe Decide
RUN pip3 install neo4j-driver==1.7
RUN pip3 install pytest
RUN pip3 install neo4j

COPY ../../crusoe_observe/neo4j-client /tmp/neo4j-client

RUN pip3 install --no-cache-dir --force-reinstall /tmp/neo4j-client

# Set environment variables
ENV MULVALROOT=/opt/mulval
ENV XSBROOT=/opt/XSB
ENV PATH="$PATH:$MULVALROOT/bin:$MULVALROOT/utils:$XSBROOT/bin:$XSBROOT/build"

# Install system packages
RUN apt-get update && apt-get install -y \
  python3.7 \
  python2 \
  python3-pip \
  default-jdk \
  build-essential \
  bison \
  flex \
  ca-certificates-java

# Set Python3.7 as default
RUN update-alternatives --install /usr/bin/python python /usr/bin/python3.7 2 && \
  update-alternatives --install /usr/bin/python python /usr/bin/python2 1

# Install python dependencies
RUN python3.7 -m pip install --upgrade pip

# Fix any broken apt packages
RUN apt-get install -f

# Create necessary directories for installation
RUN mkdir -p /usr/share/man/man1

# Download and extract MULVAL
ADD https://people.cs.ksu.edu/~xou/argus/software/mulval/mulval_1_1.tar.gz /opt/mulval_1_1.tar.gz
RUN tar -xzvf /opt/mulval_1_1.tar.gz -C /opt/

# Download and extract XSB
ADD http://xsb.sourceforge.net/downloads/XSB.tar.gz /opt/XSB.tar.gz
RUN tar -xzvf /opt/XSB.tar.gz -C /opt/

# Problem with guess script - we need to update them
RUN apt-get update && apt-get install -y \
  autoconf \
  automake \
  libtool \
  curl \
  gcc \
  make

# Replace outdated config.guess and config.sub
# 22.4.2024 stopped working - had to use internet archive wayback machine to get the scripts
# RUN curl -o /opt/XSB/build/config.guess 'http://git.savannah.gnu.org/gitweb/?p=config.git;a=blob_plain;f=config.guess;hb=HEAD'
# RUN curl -o /opt/XSB/build/config.sub 'http://git.savannah.gnu.org/gitweb/?p=config.git;a=blob_plain;f=config.sub;hb=HEAD'
COPY ./docker-config/config.sub /opt/XSB/build/
COPY ./docker-config/config.guess /opt/XSB/build/

# Compile XSB
RUN cd /opt/XSB/build && \
  ./configure && \
  ./makexsb

# Set hardcoded classpath jars (example modification)
RUN sed -i 's|^(LIBS=.*)$|LIBS=/opt/mulval/lib/dom4j-1.6.1.jar:/opt/mulval/lib/jaxen-1.1.1.jar:/opt/mulval/lib/mysql-connector-java-5.1.8-bin.jar|' /opt/mulval/src/adapter/Makefile

# Compile MULVAL
RUN cd /opt/mulval && \
  make

# Install and force reinstall of Crusoe decide component (example with a requirements.txt)
COPY ../../crusoe_decide/requirements.txt /tmp/crusoe_decide/requirements.txt
RUN pip3 install -r /tmp/crusoe_decide/requirements.txt
COPY ../../crusoe_decide/ /tmp/crusoe_decide
RUN pip3 install file:///tmp/crusoe_decide --force-reinstall

# Run apache2 service
CMD ["apachectl", "-D", "FOREGROUND"]
# ENTRYPOINT ["service", "apache2", "start"]
