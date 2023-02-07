FROM acompagnon/google_image_downloader:latest

WORKDIR /backend

RUN python3.9 -m pip install -U pip

COPY ./requirements.txt /backend/requirements.txt

RUN python3.9 -m pip install -r /backend/requirements.txt

CMD ["uvicorn", "app.main:app", "--reload", "--host", "0.0.0.0", "--port", "8888"]