FROM bamos/openface

WORKDIR /app

COPY requirements.txt /app

RUN pip install -r requirements.txt
RUN pip install annoy

COPY . /app/

CMD ["python", "django/manage.py", "runserver", "0.0.0.0:8000"]
