FROM python:3.6

ENV PYTHONDONTWRITEBYTECODE=1

COPY requirements.txt ./

RUN pip install -r requirements.txt

COPY . .

ENTRYPOINT ["python", "-u", "/monte_carlo_simulator.py"]