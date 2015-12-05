import calendar
import collections
import datetime
import json
import os.path
import pprint
import sqlite3
import time

import dateutil.parser

from flask import flash, redirect, render_template, \
     request, url_for, g, abort
 
from dashydeebee import app

DATABASE = '/tmp/dashydeebee.db'
TEST_FORMS = os.path.join(os.path.dirname(__file__),'forms.csv')
DEBUG = True

app.config.from_object(__name__)

def connect_db():
    if not os.path.exists(app.config['DATABASE']):
        init_db()
    rv = sqlite3.connect(app.config['DATABASE'])
    rv.row_factory = sqlite3.Row
    return rv

def init_db():
    import sys
    import io
    with io.StringIO() as f:
        from . import forms2sqlite
        forms2sqlite.csv2sqlite(TEST_FORMS, f)
        cur = sqlite3.connect(app.config['DATABASE'])
        cur.cursor()
        cur.executescript(f.getvalue())
        cur.close()

@app.before_request
def before_request():
    g.db = connect_db()

@app.teardown_request
def teardown_request(exception):
    db = getattr(g, 'db', None)
    if db is not None:
        db.close()

def to_epoch(datestr):
    return dateutil.parser.parse(datestr).timestamp()

def find_values(d):
    for group in d:
        for chart in group:
            for datum in chart['datum']:
                yield datum['values']

def post_process_data(date_from, date_to, d):
    for values in find_values(d):
        dates = date_range(date_from, date_to)
        defaults = dict([(date, 0) for date in dates])
        for v in values:
            defaults[v['x']] = v['y']
        del values[:]
        for x in sorted(defaults.keys()):
            values.append({'x': toepoch_in_milliseconds(x),
                           'y': defaults[x]})

@app.route('/indicators/<date_from>/<date_to>/<location>')
def indicators_view(date_from, date_to, location):
    page = 'indicators'
    page_function = pages.get(page)
    if page_function is None:
        abort(404)
    
    d, f = page_function(to_epoch(date_from), to_epoch(date_to), location)
    
    dates = {}
    dates['date_from_label'] = date_from
    dates['date_to_label'] = date_to
    dates['shortcuts'] = [dates_shortcuts(indicators_view.__name__,
                                         date_from = date_from,
                                         date_to = date_to,
                                         location = location),
                          locations_shortcuts(indicators_view.__name__,
                                              date_from = date_from,
                                              date_to = date_to,
                                              location = location)]
    
    return render_template('index.html',
                           data = d,
                           filters = f,
                           dates_urls = dates,
                           pages = pages_urls(date_from = date_from,
                                              date_to = date_to,
                                              location = location))

@app.route('/<page>/<date_from>/<date_to>')
def page_view(page, date_from, date_to):
    page_function = pages.get(page)
    if page_function is None:
        abort(404)
    
    d, f = page_function(to_epoch(date_from), to_epoch(date_to))
    
    dates = {}
    dates['date_from_label'] = date_from
    dates['date_to_label'] = date_to
    dates['shortcuts'] = [dates_shortcuts(page_view.__name__,
                                          page = page,
                                          date_from = date_from,
                                          date_to = date_to)]
    return render_template('index.html',
                           data = d,
                           filters = f,
                           dates_urls = dates,
                           pages = pages_urls(date_from = date_from,
                                              date_to = date_to))

def pages_urls(**kwargs):
    ret = []
    
    kw = kwargs.copy()
    if 'location' in kw:
        del kw['location']
    
    kw['page'] = 'activity'
    ret.append({'label': 'Activity',
                'url': url_for('page_view', **kw)})
    
    kw['page'] = 'locations'
    ret.append({'label': 'Locations',
                'url': url_for('page_view', **kw)})
    
    kw = kwargs.copy()
    if 'location' not in kw:
        kw['location'] = locations_list()[0]
        
    ret.append({'label': 'Indicators',
                'url': url_for('indicators_view', **kw)})
    
    return ret

def dates_shortcuts(endpoint, **kwargs):
    return [month_shortcut(2015, month, endpoint, kwargs) for month in range(7, 13)]

def locations_shortcuts(endpoint, **kwargs):
    ret = []
    for location in locations_list():
        kwargs['location'] = location
        ret.append({'url': url_for(endpoint, **kwargs),
                    'label': location})
    return ret

