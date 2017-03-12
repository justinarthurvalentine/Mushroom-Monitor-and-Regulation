#!/usr/bin/python
# -*- coding: utf-8 -*-
#
#  Copyright (C) 2015  Kyle T. Gabriel
#
#  This file is part of Mycodo
#
#  Mycodo is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  Mycodo is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with Mycodo. If not, see <http://www.gnu.org/licenses/>.
#
#  Contact at kylegabriel.com

import sqlalchemy
from flask import current_app

from mycodo.config import USER_ROLES
from mycodo.mycodo_flask.extensions import db
from .conditional import Conditional
from .conditional import ConditionalActions
from .alembic_version import AlembicVersion
from .camera import Camera
from .display_order import DisplayOrder
from .graph import Graph
from .lcd import LCD
from .method import Method
from .method_data import MethodData
from .misc import Misc
from .pid import PID
from .relay import Relay
from .relay_conditional import RelayConditional
from .remote import Remote
from .role import Role
from .sensor import Sensor
from .sensor_conditional import SensorConditional
from .smtp import SMTP
from .timer import Timer
from .user import User


def insert_or_ignore(an_object, a_session):
    """
    Duplicates INSERT OR IGNORE in SQLite.   This mostly illustrative and may not be production ready
    """

    a_session.add(an_object)

    try:
        a_session.commit()
    except sqlalchemy.exc.IntegrityError as e:
        # Ignore duplicate primary key
        # This is the same as the 'INSERT OR IGNORE'
        current_app.logger.debug("An error occurred when committing changes to a database: "
                                 "{err}".format(err=e))
        a_session.rollback()
    except Exception as e:
        current_app.logger.error("Exception in 'insert_or_ignore'' call.  Error: '{err}'".format(err=e))
        # Something else went wrong!!
        a_session.rollback()
        raise


def init_db():
    """
    Binds the database to the specific class tables
    and creates them if needed

    :param db_uri:  URI to the database
    :return: None
    """
    db.create_all()


def drop_db():
    """
    Remove all entries in the database
    :param db_uri: URI to the database
    :return: None
    """
    db.drop_all()


def populate_db(*args, **kwargs):
    """
    Populates the db tables with default values.  This will likely
    be replaced in the future by just setting the default values in the
    db fields
    """
    known_roles = {r.name: r for r in Role.query.all()}
    for role_cfg in USER_ROLES:
        if role_cfg['name'] in known_roles:
            # Update Previous Roles
            previous_record = known_roles[role_cfg['name']]
            for k, v in role_cfg.items():
                if k == 'id':  # skip the primary key
                    continue
                setattr(previous_record, k, v)  # set values from app config
                previous_record.save()
        else:
            # Create new roles
            Role(**role_cfg).save()

    if not AlembicVersion.query.count():
        AlembicVersion().save()
    if not DisplayOrder.query.count():
        DisplayOrder(id=1).save()
    if not Misc.query.count():
        Misc(id=1).save()
    if not SMTP.query.count():
        SMTP(id=1).save()