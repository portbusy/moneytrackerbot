FROM python:3.7

WORKDIR "/home/davide/.shared/moneytrakerBot"


ADD requirements.txt ./
RUN pip install -r requirements.txt

ADD * ./
CMD ["python", "./bot.py"]