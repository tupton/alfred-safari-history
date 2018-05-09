#!/usr/bin/env python

"""
Get relevant history from the Safari history database based on the given query and build
Alfred items based on the results.

Usage:
    safari.py PROFILE QUERY
    safari.py (-h | --help)
    safari.py --version

The path to the Safari user profile to get the history database from is given in PROFILE. The query
to search for is given in QUERY. The output is formatted as the Alfred script filter XML output
format.

    PROFILE  The path to the Safari profile whose history database should be searched
    QUERY    The query to search the history database with
"""

from __future__ import print_function

import alfred
import sqlite3
import shutil
import os
import sys
import time
import datetime
from docopt import docopt

__version__ = '0.1.0'

CACHE_EXPIRY = 60
HISTORY_DB = 'History.db'

HISTORY_QUERY = u"""
SELECT history_items.id, title, url
    FROM history_items
        INNER JOIN history_visits
        ON history_visits.history_item = history_items.id
    WHERE url LIKE ? OR title LIKE ?
    GROUP BY url
    ORDER BY visit_time DESC, visit_count DESC
"""

class ErrorItem(alfred.Item):
    def __init__(self, error):
        alfred.Item.__init__(self, {u'valid': u'NO', u'autocomplete': error.message}, error.message, u'Check the workflow log for more information.')

def alfred_error(error):
    alfred.write(alfred.xml([ErrorItem(error)]))

def copy_db(name, profile):
    cache = os.path.join(alfred.work(True), name)
    if os.path.isfile(cache) and time.time() - os.path.getmtime(cache) < CACHE_EXPIRY:
        return cache

    db_file = os.path.join(os.path.expanduser(profile), name)
    try:
        shutil.copy(db_file, cache)
    except:
        raise IOError(u'Unable to copy Safari history database from {}'.format(db_file))

    return cache

def history_db(profile):
    history = copy_db(HISTORY_DB, profile)
    db = sqlite3.connect(history)
    return db

def history_results(db, query):
    q = u'%{}%'.format(query)
    for row in db.execute(HISTORY_QUERY, (q, q,)):
        (uid, title, url) = row
        icon = None

        yield alfred.Item({u'uid': alfred.uid(uid), u'arg': url, u'autocomplete': url}, title or url, url)

if __name__ == '__main__':
    arguments = docopt(__doc__, version='Alfred Safari History {}'.format(__version__))

    profile = unicode(arguments.get('PROFILE'), encoding='utf-8', errors='ignore')
    query = unicode(arguments.get('QUERY'), encoding='utf-8', errors='ignore')

    try:
        db = history_db(profile)
    except IOError, e:
        alfred_error(e)
        sys.exit(-1)

    alfred.write(alfred.xml(history_results(db, query)))
