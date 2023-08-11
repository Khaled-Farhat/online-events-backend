FROM nginx:1.25.1

COPY http.conf.template /etc/nginx/templates/http.conf.template
COPY nginx.conf /etc/nginx/nginx.conf

CMD ["nginx", "-g", "daemon off;"]
