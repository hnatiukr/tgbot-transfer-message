FROM python:3.8
COPY . /.
RUN pip install -r requirements.txt
EXPOSE 5000
CMD python bot.py