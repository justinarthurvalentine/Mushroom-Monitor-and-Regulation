#!/bin/bash
#
#  upgrade_post.sh - Extra commands to execute for the upgrade process.
#                    Used as a way to provide additional commands to
#                    execute that wouldn't be possible from the running
#                    upgrade script.
#

if [ "$EUID" -ne 0 ]; then
    printf "Please run as root\n";
    exit
fi

INSTALL_DIRECTORY=$( cd "$( dirname "${BASH_SOURCE[0]}" )/../../" && pwd -P )
cd ${INSTALL_DIRECTORY}

ln -sf ${INSTALL_DIRECTORY} /var/www/mycodo

/bin/bash ${INSTALL_DIRECTORY}/mycodo/scripts/upgrade_commands.sh setup-virtualenv

/bin/bash ${INSTALL_DIRECTORY}/mycodo/scripts/upgrade_commands.sh update-apache2

/bin/bash ${INSTALL_DIRECTORY}/mycodo/scripts/upgrade_commands.sh update-packages

/bin/bash ${INSTALL_DIRECTORY}/mycodo/scripts/upgrade_commands.sh update-pip-packages

/bin/bash ${INSTALL_DIRECTORY}/mycodo/scripts/upgrade_commands.sh update-influxdb

printf "\n#### Checking if python modules are up-to-date\n"
pip install --upgrade -r ${INSTALL_DIRECTORY}/install/requirements.txt

# Not needed here since it is done in the flask app, but done again for good measure
/bin/bash ${INSTALL_DIRECTORY}/mycodo/scripts/upgrade_commands.sh update-alembic

printf "\n#### Removing statistics file\n"
rm ${INSTALL_DIRECTORY}/databases/statistics.csv

/bin/bash ${INSTALL_DIRECTORY}/mycodo/scripts/upgrade_commands.sh update-mycodo-startup-script

/bin/bash ${INSTALL_DIRECTORY}/mycodo/scripts/upgrade_commands.sh compile-translations

/bin/bash ${INSTALL_DIRECTORY}/mycodo/scripts/upgrade_commands.sh update-cron

/bin/bash ${INSTALL_DIRECTORY}/mycodo/scripts/upgrade_commands.sh initialize

printf "\n#### Reloading systemctl, Mycodo daemon, and apache2\n"
systemctl daemon-reload
/etc/init.d/apache2 restart
wget -p http://127.0.0.1 -O /dev/null
service mycodo restart
