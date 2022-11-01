# How do I set up and host my own student orchestra website with MyTaktlausvev?

First of all, to be able to follow this guide and even be able to set up and host your MyTaktlausvev-based website at all, you should have some experience about linux and git. If you don't have this, I highly encourage you to get help form someone who has.

You will need a Linux system with [Docker](https://docs.docker.com/get-docker/), [docker-compose](https://docs.docker.com/compose/install/) and Python 3. For development, I will encourage you to try [WSL](https://learn.microsoft.com/en-us/windows/wsl/install), if you have Windows. For production, read further in the next section.

1. Start by cloning this repository
   ```sh
   $ git clone --recurse-submodules github.com/sigurdo/mytaktlausvev/
   $ cd mytaktlausvev
   ```
2. Edit [`config.toml`](../config.toml) so it suits your student orchestra better.
3. Build your website code from the config.
   ```sh
   $ python3 build_website.py --clean
   $ cd website_build
   ```
4. Build containers and initialize database.
   ```sh
   sh scripts/reset.sh
   ```
5. Run local development server.
   ```sh
   sh scripts/up.sh
   ```

## For production

First of all you need to get a hosted virtual Linux server. It doesn't really have to be virtual, but pretty much every hosting provider runs hypervisors nowadays.

For setting up firewall and some other basic infrastructure on your Linux server, you can use [this guide](https://gitlab.com/taktlause/taktlausveven/-/wikis/Serveroppsett) from Taktlausveven's wiki. It is quite old, so you don't need to care about the "Django with Postgres, Nginx, Gunicorn"-section and everything after it.

1. Clone repository and edit config as described in the previous section.
2. Create an environment file `website_source/deployment/.prod.env` with the following content:
   ```.env
   DEBUG=0
   PRODUCTION=1
   ALLOWED_HOSTS=.localhost 127.0.0.1 [::1]
   CSRF_TRUSTED_ORIGINS=https://localhost
   
   CERTBOT_EMAIL=www@taktlaus.no
   USE_LOCAL_CA=1
   
   POSTGRES_DB=taktlaus_db
   POSTGRES_USER=taktlaus
   POSTGRES_PASSWORD=taktlaus
   ```

   , but configure the variables for your preferances and requirements.
3. Build website code from config as described in the previous section.
4. Start and build production server.
   ```sh
   cd website_build
   docker-compose -f docker-compose.prod.yaml up --build --force-recreate
   ```