def location(date_from, date_to, l):
    ret = {}
    ret['id'] = 'chart-location-{}'.format(l.replace(' ', ''))
    ret['title'] = l
    ret['subtitle'] = '{} forms'.format(location_count(date_from, date_to, l))
    
    ret['datum'] = []
    for user in users():
        ret['datum'].append(location_datum(date_from, date_to, l, user))
    
    ret['drawFunction'] = 'multiBarChart'
    return ret

def month_shortcut(year, month, endpoint, kwargs):
    kwargs['date_from'] = datetime.date(year, month, 1)
    kwargs['date_to'] = datetime.date(year,
                                      month,
                                      calendar.monthrange(year, month)[1])
    return {'label': kwargs['date_from'].strftime('%B'),
            'url': url_for(endpoint, **kwargs)}

#def dates_shortcuts(base):
    ## tws = this week start
    ## twe = this week end
    #d = datetime.date.today()
    #dw = datetime.timedelta(7)
    #tws = d - datetime.timedelta(d.weekday())
    #twe = tws + datetime.timedelta(6)
    #lws = tws - dw
    #lwe = twe - dw
    #tms = datetime.date(d.year, d.month, 1)
    #tme = datetime.date(d.year, d.month, calendar.monthrange(tms.year, tms.month)[1])
    #lme = d - datetime.timedelta(d.day)
    #lms = datetime.date(lme.year, lme.month, 1)
    #return [{'label': 'This week', 'url': url_for('activity', date_from = tws, date_to = twe)},
            #{'label': 'Last week', 'url': url_for('activity', date_from = lws, date_to = lwe)},
            #{'label': 'This month', 'url': url_for('activity', date_from = tms, date_to = tme)},
            #{'label': 'Last month', 'url': url_for('activity', date_from = lms, date_to = lme)}]

@app.route('/data/indicators/<date_from>/<date_to>/<location>')
def data_indicators_view(date_from, date_to, location):
    page_function = pages.get('indicators')
    if page_function is None:
        abort(404)
    d, f = page_function(to_epoch(date_from), to_epoch(date_to), location)
    return pprint.pformat(d)

@app.route('/data/<page>/<date_from>/<date_to>')
def data_page_view(page, date_from, date_to):
    page_function = pages.get(page)
    if page_function is None:
        abort(404)
    d, f = page_function(to_epoch(date_from), to_epoch(date_to))
    return pprint.pformat(d)

def data_activity(date_from, date_to):
    ret = []
    #ret.extend(submissions(date_from, date_to))
    ret.extend(users_submissions_multi(date_from, date_to))
    ret.extend(filltime(date_from, date_to))
    ret.extend(transfertime(date_from, date_to))
    post_process_data(date_from, date_to, ret)
    return ret, [users_filter()]

def data_indicators(date_from, date_to, location):
    ret = []
    for indicator in indicators():
        ret.extend(indicator_chart(indicator, date_from, date_to, location))
    #ret.extend(indicator_chart('OPD', date_from, date_to, location))
    #ret.extend(indicator_chart('REF', date_from, date_to, location))
    #ret.extend(indicator_chart('WC', date_from, date_to, location))
    #ret.extend(indicator_chart('AD', date_from, date_to, location))
    post_process_data(date_from, date_to, ret)
    return (ret, [])

def indicators():
    cur = g.db.execute('''SELECT Indicator
                          FROM (SELECT DISTINCT 0 as ordr, Indicator
                                FROM Indicators
                                WHERE Age IS NULL OR Age = ''
                                                        
                                UNION

                                SELECT DISTINCT 1 as ordr, Indicator
                                FROM Indicators
                                WHERE Age <> '')
                          ORDER BY ordr, Indicator;''')
    return [row[0] for row in cur.fetchall()]

def users_filter():
    """
    {'name': 'Team',
     'id': 'filter-Team',
     'choices': [{'id': 'filter-Team-all', 'value': 'all', 'text': 'All teams'},
                 {'id': 'filter-Team-MCA 1', 'value': 'MCA 1', 'text': 'MCA 1'},
                 {'id': 'filter-Team-MCA 2', 'value': 'MCA 2', 'text': 'MCA 2'},
                 {'id': 'filter-Team-MCL 1', 'value': 'MCL 1', 'text': 'MCL 1'},
                 {'id': 'filter-Team-MCL 2', 'value': 'MCL 2', 'text': 'MCL 2'}]}
    """
    name = 'Team'
    text_all = 'All teams'
    mask_id = 'filter-{}'
    
    ret = {}
    ret['name'] = name
    ret['id'] = mask_id.format(name)
    
    mask_choice_id = ret['id'] + '-{}'
    choices = []
    choices.append(choice(mask_choice_id, 'all', 'All teams', True))
    choices.extend([choice(mask_choice_id, user) for user in users()])
    ret['choices'] = choices
    return ret

