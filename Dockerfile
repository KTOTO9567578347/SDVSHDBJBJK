FROM python:3.11
WORKDIR /system
COPY . /
RUN pip install -r requirements.txt
EXPOSE 3000/tcp
CMD ["python", "main.py"]
