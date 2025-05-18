FROM python:3.12.2
WORKDIR /app
COPY ./ /app
RUN pip install --no-cache-dir -r requirements.txt
EXPOSE 8000

ENV TZ=Europe/Berlin

CMD ["python3.12", "streamer.py"]