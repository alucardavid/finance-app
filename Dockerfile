FROM python:3.10

ENV FINANCEENV="prd"

WORKDIR /app

COPY ./requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt

COPY . .

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]