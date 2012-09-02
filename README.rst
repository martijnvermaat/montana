Montana
=======

Simple event monitor.

Services on remote systems send event notifications to the Montana server
using a REST protocol. The notification includes service name, status and
hostname. Example backup script invocation::

    ~/bin/my-backup-script >> /var/log/backup-script 2>&1
    curl -s -d "service=backup" $([ $? -eq 0 ] || echo "-d status=error") "http://127.0.0.1:5000/events"

The Montana web frontend shows recent events with their status.

This is basically a minimal working prototype which I will be working out
further if my agenda allows.
