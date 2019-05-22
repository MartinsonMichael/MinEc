FROM node:latest as front

WORKDIR /frontend
COPY ./package*.json ./
RUN npm install --silent
COPY . ./
RUN npm run --silent build

FROM nginx:latest as nginx

COPY --from=front frontend/build ./front_static
