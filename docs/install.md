Installation Instructionms

1. We assume you have a server with MySQL and a web server (Apache or Nginx) installed and configured. The MySQL database should be called `slp_rtf` and should be accessible to a user called `rtf`.
    - (1a) How to install MySQL: `sudo apt-get update; sudo apt-get install mysql-server` (on Ubuntu). It is recommended you then run `sudo mysql_secure_installation` to harden the server. Answer yes to all the questions except the first, as you already set a root   password.
    - (1b) Creating the database: Log in as root: `mysql -u root -p`, then `CREATE DATABASE slp_rtf`, then `GRANT ALL PRIVILEGES ON slp_rtf.* TO 'rtf' IDENTIFIED BY 'password'`
    - (1c) Configuring the server: Install Apache: `sudo apt-get install apache2`; the official Django site has directions on how to configure it: https://docs.djangoproject.com/en/1.9/howto/deployment/wsgi/modwsgi/. On Ubuntu, the file is at the non-standard location `/etc/apache2/apache2.conf`. Don't forget to install mod_wsgi: `sudo apt-get install libapache2-mod-wsgi`. The `WSGIPythonPath` is the folder where manage.py is located.
2. Grab a copy of our code; you should have been provided with a zip, or Prof. Bloomfield (aaron@virginia.edu) will be able to get you one.
3. Extract the code somewhere on the server, and finish configuring the web server. In the following steps, `[project-root]` refers to the top-level RTF directory (with README.md, docs, and rtf subfolders).
4. Install dependent libraries: `sudo apt-get install libgeos-dev python-dev python-mysqldb`
5. Upgrade pip to the latest version: `sudo pip install --upgrade pip`.
6. Install dependent Python packages: Change to the root directory of the project and run `sudo pip install -r requirements.txt`
7. Run `python manage.py migrate` from `[project-root]/rtf` to prep the database for first use.
8. If you configured the server correctly, the project should now be available at localhost.
9. If you weren't already prompted, from the root of the project, run `python manage.py createsuperuser`. Create a username and password.
10. Set up static files: Open [project-root]/rtf/rtf/settings.py. Find the line `STATIC_URL` and change it to read `STATIC_URL = '/rtf/static'`. Below this, add the line `STATIC_ROOT = [project-root]/rtf/static`.
11. Then, run `python manage.py collectstatic` to allow Django to find the static files. Go back to Apache's config file and add a setting to serve these. Follow the example in the page linked in step 1c (under the heading "Serving files") if you need to - you have to add an Alias for /rtf/static and point it to the correct directory. (We don't have a media folder, so don't worry about that.)
12. Start Celery to allow uploading files to run in the background. This can either be done in the active terminal (described in README.md), through a shell script and cron job (also described in the readme), or as a daemon (Celery docs: http://docs.celeryproject.org/en/latest/tutorials/daemonizing.html)
13. Log in to the project and use the "Create a new user" link to create as many new users as you need.
14. Download the public data you need. 
    -First, go to http://albemarle.org/department.asp?department=gds&relpage=3914#Parcels and download Current Parcels as a Shapefile and Real Estate Information - Parcel Level Data as a XLSX. Both will arrive as zip files.
    -Then, go here: http://charlottesville.org/online-services/maps-and-gis-data/download-gis-data. Under Cadastre, download Parcel Area as an SHP and Parcel Owner Points as an SHP. These will also arrive zip files.
15. Upload the four zip files you downloaded in step 9 and the RTF KMZ file on the "Upload new files" page linked from the project home page. Apache's root folder should be writable by user and group (but not world).
16. The server will run for a little bit while it processes all the uploaded data. When this is done, the server should be up and running like normal.

