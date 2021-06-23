# Setup PostgreSQL for Datashark

## Procedure

* Start `psql` as `postgres` user on the server:

```bash
sudo su - postgres
psql
```

* When you see `psql` prompt:

```sql
CREATE ROLE datashark WITH PASSWORD '${YOUR_PASSWORD_HERE}' NOSUPERUSER CREATEDB INHERIT LOGIN;
CREATE DATABASE datashark WITH OWNER = datashark ENCODING = 'UTF8' CONNECTION LIMIT = -1;
```

* Edit `/etc/postgresql/12/main/pg_hba.conf` and add:

```bash
host datashark datashark [network] md5
```

* Edit `/etc/postgresql/12/main/postgresql.conf` and change:

```bash
listen_addresses = '*'
```

* Restart `postgresql` instance:

```bash
systemctl restart postgresql@12-main
```

* Test the connection from `datashark-service` machine:

```bash
psql -h [host] -U datashark datashark
```

## Optionally

Setup `pgadmin4` on the server hosting the database :

```bash
# Install the public key for the repository (if not done previously)
sudo curl https://www.pgadmin.org/static/packages_pgadmin_org.pub | sudo apt-key add
# Create the repository configuration file
echo "deb https://ftp.postgresql.org/pub/pgadmin/pgadmin4/apt/$(lsb_release -cs) pgadmin4 main" | sudo tee /etc/apt/sources.list.d/pgadmin4.list
sudo apt update
# Install for web mode only
sudo apt install pgadmin4-web
# Configure the webserver, if you installed pgadmin4-web
sudo /usr/pgadmin4/bin/setup-web.sh
```
