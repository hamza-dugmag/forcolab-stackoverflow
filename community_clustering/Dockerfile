FROM python:3

WORKDIR /usr/src/app
COPY . .

RUN pip install hdbscan --upgrade --user
RUN pip install pandas --upgrade --user
RUN pip install numpy --upgrade --user
RUN pip install matplotlib --upgrade --user
RUN pip install scikit-learn --upgrade --user

CMD python hdbscan_opt_server.py
