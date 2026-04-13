FROM rasa/rasa:3.6.20-full

WORKDIR /app

COPY . /app

USER root
RUN pip install --no-cache-dir -r requirements.txt
RUN rasa train --fixed-model-name model
USER 1001

EXPOSE 5005

HEALTHCHECK --interval=30s --timeout=10s CMD curl -f http://localhost:5005/ || exit 1

CMD ["run", "--enable-api", "--cors", "*", "--port", "5005"]