def choice(mask_id, value, text = None, checked = False):
    if text is None:
        text = value
    return {'id': mask_id.format(value),
            'value': value,
            'text': text,
            'checked': checked}

def transfertime(date_from, date_to):
    ret = {}
    ret['id'] = 'chart-transfertime'
    ret['title'] = 'Transfer time'
    ret['subtitle'] = '{} seconds (average)'.format(transfertime_average(date_from, date_to))
    ret['datum'] = transfertime_datum(date_from, date_to)
    ret['drawFunction'] = 'lineChart'
    return [[ret]]

def transfertime_average(date_from, date_to):
    cur = g.db.execute('''SELECT CAST(ROUND(AVG(TimeReceivedOn - TimeEnd)) AS INTEGER)
                          FROM Forms
                          WHERE Date >= ? AND Date <= ?;''', (date_from, date_to))
    return cur.fetchone()[0]

def transfertime_datum(date_from, date_to):
    cur = g.db.execute('''SELECT Team,
                                 Date,
                                 CAST(ROUND(AVG(TimeReceivedOn - TimeEnd)) AS INTEGER)
                          FROM Forms
                          WHERE Date >= ? AND Date <= ?
                          GROUP BY Team, Date;''', (date_from, date_to))
    d = collections.defaultdict(list)
    for row in cur.fetchall():
        d[row[0]].append({'x': row[1], 'y': row[2]})
    return [{'key': k, 'values': v} for k, v in sorted(d.items())]

def filltime(date_from, date_to):
    ret = {}
    ret['id'] = 'chart-filltime'
    ret['title'] = 'Fill time'
    ret['subtitle'] = '{} seconds (average)'.format(filltime_average(date_from, date_to))
    ret['datum'] = filltime_datum(date_from, date_to)
    ret['drawFunction'] = 'lineChart'
    return [[ret]]

def filltime_average(date_from, date_to):
    cur = g.db.execute('''SELECT CAST(ROUND(AVG(TimeEnd - TimeStart)) AS INTEGER)
                          FROM Forms
                          WHERE Date >= ? AND Date <= ?;''', (date_from, date_to))
    return cur.fetchone()[0]

def filltime_datum(date_from, date_to):
    cur = g.db.execute('''SELECT Team,
                                 Date,
                                 CAST(ROUND(AVG(TimeEnd - TimeStart)) AS INTEGER)
                          FROM Forms
                          WHERE Date >= ? AND Date <= ?
                          GROUP BY Team, Date;''', (date_from, date_to))
    d = collections.defaultdict(list)
    for row in cur.fetchall():
        d[row[0]].append({'x': row[1], 'y': row[2]})
    return [{'key': k, 'values': v} for k, v in sorted(d.items())]

def indicator_chart(indicator, date_from, date_to, location):
    ret = {}
    ret['id'] = 'chart-{}'.format(indicator)
    ret['title'] = indicator
    ret['subtitle'] = '{}'.format(indicator_count(indicator, date_from, date_to, location))
    ret['datum'] = indicator_datum(indicator, date_from, date_to, location)
    ret['drawFunction'] = 'multiBarChart' if len(ret['datum']) > 1 else 'historicalBarChart'
    return [[ret]]

def indicator_count(indicator, date_from, date_to, location):
    cur = g.db.execute('''SELECT SUM(Value)
                          FROM Indicators
                          NATURAL JOIN Forms
                          WHERE Indicator = ? AND Location = ? AND Date >= ? AND Date <= ?
                          ORDER BY Date;''', (indicator, location, date_from, date_to))
    return cur.fetchone()[0]

def indicator_datum(indicator, date_from, date_to, location):
    cur = g.db.execute('''SELECT Date, Age, SUM(Value)
                          FROM Indicators
                          NATURAL JOIN Forms
                          WHERE Indicator = ? AND Location = ? AND Date >= ? AND Date <= ?
                          GROUP BY Date, Age
                          ORDER BY Age, Date;''', (indicator, location, date_from, date_to))
    d = collections.defaultdict(list)
    for row in cur:
        date = row[0]
        age = row[1]
        value = row[2]
        d[age].append({'x': date, 'y': value})
    
    ret = []
    for key, values in d.items():
        if len(key) == 0:
            key = indicator
        ret.append({'key': key,
                    'values': values})
    return ret

