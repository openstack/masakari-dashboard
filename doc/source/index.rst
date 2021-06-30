===============================
Masakari dashboard
===============================

Horizon plugin for masakari

* Free software: Apache license
* Source: https://opendev.org/openstack/masakari-dashboard
* Bugs: https://bugs.launchpad.net/masakari-dashboard

Features
--------

* TODO

Enabling in DevStack
--------------------

Add this repo as an external repository into your ``local.conf`` file::

    [[local|localrc]]
    enable_plugin masakaridashboard https://github.com/openstack/masakari-dashboard

Manual Installation
-------------------

Begin by cloning the Horizon and Masakari dashboard repositories::

    git clone https://github.com/openstack/horizon
    git clone https://github.com/openstack/masakari-dashboard

Create a virtual environment and install Horizon dependencies::

    cd horizon
    python tools/install_venv.py

Set up your ``local_settings.py`` file::

    cp openstack_dashboard/local/local_settings.py.example openstack_dashboard/local/local_settings.py

Open up the copied ``local_settings.py`` file in your preferred text
editor. You will want to customize several settings:

-  ``OPENSTACK_HOST`` should be configured with the hostname of your
   OpenStack server. Verify that the ``OPENSTACK_KEYSTONE_URL`` and
   ``OPENSTACK_KEYSTONE_DEFAULT_ROLE`` settings are correct for your
   environment. (They should be correct unless you modified your
   OpenStack server to change them.)

Install Masakari dashboard with all dependencies in your virtual environment::

    tools/with_venv.sh pip install -e ../masakari-dashboard/

And enable it in Horizon::

    ln -s ../masakari-dashboard/masakaridashboard/local/enabled/_50_masakaridashboard.py openstack_dashboard/local/enabled
    ln -s ../masakari-dashboard/masakaridashboard/local/local_settings.d/_50_masakari.py openstack_dashboard/local/local_settings.d
    ln -s ../masakari-dashboard/masakaridashboard/conf/masakari_policy.yaml openstack_dashboard/conf

To run horizon with the newly enabled Masakari dashboard plugin run::

    ./run_tests.sh --runserver 0.0.0.0:8080

to have the application start on port 8080 and the horizon dashboard will be
available in your browser at http://localhost:8080/

For Contributors
================

* If you are a new contributor to Masakari Dashboard please refer: :doc:`contributor/contributing`

  .. toctree::
     :hidden:

     contributor/contributing
