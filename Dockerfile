FROM python:3.7

ADD ./ ./
RUN git pull

ADD requirements.txt ./
RUN pip install -r requirements.txt

ADD * ./
CMD ["python", "./bot.py"]