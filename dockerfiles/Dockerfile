FROM ubuntu:20.04

#Installing postgres-12
ENV DEBIAN_FRONTEND=nonintercative
ENV TZ=America/Phoenix
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone
RUN apt-get update && apt-get install -y tzdata postgresql postgresql-contrib libpq-dev

#Installing Python
RUN apt-get update && apt-get install -y python3.9 python3.9-dev gnupg2 wget ca-certificates python3-pip

#Creating user and Database
USER postgres
RUN    /etc/init.d/postgresql start &&\
    psql --command "CREATE USER admin WITH SUPERUSER PASSWORD 'admin';" &&\
    createdb -O admin stock_trade

RUN echo "host all  all    0.0.0.0/0  trust" >> /etc/postgresql/12/main/pg_hba.conf
RUN echo "listen_addresses='*'" >> /etc/postgresql/12/main/postgresql.conf

#Setting up the root directory
WORKDIR /stock_trade
COPY requirements.txt requirements.txt
RUN pip3 install --upgrade pip
RUN pip3 install --user --no-cache-dir --upgrade -r requirements.txt

#Copying all the necessary files to their respective locations
COPY lib lib
COPY static static
COPY templates templates
COPY main.py main.py

#Exposing flask server port for web access
EXPOSE 5000

#Setting the environment PYTHONPATH
ENV PYTHONPATH=/stock_trade

#CMD [ "python3", "main.py"]

# Set the default command to run when starting the container
#CMD ["/usr/lib/postgresql/9.3/bin/postgres", "-D", "/var/lib/postgresql/9.3/main", "-c", "config_file=/etc/postgresql/9.3/main/postgresql.conf"]