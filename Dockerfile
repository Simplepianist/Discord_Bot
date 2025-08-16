FROM python:3.13.7
WORKDIR /app
COPY ./ /app
RUN pip install --no-cache-dir -r requirements.txt

ENV TZ=Europe/Berlin

CMD ["python3.12", "streamer.py"]