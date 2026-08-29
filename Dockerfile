FROM nginx:alpine

# Remove default site
RUN rm /etc/nginx/conf.d/default.conf

# Copy custom config
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copy app files
COPY src/ /usr/share/nginx/html/
COPY data/ /usr/share/nginx/html/data/
COPY assets/ /usr/share/nginx/html/assets/

EXPOSE 80

HEALTHCHECK --interval=30s --timeout=3s CMD curl -f http://localhost/healthz || exit 1

CMD ["nginx", "-g", "daemon off;"]
