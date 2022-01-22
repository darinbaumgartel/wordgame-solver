FROM python:3.8.3-buster
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt
CMD ["streamlit", "run", "streamlit_wordgame.py"]