# rtf
Rivanna Trails Foundation project (SLP 2015-2016)

**Team Members:** Kyle Bibler, Chase Deets, Trisha Hajela, Elizabeth Kukla, Shane Matthews, Nate Rathjen, John Reagan, Michael Snider   

[![Circle CI](https://circleci.com/gh/uva-slp/rtf.svg?style=shield&circle-token=c839cfbe2473405779fc33a5d8e4233b49250d78)](https://circleci.com/gh/uva-slp/rtf)

## Local Env Setup

#### Databases
You will need to create a database on your local machine. The easiest way is to have it be the same username and password as is on the server, so that you can use the same database configuration files.

1. Start mysql as root: `mysql -u root -p`, and enter the root password (likely 'password')
2. Create the database: `create database slp_rtf`;
3. Grant permission for your user to use it: `grant all on slp_rtf.* to 'rtf' identified by 'password'`;
Note the .* after the database name (the first 'mst3k')
Use the same username and password as was provided on the server
4. Call that line again, but put a @'localhost' after the userid:`grant all on slp_rtf.* to 'rtf'@'localhost' identified by 'password'`;
5. Exit mysql

#### Settings.py
Settings.py is not tracked by the repo because the server and local dev both have different files and this causes auto_deploy to have merge conflicts and therefore not work. When you set up the repo locally you will need to add the following in a new settings.py file in the `rts/rtf` directory.
```
"""
Django settings for rtf project.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.7/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.7/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'cp1z9%e@3n-f6h7xkq5r2lt@r%odi32%58**dw-!8hz05ha5m$'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

TEMPLATE_DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rtfapp',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'rtf.urls'

WSGI_APPLICATION = 'rtf.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.7/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'slp_rtf',
        'USER': 'rtf',
        'PASSWORD': 'REPLACE WITH GROUP PASSWORD (in Postem on Collab)',
        'HOST': 'localhost',
        'PORT': '3306',
    }
}

# Internationalization
# https://docs.djangoproject.com/en/1.7/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'America/New_York'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.7/howto/static-files/

STATIC_URL = '/static/'


```

## Celery
For background tasks such as the operation to intersect the trail with parcels, we use [Celery](http://celeryproject.org/).

### Starting up a worker instance in an active terminal (not recommended as task can take up to 10 hours)
Navigate to the `~/rtf/rtf` directory

Next, run the following command:
```
celery -A rtf worker -l info
```

The worker instance will now run in the current terminal.

### Running headless worker instances
1. Create `/etc/init.d/celeryd` with this [shell script](https://github.com/celery/celery/blob/3.1/extra/generic-init.d/celeryd) and run `sudo chmod 755 /etc/init.d/celeryd`
2. Create `/etc/default/celeryd` with a [Django configuration](http://docs.celeryproject.org/en/latest/tutorials/daemonizing.html#init-script-celeryd).
    ```
    # Names of nodes to start
    #   most people will only start one node:
    CELERYD_NODES="worker1"
    #   but you can also start multiple and configure settings
    #   for each in CELERYD_OPTS (see `celery multi --help` for examples):
    #CELERYD_NODES="worker1 worker2 worker3"
    #   alternatively, you can specify the number of nodes to start:
    #CELERYD_NODES=10
    
    # Absolute or relative path to the 'celery' command:
    CELERY_BIN="/usr/local/bin/celery"
    #CELERY_BIN="/virtualenvs/def/bin/celery"
    
    # App instance to use
    # comment out this line if you don't use an app
    CELERY_APP="rtf"
    # or fully qualified:
    #CELERY_APP="proj.tasks:app"
    
    # Where to chdir at start.
    CELERYD_CHDIR="/home/student/rtf/rtf/"
    
    # Extra command-line arguments to the worker
    CELERYD_OPTS="-l info"
    
    # %N will be replaced with the first part of the nodename.
    CELERYD_LOG_FILE="/home/student/celery/%N.log"
    CELERYD_PID_FILE="/home/student/celery/%N.pid"
    
    # Workers should run as an unprivileged user.
    #   You need to create this user manually (or you can choose
    #   a user/group combination that already exists, e.g. nobody).
    CELERYD_USER="student"
    CELERYD_GROUP="student"
    
    # If enabled pid and log directories will be created if missing,
    # and owned by the userid/group configured.
    CELERY_CREATE_DIRS=1
    
    export DJANGO_SETTINGS_MODULE="rtf.settings"
    ```
Change the user and group to your trusted non-root user and group (such as `rtf` or `student` on the class VM), replace all absolute paths from `/home/student` to your trusted user's home directory, set the Celery project to `rtf`, and add `export DJANGO_SETTINGS_MODULE="rtf.settings"`. A few other details are changed such as making log files go to the `/home/student/celery` directory and finding the project in `/home/student/rtf/rtf` (or where every the django manage.py is located) that are needed as well. Specifically, you should give the absolute path to the directories as crontab will run this as the root user. Next, run `sudo chmod 640 /etc/default/celeryd`.
3. Create a new bash script by running `sudo touch /etc/init.d/rtf_celeryd_status`
4. Open the file in a text editor and add the following bash script:
    ```
    #!/bin/bash

    sh /etc/init.d/celeryd status

    if [ $? = 1 ]; then
        echo "Starting celery worker instance..."
        sh /etc/init.d/celeryd start
    else
        echo "Already running a worker instance."
    fi
    ```
5. `sudo crontab -e` to add the following cron job to trigger the bash script every 5 minutes for picking up a worker instance if one is unavailable (logging is an optional, but useful step included in this command):
    ```
    */5 * * * * /bin/bash /etc/init.d/rtf_celeryd_status > /var/log/rtf.log 2>&1
    
    ```
6. Now you can check the status via `/var/log/rtf.log`, view crontab logs via `/var/log/syslog`, or manage the worker instance using some of the commands listed below.

#### Managing the worker instance
Check status (such as if an instance is running):
`sudo /etc/init.d/celeryd status`

Start an instance:
`sudo /etc/init.d/celeryd start`

Restart an instance:
`sudo /etc/init.d/celeryd restart`

Stop an instance (although with crontab, a new one will be shortly started):
`sudo /etc/init.d/celeryd stop`

Kill an instance:
`sudo /etc/init.d/celeryd kill`

Edit configurations in `/etc/default/celeryd`


## JS Coverage
We use QUnit, Blanket, and PhantomJS to test the javascript files in the project.

### Running JS Unit Tests
1. `cd rtf/jsunit/`
2. Run the following command:
```
phantomjs run-qunit.js file://`pwd`/qunit.html\?coverage
```
3. If successful, `rm ../../docs/jscoverage.pdf` and then `mv jscoverage.pdf ../../docs/jscoverage.pdf`
4. Open the coverage report in `docs/jscoverage.pdf`

### Making JS Unit Tests
Write QUnit tests in `rtf/jsunit/tests.js`

### Run Tests in Chrome
Blanket references the JS files using XMLHttpRequests, which are considered cross origin requests not typically allowed for standalone files.

However, you can set a flag in chrome by starting it from a command line:
1. `google-chrome --allow-file-access-from-files`
2. Open the qunit page located in `rtf/jsunit/qunit.html`



## Terminal & Productivity Hacks

#### Keeping Time
We have to submit out time on the custom management thing, but if you are looking for an easy way to do the actual tracking I highly recommend [Toggl](https://www.toggl.com/). They have web, desktop, and mobile apps that all sync with your account and it makes it really easy to track time on given activities and put them in categories. It will also send you a weekly summary and make pretty graphs you can view in your web dashboard.

#### Naming tabs and windows
adding these to your `.bash_profile` will allow you to name your terminal tabs and windows which is super helpful for keeping track of where things are when you are doing a bunch of stuff in your terminal at once. 
```
function tabname {
  printf "\e]1;$1\a"
}

function windowname {
  printf "\e]2;$1\a"
}
```
To activate this once you have added it run `$ source .bash_profile`

#### Git branch in terminal prompt
to add your current branch to the terminal prompt when in a git repo (SO HELPFUL when you have different branches it's easy to forget if you are on the one you think you are on) add this to your `.bash_profile`.

```
# Git branch in prompt.
parse_git_branch() {
    git branch 2> /dev/null | sed -e '/^[^*]/d' -e 's/* \(.*\)/ (\1)/'
}
export PS1="\u@\h \W\[\033[32m\]\$(parse_git_branch)\[\033[00m\] $ "
```
run `$ source .bash_profile` to activate. 

### Sublime Text 2
You probably already know about sublime text but if you follow the first part of [this doc](https://gist.github.com/artero/1236170) you can activate the `subl` command in terminal which is awesome because it enables you to easily open an entire project in sublime from the terminal. 

#### Package Control
Sublime is awesome because you can add packages to it. Installing their [package manager](https://packagecontrol.io/) is both easy and worth it.

Once installed I would suggest installing GitGutter. It is a Sublime plugin that marks which lines are different in your current edit from the remote repo of your current branch. It's basically like a real-time `git diff` and really helpful. 


## Slack
our slack channel is slprtf.slack.com
