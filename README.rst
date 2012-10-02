Montana
=======

Simple event monitor.

Services on remote systems send event notifications to the Montana server
using a JSON/HTTP protocol. The notification includes service name, status and
hostname. Example backup script invocation::

    $ ~/bin/my-backup-script >> /var/log/backup-script 2>&1
    $ curl -s -d "service=backup" $([ $? -eq 0 ] || echo "-d status=failure") "http://127.0.0.1:5000/events"

The Montana web frontend shows recent events with their status.

Create a configuration file and run the server as follows::

    $ cat <<EOF > settings.py
    DEBUG = False
    API_KEY = 'mysecret'
    EOF
    $ MONTANA_SETTINGS=settings.py ./runserver.py

By default, an in-memory database will be used. Adding `--load-fixtures` loads
some test data.

This is basically a minimal working prototype which I will be working out
further if my agenda allows.