def submissions(date_from, date_to):
    ret = {}
    ret['id'] = 'chart-submissions'
    ret['title'] = 'Submissions'
    ret['subtitle'] = '{} forms'.format(submissions_count(date_from, date_to))
    ret['datum'] = submissions_datum(date_from, date_to)
    ret['drawFunction'] = 'historicalBarChart'
    return [[ret]]

def date_range(date_from, date_to):
    cur = date_from
    delta = 60*60*24
    
    while cur <= date_to:
        yield cur
        cur += delta

def users_submissions_multi(date_from, date_to):
    ret = {}
    ret['id'] = 'chart-users-submissions'
    ret['title'] = 'Teams'
    ret['subtitle'] = '<ul>' #
    ret['datum'] = [] #user_submissions_datum(user)
    
    submissions = user_submissions_count(date_from, date_to)
    datum = user_submissions_datum(date_from, date_to)
    for user in users():
        ret['subtitle'] += '<li>{} {} forms</li>'.format(user, submissions.get(user, 0))
        ret['datum'].append({'key': user,
                             'values': datum.get(user, [])})

    #ret['datum'] = [ret['datum'][0]]
    ret['subtitle'] += '</ul>'
    ret['drawFunction'] =  'multiBarChart'
    return [[ret]]

def submissions_datum(date_from, date_to):
    cur = g.db.execute('''SELECT Date, COUNT()
                          FROM Forms
                          WHERE Date >= ? AND DATE <= ?
                          GROUP BY Date;''', (date_from, date_to))
    d = {'key': 'Submissions',
         'values': [{'x': row[0], 'y': row[1]} for row in cur.fetchall()]}
    return [d]

def user_submissions_datum(date_from, date_to):
    cur = g.db.execute('''SELECT Team, Date, COUNT()
                          FROM Forms
                          WHERE Date >= ? AND Date <= ?
                          GROUP BY Team, Date;''', (date_from, date_to))
    d = collections.defaultdict(list)
    for row in cur.fetchall():
        d[row[0]].append({'x': row[1], 'y': row[2]})
    return d

def submissions_count(date_from, date_to):
    cur = g.db.execute('''SELECT COUNT()
                          FROM Forms
                          WHERE DATE >= ? AND DATE <= ?;''', (date_from, date_to))
    return cur.fetchone()[0]

def user_submissions_count(date_from, date_to):
    cur = g.db.execute('''SELECT Team, COUNT()
                          FROM Forms
                          WHERE Date >= ? AND Date <= ?
                          GROUP BY Team;''', (date_from, date_to))
    return dict([(row[0], row[1]) for row in cur.fetchall()])

def data_locations(date_from, date_to):
    charts = [[location(date_from, date_to, l)] for l in locations_list()]
    post_process_data(date_from, date_to, charts)
    return charts, [users_filter()]

def location_count(date_from, date_to, l):
    cur = g.db.execute('select count(FormID) FROM Forms WHERE Date >= ? AND Date <= ? AND Location = ?;', (date_from, date_to, l))
    return cur.fetchone()[0]

def location_datum(date_from, date_to, l, user):
    cur = g.db.execute('''SELECT Date, COUNT()
                          FROM Forms
                          WHERE Date >= ? AND Date <= ? AND Location = ? AND Team = ?
                          GROUP BY Team, Date
                          ORDER BY Team, Date;''', (date_from, date_to, l, user))
    d = {'key': user,
         'values': [{'x': row[0], 'y': row[1]} for row in cur.fetchall()]}
    return d

def alldates():
    cur = g.db.execute('SELECT * FROM Dates;')
    return [row[0] for row in cur.fetchall()]

def locations_list():
    cur = g.db.execute('SELECT DISTINCT Location FROM Forms ORDER BY Location;')
    return [row[0] for row in cur.fetchall()]

def users():
    cur = g.db.execute('SELECT Team FROM Forms GROUP BY Team ORDER BY Team;')
    return [row[0] for row in cur.fetchall()]

def toepoch_in_milliseconds(from_epoch):
    return from_epoch * 1000

pages = {'activity': data_activity,
         'locations': data_locations,
         'indicators': data_indicators}

