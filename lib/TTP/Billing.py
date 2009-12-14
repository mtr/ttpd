#! /usr/bin/python
# -*- coding: utf-8 -*-
# $Id$
"""
Copyright (C) 2009 by Martin Thorsen Ranang
"""
__author__ = ""
__revision__ = "$Rev$"
__version__ = "@VERSION@"

import datetime
import elixir


class Bill(elixir.Entity):
    """A relational-database-mapped entity that is used for logging
    billing information.  These (persistent) entities is also used for
    generating statistics.
    """
    timestamp = elixir.Field(elixir.DateTime,
                             default=datetime.datetime.now,
                             index=True)
    #uuid = Field(Integer) # UUIDs are 128-bit integers.
    #
    # Do not need any UUID, because the inserts are done to a
    # database, and the TIMESTAMP will be created on insertion.
    #
    amount = elixir.Field(elixir.Integer)
    interface = elixir.Field(elixir.Unicode(4))
    host = elixir.Field(elixir.Unicode(24))
    transaction_type = elixir.Field(elixir.Unicode(16))
    description = elixir.Field(elixir.Unicode(16))
    
   
def initialize(db_address='sqlite:///:memory:', logger=None, db_echo=True):
    """Bind the ORM module to a DB and setup and (if necessary) create
    the tables and mappings defined in the default collection.
    """
    elixir.metadata.bind = db_address
    if logger is not None:
        elixir.metadata.bind.logger = logger
        
    elixir.metadata.bind.echo = db_echo # Show all SQL queries.
    
    #print db_address
    elixir.setup_all()
    elixir.create_all()

def log(amount, interface, host, transaction_type, description):
    """Insert a new billing log entry.
    """
    # Create a new Bill instance.  Bill entities have a timestamp
    # attribute that is automatically set to datetime.datetime.now.
    bill = Bill(amount=amount, interface=interface, host=host,
                transaction_type=transaction_type, description=description)

    # Store the new entity in the database.
    elixir.session.commit()
    
def main():
    """Module mainline (for standalone execution)."""
    pass


if __name__ == "__main__":
    main()
