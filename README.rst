Using Sipgate for SMS notifications on a Synology NAS
======================================================

The Synology OS (DSM 3.0) supports sending SMS notifications by posting
to a HTTP url. Sipgate offers a SMS gateway, and an XMLRPC-based API.

This is a small script to bridge the Synology SMS feature to Sipgate by
running a tiny HTTP service locally on your NAS, which accepts the URL
parameters passed to it, and converts them into a Sipgate API call.


Installation
------------

This script is written in Python, which isn't installed by default, so
we install it first::

    $ ipkg install python27

If you don't have ``ipkg`` installed yet, see:
http://forum.synology.com/wiki/index.php/Overview_on_modifying_the_Synology_Server,_bootstrap,_ipkg_etc#How_to_install_ipkg

Let's install the tarball::

    $ cd /opt/local
    $ curl -L http://github.com/miracle2k/synology-sipgate-sms/tarball/master | tar -xzv
    $ mv miracle2k-synology-sipgate-sms-* sipgate-sms

Create the configuration file (no need to change it, normally)::

    $ cd /opt/local/sipgate-sms
    $ cp config.py.template config.py

Enable the daemon to autostart::

    $ cp /opt/local/sipgate-sms/initd-script /opt/etc/init.d/S10sipgate-sms

Start the daemon::

    $ /opt/etc/init.d/S10sipgate-sms start

Now, in the Synology Admin GUI, setup the SMS provider (Control Panel ->
Notification -> SMS -> SMS service provider -> Add). Name the new provider
"Sipgate" and use the following url::

    http://localhost:10288/?user=&password=&to=&text=Hello+World

Press "Next", and assign the proper category for each parameter.

Press the "Send a test SMS message" button to test.


Debugging
---------

You can run ``./server.py`` on the console to get output. Alternatively,
when running as a daemon, a log file will be created in
``/var/log/sipgate-sms.log``. You can modify it's location in the
``config.py`` file.