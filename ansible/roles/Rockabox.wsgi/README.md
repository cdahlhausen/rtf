# Rockabox WSGI App Container

[![Join the chat at https://gitter.im/rockabox/Rockabox.wsgi](https://badges.gitter.im/Join%20Chat.svg)](https://gitter.im/rockabox/Rockabox.wsgi?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge)

[![Build Status](https://travis-ci.org/rockabox/Rockabox.wsgi.svg?branch=master)](https://travis-ci.org/rockabox/Rockabox.wsgi)

This is a role for installing a wsgi application container. It makes the
following assumptions about your application:

* It has a [wsgi](http://wsgi.readthedocs.org/en/latest/) file, see below
* You have installed Nginx in another role prior to running this one
* You have a deployment key stored at `wsgi_ssh_key` (see defaults) \*

\* See [this guide](https://help.github.com/articles/generating-ssh-keys/) for help generating ssh keys

## Role variables:

### Required
* `wsgi_project_name` (The name of your project, letters and underscores only)
* `wsgi_wsgi_path` (the relative python path to your application's wsgi file)

### Overidable
Loads! take a look in defaults/main.yml for the full list

Once you have this role on your server, all you need to do is put your
wsgi application at `wsgi_project_name@host.com:current`, and your `wsgi_wsgi_path`
points to your wsgi file...and you're good to go.

To restart your application you can `sudo supervisorctl restart wsgi_project_name`
you can ssh into your box as your application with\* `wsgi_project_name@host.com`

\* Providing you did not set `wsgi_ssh: no`

### Environmental Variables
The following environmental variables are made available to your application
and your ssh session:

```yaml
    PREFIX_APP_PATH (The location of your project)
    PREFIX_APP_NAME (The name of your project)
    PREFIX_RELEASE_DIR (The location of your projects releases)
    PREFIX_VENV (The location of your projects virtual environment)
    PREFIX_LOG_DIR (The location of your projects log directory)
    PREFIX_PID (The location of your projects pid file)
    PREFIX_STATIC_DIR (The location of your static files directory, if you have one)
    PREFIX_MEDIA_DIR (The location of your media files directory, if you have one)
```

Where `PREFIX` is `wsgi_project_name` in upper case, you can overide this
with `wsgi_env_prefix`

Also any databases you have defined in your application will be available as
environmental variables using the following format:

```yaml
    PREFIX_DB_DBID_NAME (The name of your database)
    PREFIX_DB_DBID_USER (The username for your database)
    PREFIX_DB_DBID_PASSWORD (The password for your database)
    PREFIX_DB_DBID_HOST (The host for your database)
    PREFIX_DB_DBID_PORT (The port your database runs on)
```

Where DBID is the upper-cased id of your database, and PREFIX is as above.

Also, any other environmental variables you need your application to have
access to, should be stored in `wsgi_env_vars` like so:

```yaml
    wsgi_env_vars:
        my_secret: 'super-secret-key'
        ...
```

Note: the key names will be automatically upper-cased, to see a full list of
env vars for your app:

    ssh wsgi_project_name@host.com 'printenv | grep `wsgi_env_prefix`'

## Pil/Pillow support

Python imaging libraries (PIL / Pillow) depend on native libraries to support
some image formats or to provide additional functionality, like JPEG or FreeType
libraries. Those dependencies can be automatically installed using `wsgi_enable_python_image: yes`

## Deployment
To deploy to this container, ensure your project is available in

    $PREFIX_APP_RELEASE_DIR/current

And ensure your projects pip dependencies are installed into

    $PREFIX_APP_VENV

Once deployed, restart your application with

    sudo service $PREFIX_APP_NAME restart

Ensure your media is stored in `$PREFIX_APP_MEDIA_DIR`, and your
static files in `$PREFIX_APP_STATIC_DIR`

To see stdout and stderr from your application, see:

    $PREFIX_APP_LOG_DIR/supervisor.log

## Application Cron tasks

You can add cron tasks to your wsgi app using the `wsgi_cron_tasks` variable,
an example is as follows:

    wsgi_cron_tasks:

      - name: Rotate the logs
        user: root
        command: "/usr/sbin/logrotate -f /etc/logrotate.d/log_conf"
        frequency:
            minute: "*/5"
        logfile: "/dev/null"
        environment:
            MY_ENV_VAR: 'MY_VALUE'
            MY_ENV_VAR_2: 'MY_VALUE_2'

Providing additional environment variables by the ``environment`` argument is
optional. Note that all of your environmental variables are made available to
the process running the cron, the command will look something like this:

    /bin/bash -c "source ~/.bash_profile && {{ command }} &>> {{ logfile }}

Note: you can set day, hour, minute or month in frequency, values not set
default to '\*'

You can also specify that your command shouldn't run multiple times at once, in
that case it will be locked on a file using ``flock``. You must ensure that you
provide a ``slug`` to identify your cron task, and it will be used to name
the locking file::

    wsgi_cron_tasks:

      - name: Rotate the logs
        slug: rotate_logs
        lock: yes
        user: root
        command: "/usr/sbin/logrotate -f /etc/logrotate.d/log_conf"
        frequency:
            minute: "*/5"
        logfile: "/dev/null"

## SSl
If you wish to use SSL set the `wsgi_ssl` variable to `yes`, and define the
following paths to your key/cert files

    wsgi_local_ssl_crt_file:  /path/to/signed_cert_plus_intermediates;
    wsgi_local_ssl_key_file:  /path/to/private_key;


To Use [Diffie Hellman Key Exchange](https://en.wikipedia.org/wiki/Diffie%E2%80%93Hellman_key_exchange),
set the following varialbes:

    wsgi_ssl_diffie_hellman: yes
    wsgi_local_ssl_diffie_hellman_pem: /path/to/dhparam.pem

To Use OSCP for speeding up your ssl handshakes, set `wsgi_ssl_ocsp: yes` and
set the following variables:

    wsgi_ssl_ocsp: yes
    wsgi_local_ssl_staple_crt_file: /path/to/root_CA_cert_plus_intermediates

Note: You will need to ensure you have copied the certificates/keys onto the
server in the given locations, before this role is run, e.g::

    ...
    pre_tasks:
      - name: Copy the ssl key file across
        copy: src='./ssl/my.key' dest='/my/destination'
      ...
    ...

Thanks to Mozilla for their [SSL Configuration Generator](https://mozilla.github.io/server-side-tls/ssl-config-generator/)

## Multiple wsgi apps in one play

You can have multiple wsgi apps in one play, by using the `vars_file` var:

    roles:

      - Rockabox.wsgi_app_container
        vars_file: "/path/to/vars/projectA.yml"

      - Rockabox.wsgi_app_container
        vars_file: "../../vars/projectB.yml"

The path needs to be relative to the playbook, or absolute, as described in
the [ansible docs](http://docs.ansible.com/include_vars_module.html#options)

## Future Work

- Release fabric scripts for deployment
