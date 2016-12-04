FROM python:3.6

WORKDIR /app

COPY requirements.txt /app

RUN pip install -r requirements.txt

COPY ./ /app/

CMD ["python", "django/manage.py", "runserver", "0.0.0.0:8000"]
