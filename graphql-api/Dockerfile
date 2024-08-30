FROM node:12

RUN mkdir -p /app
WORKDIR /app

ARG GRAPHQL_SERVER_PORT="4001"
ARG NEO4J_URL="bolt://localhost:7687"
ARG NEO4J_USER="neo4j"
ARG NEO4J_PASS="password"

ENV GRAPHQL_SERVER_PORT=${GRAPHQL_SERVER_PORT}
ENV NEO4J_URL=${NEO4J_URL}
ENV NEO4J_USER=${NEO4J_USER}
ENV NEO4J_PASS=${NEO4J_PASS}

COPY package.json .
RUN npm install
COPY . .

RUN cp src/db_config.js.template src/db_config.js

RUN sed -i "s|uri: \"bolt://localhost:7687\",|uri: \""$NEO4J_URL"\",|" src/db_config.js \
  && sed -i "s|user: \"neo4j\",|user: \""$NEO4J_USER"\",|" src/db_config.js \
  && sed -i "s|password: \"password\",|password: \""$NEO4J_PASS"\",|" src/db_config.js

EXPOSE ${GRAPHQL_SERVER_PORT}

CMD ["npm", "start"]
