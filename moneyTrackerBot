FROM python:3.7

WORKDIR "/home/davide/.shared/moneytrakerBot"


COPY requirements.txt ./
RUN pip install -r requirements.txt

COPY . .
CMD ["python", "./bot.py"]