### STAGE 1: Build ###
FROM node:12 AS build
WORKDIR /usr/src/app
COPY package.json package-lock.json ./
RUN npm install --legacy-peer-deps
COPY . .

ARG NEO4J_REST_URL="http://localhost/"
ARG FLOWER_URL="http://localhost:5555/"
ARG ACT_API="http://localhost/act"
ARG GRAPHQL_URL="http://localhost:4001/graphql"
ARG FIREWALL_PAO_URL="http://localhost/firewall"
ARG RECOMMENDER_API="http://localhost/recommender"

RUN sed -i "s|baseUrl: 'http://localhost/',|baseUrl: '"$NEO4J_REST_URL"',|" ./src/environments/environment.prod.ts \
  && sed -i "s|flowerUrl: 'http://localhost:5555/',|flowerUrl: '"$FLOWER_URL"',|" ./src/environments/environment.prod.ts \
  && sed -i "s|tmpActApi: 'http://localhost/act',|tmpActApi: '"$ACT_API"',|" ./src/environments/environment.prod.ts \
  && sed -i "s|graphqlApi: 'http://localhost:4001/graphql',|graphqlApi: '"$GRAPHQL_URL"',|" ./src/environments/environment.prod.ts \
  && sed -i "s|firewallApi: 'http://localhost/firewall',|firewallApi: '"$FIREWALL_PAO_URL"',|" ./src/environments/environment.prod.ts \
  && sed -i "s|recommenderApi: 'http://localhost/recommmender',|recommenderApi: '"$RECOMMENDER_API"',|" ./src/environments/environment.prod.ts

RUN npm run build

### STAGE 2: Run ###
FROM nginx
COPY ./docker-config/dashboard.conf /etc/nginx/nginx.conf
COPY --from=build /usr/src/app/dist /usr/share/nginx/html

