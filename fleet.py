from flask import Flask
from flask import send_file, render_template_string, render_template, flash, redirect, url_for, request, make_response, send_from_directory, session
from flask_cors import CORS, cross_origin
import os, sys, json, time, mimetypes, feedparser
from datetime import datetime, timedelta
from html.parser import HTMLParser
import urllib.request
#from flask_socketio import SocketIO
import random, string, tempfile
import sqlite3, re, hashlib
from pytz import timezone
from PIL import Image, ExifTags
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from random import randint
from twilio.rest import Client
from shutil import copyfile
from lxml import etree
from werkzeug.serving import WSGIRequestHandler
from dateutil import parser
from flask_talisman import Talisman
from flask_seasurf import SeaSurf
from pydub import AudioSegment
import cv2
from email import utils
import html
import subprocess
import html2text
import requests
import tensorflow as tf
import tensorflow_hub as hub
import pandas as pd
from socket import timeout
from extruct.opengraph import OpenGraphExtractor
import bcrypt
import csv
import socket
import ssl
from io import BytesIO
from gensim.models import Word2Vec
import dataclasses
import nltk
from nltk.corpus import wordnet
from itertools import chain




appdir = os.getcwd() + '/'

cities = []

tf.get_logger().setLevel('ERROR')

h2t = html2text.HTML2Text()

twilio_id = os.getenv('TWILIO_ID')
twilio_token = os.getenv('TWILIO_TOKEN')
sendgrid_token = os.getenv('SENDGRID_TOKEN')

app = Flask(__name__, static_url_path=appdir)

app.secret_key = os.getenv('APP_SECRET_KEY')

app.permanent_session_lifetime = timedelta(days=31)

#csrf = SeaSurf()
#csrf.init_app(app)


talisman = Talisman(
  app,
  content_security_policy={
    'default-src': [
      '\'self\'',
      '\'unsafe-inline\'',
      '\'unsafe-eval\'',
      'data:',
      'blob:',
      'https://www.youtube.com/embed/90kS-WljHX0',
    ],
    'font-src': [
      '*',
      'data:',
    ],
    'img-src': [
      '*',
      'data:',
    ],
    'media-src': [
      '*',
      'data:',
    ],
  }
)


#socketio = SocketIO(app)
#socketio.init_app(app)


myapp = appdir + os.getenv('FLEET_APP')
mydomain = os.getenv('APP_HOSTNAME')

UPLOAD_FOLDER = appdir + 'myfiles/'
ALLOWED_EXTENSIONS = set(['xml','opml','txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'mov', 'mp4', 'mp3'])
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/file/<filename>')
def sendstatic(filename):
  return send_from_directory('public', filename)

def allowed_file(filename):
  return '.' in filename and \
    filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/post/<postid>')
def post(postid):
  p = get_one_by( 'posts', postid, 'key' )
  if not len(p) > 0:
    return 'OK'
  urlsrc = 'https://' + mydomain + '/p/' + postid
  #ht = '<!DOCTYPE html>' + "\n"
  #ht = ht + '<html>' + "\n"
  #ht = ht + '  <head>' + "\n"
  #ht = ht + '    <title>' + grps[0]['name'] + '</title>'
  ht = ''
  title = re.sub('<[^<]+?>', '', p[0]['title'])
  ht = ht + '    <meta property="og:title" content="' + title + '" />' + "\n"
  ht = ht + '    <meta property="og:type" content="website" />'
  if not p[0]['image'] is None:
    ht = ht + '    <meta property="og:image:type" content="image/jpeg" />'
    imgsrc = 'https://' + mydomain + '/myFile?field=image&name=' + p[0]['image']
    ht = ht + '    <meta property="og:image" content="' + imgsrc + '" />' + "\n"
  ht = ht + '    <meta property="og:url" content="' + urlsrc + '" />'
  ht = ht + '    <meta property="og:description" content="' + title + '" />'
  ht = ht + '  </head>' + "\n"
  #ht = ht + '  <body>Group Page</body>' + "\n"
  #ht = ht + '</html>' + "\n"
  fleet = open(myapp).read()
  fleet = fleet.replace('rp.ly',mydomain)
  fleet = fleet.replace('</head>',ht)
  response = make_response(fleet,200)
  return response

@app.route('/p/<postid>')
def postuser(postid):
  p = get_one_by( 'posts', postid, 'key' )
  if not len(p) > 0:
    return 'OK'
  urlsrc = 'https://' + mydomain + '/p/' + postid
  ht = ''
  title = re.sub('<[^<]+?>', '', p[0]['title'])
  ht = ht + '    <meta property="og:title" content="' + title + '" />' + "\n"
  ht = ht + '    <meta property="og:type" content="website" />'
  if not p[0]['image'] is None:
    ht = ht + '    <meta property="og:image:type" content="image/jpeg" />'
    imgsrc = 'https://' + mydomain + '/myFile?field=image&name=' + p[0]['image']
    ht = ht + '    <meta property="og:image" content="' + imgsrc + '" />' + "\n"
  ht = ht + '    <meta property="og:url" content="' + urlsrc + '" />'
  ht = ht + '    <meta property="og:description" content="' + title + '" />'
  ht = ht + '  </head>' + "\n"
  #ht = ht + '  <body>Group Page</body>' + "\n"
  #ht = ht + '</html>' + "\n"
  fleet = open(myapp).read()
  fleet = fleet.replace('rp.ly',mydomain)
  fleet = fleet.replace('</head>',ht)
  response = make_response(fleet,200)
  return response


@app.route('/grp/<grpid>')
def group(grpid):
  grps = get_one_by( 'groups', grpid, 'key' )
  if not len(grps) > 0:
    return 'OK'
  urlsrc = 'https://' + mydomain + '/g/' + grpid
  #ht = '<!DOCTYPE html>' + "\n"
  #ht = ht + '<html>' + "\n"
  #ht = ht + '  <head>' + "\n"
  #ht = ht + '    <title>' + grps[0]['name'] + '</title>'
  ht = ''
  ht = ht + '    <meta property="og:title" content="' + grps[0]['name'] + '" />' + "\n"
  ht = ht + '    <meta property="og:type" content="website" />'
  if not grps[0]['image'] is None:
    ht = ht + '    <meta property="og:image:type" content="image/jpeg" />'
    imgsrc = 'https://' + mydomain + '/grpFile?field=image&name=' + grps[0]['image']
    ht = ht + '    <meta property="og:image" content="' + imgsrc + '" />' + "\n"
  ht = ht + '    <meta property="og:url" content="' + urlsrc + '" />'
  ht = ht + '    <meta property="og:description" content="' + grps[0]['name'] + '" />'
  ht = ht + '  </head>' + "\n"
  #ht = ht + '  <body>Group Page</body>' + "\n"
  #ht = ht + '</html>' + "\n"
  fleet = open(myapp).read()
  fleet = fleet.replace('rp.ly',mydomain)
  fleet = fleet.replace('</head>',ht)
  response = make_response(fleet,200)
  return response
  #ht = ht + '    <meta name="description" content="' + grps[0]['name'] + '" />'
  #ht = ht + '    <link rel="shortcut icon" href="' + imgsrc + '" type="image/x-icon" />'

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):
  context = ssl._create_unverified_context()
  grps = get_one_by( 'groups', path, 'publicPath' )
  if (len(grps) > 0):
    if path in cities:
      #mod_one( 'groups', {'feeds':json.dumps(result)}, grps[0]['id'] )
      #return 'OK!nice '
      #return 'OK'
      #if path == 'nyssao':
      #  del_one('groups',grps[0]['id'])
      #  print(' DEL CITY')
      #  return 'OK'
      print('CITY')
    if 'key' in grps[0]:
      urlsrc = 'https://' + mydomain + '/grp/' + grps[0]['key']
      return redirect(urlsrc)
    else:
      return 'OK'
  else:
    if path in cities:
      srch = 'https://www.googleapis.com/customsearch/v1?' + urllib.parse.urlencode({
        'key':os.getenv('GOO_KEY'),
        'cx':os.getenv('GOO_CTX'),
        'q':cities[path],
        'searchType':'image'
      })
      data = urllib.request.urlopen(srch).read()
      arr = json.loads(data)
      newfile = ''
      if 'items' in arr:
        for search in arr['items']:
          if any(x in search['link'].lower() for x in ['.jpg','.jpeg']):
            newfile = time.strftime("%d_%m_%Y_%H_%M_%S_" + '.jpg')
            data = False
            try:
              data = urllib.request.urlopen(search['link'], timeout=5, context=context).read()
            except urllib.error.HTTPError as err:
              data = False
            except urllib.error.URLError as err:
              data = False
            except socket.timeout as err:
              data = False
            if data:
              f = open(appdir + 'myfiles/' + newfile,'wb')
              f.write(data)
              f.close()
              break
      regex = re.compile(
        r'^(?:http|ftp)s?://' # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|' #domain...
        r'localhost|' #localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' # ...or ip
        r'(?::\d+)?' # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
      result = []
      possible_feeds = []
      sites = []
      srch = 'https://www.googleapis.com/customsearch/v1?' + urllib.parse.urlencode({
        'key':os.getenv('GOO_KEY'),
        'cx':os.getenv('GOO_CTX'),
        'q':cities[path] + ' news'
      })
      data = urllib.request.urlopen(srch).read()
      arr = json.loads(data)
      if 'items' in arr:
        for search in arr['items']:
          sites.append(search['link'])
          uri = urllib.parse.urlparse(search['link'])
          baseurl = uri.scheme + '://' + uri.netloc
          if baseurl not in sites and not baseurl + '/' in sites:
            sites.append( uri.scheme + '://' + uri.netloc )
      srch = 'https://www.googleapis.com/customsearch/v1?' + urllib.parse.urlencode({
        'key':os.getenv('GOO_KEY'),
        'cx':os.getenv('GOO_CTX'),
        'q':cities[path] + ' news',
        'start': 11
      })
      data = urllib.request.urlopen(srch).read()
      arr = json.loads(data)
      if 'items' in arr:
        for search in arr['items']:
          sites.append(search['link'])
          uri = urllib.parse.urlparse(search['link'])
          baseurl = uri.scheme + '://' + uri.netloc
          if baseurl not in sites and not baseurl + '/' in sites:
            sites.append( uri.scheme + '://' + uri.netloc )
      srch = 'https://www.googleapis.com/customsearch/v1?' + urllib.parse.urlencode({
        'key':os.getenv('GOO_KEY'),
        'cx':os.getenv('GOO_CTX'),
        'q':cities[path] + ' news',
        'start': 21
      })
      data = urllib.request.urlopen(srch).read()
      arr = json.loads(data)
      if 'items' in arr:
        for search in arr['items']:
          sites.append(search['link'])
          uri = urllib.parse.urlparse(search['link'])
          baseurl = uri.scheme + '://' + uri.netloc
          if baseurl not in sites and not baseurl + '/' in sites:
            sites.append( uri.scheme + '://' + uri.netloc )
      for site in sites:
        time.sleep(0.3)
        try:
          data = urllib.request.urlopen(site, timeout=5, context=context).read()
        except urllib.error.HTTPError as err:
          data = False
        except urllib.error.URLError as err:
          data = False
        except socket.timeout as err:
          data = False
        if data:
          tree = etree.HTML(data)
          parsed_url = urllib.parse.urlparse(site)
          base = parsed_url.scheme+"://"+parsed_url.hostname
          for node in tree.findall('.//link'):
            t = node.attrib.get('type')
            if t:
              if "rss" in t or "xml" in t:
                href = node.attrib.get('href')
                if href:
                  if '//' == href[:2]:
                    possible_feeds.append('http:'+href)
                  elif 'http' == href[:4]:
                    possible_feeds.append(href)
                  else:
                    possible_feeds.append(base+href)
          for node in tree.findall('.//a'):
            href = node.attrib.get('href')
            if href:
              if "xml" in href or "rss" in href or "feed" in href:
                if 'http' == href[:4]:
                  possible_feeds.append(href)
                else:
                  possible_feeds.append(base+href)
      for url in possible_feeds:
        if not re.match(regex, url):
          print('NOT URL BRE ' + url)
        else:
          time.sleep(0.3)
          try:
            data = urllib.request.urlopen(url, timeout=5, context=context).read()
          except urllib.error.HTTPError as err:
            continue
          except urllib.error.URLError as err:
            continue
          except socket.timeout as err:
            continue
          f = feedparser.parse(data)
          if len(f.entries) > 0:
            ftitle = 'News Feed'
            if 'feed' in f:
              if 'title' in f['feed']:
                ftitle = f['feed']['title']
            if url not in result:
              result.append(url)
      newrec = {
        'name' : cities[path],
        'image': newfile,
        'maxres': '2000',
        'allowPosts': '0',
        'blockDownloads': '0',
        'user_id' : 0,
        'key' : randomword(8),
        'public': '1',
        'publicImage': newfile,
        'publicName': cities[path],
        'publicBio': '',
        'publicName': cities[path],
        'publicLink': 'https://rp.ly/' + path,
        'publicPath': path,
        'publicGroups': '[]',
        'feeds': json.dumps(result),
        'created' : str( timezone( 'US/Pacific' ).localize( datetime.now() ) )
      }
      print(json.dumps(result))
      gr1 = add_one( 'groups', newrec )
      if gr1 > 0:
        newrec = {
          'title' : '',
          'image' : newfile,
          'sound' : '',
          'video' : '',
          'groups' : json.dumps([int(gr1)]),
          'inreplyto' : '',
          'link':'',
          'user_id' : 0,
          'created' : str( timezone( 'US/Pacific' ).localize( datetime.now() ) )
        }
        rid = add_one( 'posts', newrec )
      grps = get_one_by( 'groups', path, 'publicPath' )
      if (len(grps) > 0):
        urlsrc = 'https://' + mydomain + '/grp/' + grps[0]['key']
        return redirect(urlsrc)
  return 'OK'

@app.route('/g/<grpid>')
def groupuser(grpid):
  grps = get_one_by( 'groups', grpid, 'key' )
  if not len(grps) > 0:
    return 'OK'
  urlsrc = 'https://' + mydomain + '/g/' + grpid
  #ht = '<!DOCTYPE html>' + "\n"
  #ht = ht + '<html>' + "\n"
  #ht = ht + '  <head>' + "\n"
  #ht = ht + '    <title>' + grps[0]['name'] + '</title>'
  ht = ''
  ht = ht + '    <meta property="og:title" content="' + grps[0]['name'] + '" />' + "\n"
  ht = ht + '    <meta property="og:type" content="website" />'
  if not grps[0]['image'] is None:
    ht = ht + '    <meta property="og:image:type" content="image/jpeg" />'
    imgsrc = 'https://' + mydomain + '/grpFile?field=image&name=' + grps[0]['image']
    ht = ht + '    <meta property="og:image" content="' + imgsrc + '" />' + "\n"
  ht = ht + '    <meta property="og:url" content="' + urlsrc + '" />'
  ht = ht + '    <meta property="og:description" content="' + grps[0]['name'] + '" />'
  ht = ht + '  </head>' + "\n"
  #ht = ht + '  <body>Group Page</body>' + "\n"
  #ht = ht + '</html>' + "\n"
  fleet = open(myapp).read()
  fleet = fleet.replace('rp.ly',mydomain)
  fleet = fleet.replace('</head>',ht)
  response = make_response(fleet,200)
  return response
  #ht = ht + '    <meta name="description" content="' + grps[0]['name'] + '" />'
  #ht = ht + '    <link rel="shortcut icon" href="' + imgsrc + '" type="image/x-icon" />'

@app.route('/updater')
def updater():
  item = get_all('posts')[0]
  if not 'video' in item:
    rid = add_one( 'posts', {'video':''} )
    if rid > 0:
      del_one('posts',rid)
    for p in get_all('posts'):
      mod_one( 'posts', {'video':''}, p['id'])
  item = get_all('posts')[0]
  if not 'inreplyto' in item:
    rid = add_one( 'posts', {'inreplyto':''} )
    if rid > 0:
      del_one('posts',rid)
    for p in get_all('posts'):
      mod_one( 'posts', {'inreplyto':''}, p['id'])
  item = get_all('groups')[0]
  if not 'publicBio' in item:
    grobj = {
      'public':'0',
      'publicImage':'',
      'publicName':'',
      'publicBio':'',
      'publicLink':'',
      'publicGroups':'[]'
    }
    rid = add_one( 'groups', grobj )
    if rid > 0:
      del_one('groups',rid)
    for i in get_all('groups'):
      mod_one( 'groups', grobj, i['id'])
  item = get_all('groups')[0]
  if not 'publicPath' in item:
    rid = add_one( 'groups', {'publicPath':''} )
    if rid > 0:
      del_one('groups',rid)
    grobj = {
      'publicPath':''
    }
    for i in get_all('groups'):
      mod_one( 'groups', grobj, i['id'])
  item = get_all('groups')[0]
  if not 'shareLinks' in item:
    rid = add_one( 'groups', {'shareLinks':'0'} )
    if rid > 0:
      del_one('groups',rid)
    grobj = {
      'shareLinks':'0'
    }
    for i in get_all('groups'):
      mod_one( 'groups', grobj, i['id'])
  item = get_all('posts')[0]
  if not 'link' in item:
    rid = add_one( 'posts', {'link':''} )
    if rid > 0:
      del_one('posts',rid)
    grobj = {
      'link':''
    }
    for i in get_all('posts'):
      mod_one( 'posts', grobj, i['id'])
  item = get_all('groups')[0]
  if not 'feeds' in item:
    rid = add_one( 'groups', {'feeds':'[]'} )
    if rid > 0:
      del_one('groups',rid)
    grobj = {
      'feeds':'[]'
    }
    for i in get_all('groups'):
      mod_one( 'groups', grobj, i['id'])
  return 'UPDATED DB'

@app.route('/')
def index():
  global fleet
  if not os.getenv('DEV_IP') is None:
    fleet = open(myapp).read()
    fleet = fleet.replace('rp.ly',mydomain)
    return fleet
  pall = False
  if mydomain == 'photo.gy':
    pall = 'ef6c57 7ed3b2 b9e6d3 f2f2f2'.split()
  #if mydomain == 'audio.gy':
  pall = '445c3c fda77f c9d99e fae8c8'.split()
  if mydomain == 'movie.gd':
    pall = '557571 d49a89 d49a89 f4f4f4'.split()
  if pall:
    fleet = fleet.replace('222831',pall[0])
    fleet = fleet.replace('393e46',pall[1])
    fleet = fleet.replace('32e0c4',pall[2])
    fleet = fleet.replace('ffd3e1',pall[3])
  return fleet
  
def randomword(length):
   letters = string.ascii_lowercase
   return ''.join(random.choice(letters) for i in range(length))

def saveFile(field):
  curr = current_user()
  if not 'id' in curr:
    return ''
  sess = get_one_by('sessions',field + str(curr['id']),'field')
  if len(sess) > 0:
    save = sess[0]['data']
    return save
  return ''

def setSession(field,data):
  curr = current_user()
  if not 'id' in curr:
    return ''
  sess = get_one_by('sessions',field + str(curr['id']),'field')
  if len(sess) > 0:
    mod_one('sessions',{'data':data},sess[0]['id'])
  else:
    add_one('sessions',{'field':field + str(curr['id']),'data':data})
  return True

def clearSession(field):
  curr = current_user()
  if not 'id' in curr:
    return ''
  sess = get_one_by('sessions',field + str(curr['id']),'field')
  if len(sess) > 0:
    mod_one('sessions',{'data':''},sess[0]['id'])
  return True

class FleetParser(HTMLParser):
  def __init__(self):
    HTMLParser.__init__(self)
    self.recording = 0
    self.data = []
  def handle_starttag(self, tag, attributes):
    if tag != 'script':
      return
    if self.recording:
      self.recording += 1
      return
    for name, value in attributes:
      if name == 'id' and value == 'server':
        break
    else:
      return
    self.recording = 1
  def handle_endtag(self, tag):
    if tag == 'script' and self.recording:
      self.recording -= 1
  def handle_data(self, data):
    if self.recording:
      self.data.append(data)

if not 'username' in vars() or 'username' in globals():
  username = ''

def dict_factory(cursor, row):
  d = {}
  for idx, col in enumerate(cursor.description):
    d[col[0]] = row[idx]
  return d

def add_one(resource,obj):
  resource = username + resource
  conn = sqlite3.connect('sqlite.db')
  cur = conn.cursor()
  cur.execute("""SELECT name FROM sqlite_master WHERE type='table' AND name=?;
    """,(resource,))
  if bool(cur.fetchone()) == False:
    sql = "CREATE TABLE " + resource + "(id INTEGER PRIMARY KEY"
    for key, val in obj.items():
      sql = sql + "," + key + " TEXT"
    sql = sql + ")"
    cur.execute(sql)
  sql = "pragma table_info(" + resource + ")"
  result = cur.execute(sql)
  fields = result.fetchall()
  exist = []
  for fie in fields:
    exist.append(fie[1])
  for field in obj.keys():
    if not field in exist:
      sql = "alter table " + resource + " add column " + field + " TEXT"
      cur.execute(sql)
  cols = ', '.join('"{}"'.format(col) for col in obj.keys())
  vals = ', '.join(':{}'.format(col) for col in obj.keys())
  sql = 'INSERT INTO "{0}" ({1}) VALUES ({2})'.format(resource, cols, vals)
  cur = conn.cursor()
  cur.execute(sql, obj)
  conn.commit()
  rid = cur.lastrowid
  conn.close()
  return rid

def get_one_by(resource,value,field):
  resource = username + resource
  conn = sqlite3.connect('sqlite.db')
  conn.row_factory = dict_factory
  cur = conn.cursor()
  vals = []
  sql = "SELECT * FROM " + resource
  sql = sql + " WHERE " + field + " like ?"
  vals.append(value)
  try:
    result = conn.cursor().execute(sql,vals)
  except sqlite3.OperationalError:
    return []
  return result.fetchall()

def get_one(resource,id):
  resource = username + resource
  conn = sqlite3.connect('sqlite.db')
  conn.row_factory = dict_factory
  cur = conn.cursor()
  cur.execute("""SELECT name FROM sqlite_master WHERE type='table' AND name=?;
    """,(resource,))
  if bool(cur.fetchone()) == False:
    return []
  sql = "SELECT * FROM " + resource + " WHERE id = ?"
  try:
    result = conn.cursor().execute(sql,[id])
  except sqlite3.OperationalError:
    return []
  return result.fetchall()

def mod_one(resource,obj,id):
  resource = username + resource
  conn = sqlite3.connect('sqlite.db')
  cur = conn.cursor()
  sql = "UPDATE " + resource + " SET "
  comma = ""
  vals = []
  for key, val in obj.items():
    sql = sql + comma + key + "=?"
    vals.append(val)
    comma = ","
  sql = sql + " WHERE id = ?"
  vals.append(id)
  conn.cursor().execute(sql,vals)
  conn.commit()
  return True

def del_one(resource,id):
  resource = username + resource
  conn = sqlite3.connect('sqlite.db')
  cur = conn.cursor()
  sql = "DELETE FROM " + resource + " WHERE id = ?"
  conn.cursor().execute(sql,[id])
  conn.commit()
  return True

def get_all(resource):
  resource = username + resource
  conn = sqlite3.connect('sqlite.db')
  cur = conn.cursor()
  cur.execute("""SELECT name FROM sqlite_master WHERE type='table' AND name=?;
    """,(resource,))
  if bool(cur.fetchone()) == False:
    return []
  conn.row_factory = dict_factory
  try:
    result = conn.cursor().execute("SELECT * FROM " + resource + ' ORDER BY id DESC')
  except sqlite3.OperationalError:
    return []
  return result.fetchall()

def sendcomet(recips,obj):
  for id in recips:
    recip = get_parent(id)
    print('SEND ' + '/rply/' + recip['code'],file=sys.stderr)
    #socketio.emit('new item', obj, namespace='/rply/' + recip['code'] )
  return True

def get_parent(id):
  id = int(id)
  conn = sqlite3.connect('sqlite.db')
  conn.row_factory = dict_factory
  cur = conn.cursor()
  sql = "SELECT * FROM contacts WHERE id = ?"
  result = conn.cursor().execute(sql,[id])
  rows = result.fetchall()
  if len(rows) > 0:
    if len(rows[0]['email']) > 0:
      items = get_one_by( 'contacts', rows[0]['email'], 'email' )
      if len(items) > 0:
        for con in items:
          if con['user_id'] is None:
            return con
    if len(rows[0]['phone']) > 0:
      items = get_one_by( 'contacts', rows[0]['phone'], 'phone' )
      if len(items) > 0:
        for con in items:
          if con['user_id'] is None:
            return con
  return rows[0]

def share_my_contact(newrec,grps):
  usr = []
  user = current_user()
  if len(newrec['phone']) > 0:
    loginuser = newrec['phone']
    usr = get_one_by('contacts',loginuser,'phone')
  if len(newrec['email']) > 0:
    loginuser = newrec['email']
    usr = get_one_by('contacts',loginuser.lower(),'email')
  if len(usr) > 0:
    for u in usr:
      if u['user_id'] is None:
        contacts = get_one_by('contacts',u['id'],'user_id')
        exists = False
        existscon = {}
        for con in contacts:
          if len(con['phone']) > 0:
            if user['phone'] == con['phone']:
              exists = True
              existscon = con
          if len(con['email']) > 0:
            if user['email'] == con['email']:
              exists = True
              existscon = con
        name = ''
        if not exists:
          ra = randomword(6)
          copy = current_user()
          copy['user_id'] = u['id']
          copy['groups'] = json.dumps(grps)
          copy['code'] = ra
          del copy['id']
          con = add_one( 'contacts', copy )
          name = copy['name']
        else:
          if len(grps) > 0:
            items = get_one( 'groups', grps[0] )
            user = get_user(existscon['id'])
            groups = json.loads(user['groups'])
            groups.append(items[0]['id'])
            con = mod_one('contacts',{'groups': json.dumps(groups)},existscon['id'])
            name = user['name']
        if len(grps) > 0:
          cont = u
          grpdata = get_one('groups',grps[0])
          if len(cont['phone']) > 0:
            client = Client(twilio_id, twilio_token)
            rl = name + " joined your gallery " + grpdata[0]['name'] + " on " + mydomain
            message = client.messages.create(
              body=rl,
              from_='+1' + os.getenv('TWILIO_FROM'),
              to=cont['phone']
            )
            print('notify JOIN ' + cont['phone'], file=sys.stderr)
          if len(cont['email']) > 0:
            owner = current_user()
            em = cont['email']
            message = Mail(
              from_email=owner['name'] + ' via ' + mydomain + ' <' + os.getenv('SENDGRID_FROM') + '>',
              to_emails=em,
              subject=name + " joined your gallery " + grpdata[0]['name'] + " on " + mydomain,
              html_content='<strong><p>' + name + " joined your gallery " + grpdata[0]['name'] + " on " + mydomain + '</p></strong>')
            sg = SendGridAPIClient(sendgrid_token)
            response = sg.send(message)
            print('notify JOIN ' + em, file=sys.stderr)
  return

def notify_comment(addgrp,name):
  grpdata = get_one('groups',addgrp)
  if 'user_id' in grpdata[0]:
    cont = get_user(grpdata[0]['user_id'])
    if len(cont['phone']) > 0:
      client = Client(twilio_id, twilio_token)
      rl = name + " commented in your gallery " + grpdata[0]['name'] + " on " + mydomain
      message = client.messages.create(
        body=rl,
        from_='+1' + os.getenv('TWILIO_FROM'),
        to=cont['phone']
      )
      print('notify COMMENT ' + cont['phone'], file=sys.stderr)
    if len(cont['email']) > 0:
      owner = current_user()
      em = cont['email']
      message = Mail(
        from_email=owner['name'] + ' via ' + mydomain + ' <' + os.getenv('SENDGRID_FROM') + '>',
        to_emails=em,
        subject=name + " commented in your gallery " + grpdata[0]['name'] + " on " + mydomain,
        html_content='<strong><p>' + name + " commented in your gallery " + grpdata[0]['name'] + " on " + mydomain + '</p></strong>')
      sg = SendGridAPIClient(sendgrid_token)
      response = sg.send(message)
      print('notify COMMENT ' + em, file=sys.stderr)
  return

def notify_sponsor(plan,addgrp,name):
  grpdata = get_one('groups',addgrp)
  plans = {'fans300':'$3/mo','fans50':'$6/yr','firstyear5':'$5/mo'}
  if 'user_id' in grpdata[0]:
    cont = get_user(grpdata[0]['user_id'])
    if len(cont['phone']) > 0:
      client = Client(twilio_id, twilio_token)
      rl = name + " paid for a " + plans[plan] + " subscription to " + grpdata[0]['name'] + " on " + mydomain
      message = client.messages.create(
        body=rl,
        from_='+1' + os.getenv('TWILIO_FROM'),
        to=cont['phone']
      )
      print('notify PAY ' + cont['phone'], file=sys.stderr)
    if len(cont['email']) > 0:
      owner = current_user()
      em = cont['email']
      message = Mail(
        from_email=owner['name'] + ' via ' + mydomain + ' <' + os.getenv('SENDGRID_FROM') + '>',
        to_emails=em,
        subject=name + " paid for a " + plans[plan] + " subscription to " + grpdata[0]['name'] + " on " + mydomain,
        html_content='<strong><p>' + name + " bought a " + plan + " subscription on " + mydomain + '</p></strong>')
      sg = SendGridAPIClient(sendgrid_token)
      response = sg.send(message)
      print('notify PAY ' + em, file=sys.stderr)
  return True

def notify_photo(id,grpcode,email,phone):
  num = randint(100, 999)
  cont = get_user(id)
  if len(cont['phone']) > 0 and phone:
    urlsrc = 'https://' + mydomain + '/g/' + grpcode + '#/connect/' + cont['code']
    items = get_one_by( 'groups', grpcode, 'key' )
    client = Client(twilio_id, twilio_token)
    rl = current_user()['name'] + " updated the gallery " + items[0]['name'] + ' ' + urlsrc
    message = client.messages.create(
      body=rl,
      from_='+1' + os.getenv('TWILIO_FROM'),
      to=cont['phone']
    )
    print('notify ' + cont['phone'], file=sys.stderr)
  if len(cont['email']) > 0 and email:
    owner = current_user()
    em = cont['email']
    invitetext = ' updated the gallery '
    items = get_one_by( 'groups', grpcode, 'key' )
    imgsrc = ''
    if not items[0]['image'] is None:
      imgsrc = urllib.parse.quote(items[0]['image'])
    html = '<div style="font-family:courier,monospace;width:90%"><img alt="group image for ' + items[0]['name'] + '" style="height:auto;padding:30px;display:block;margin-left:auto;margin-right:auto;width:50%;padding:10px;" src="https://' + mydomain + '/grpFile?field=image&name='
    html = html + imgsrc + '" /><p style="text-align:center;display:block;padding:10px;">' + owner['name'] + invitetext + items[0]['name'] + '</p><a style="text-align:center;background-color:#32e0c4;display:block;color:black;text-decoration:none;padding:10px;" href="https://' + mydomain + '/g/' + grpcode + '#/connect/' + cont['code'] + '">View Gallery</a></div>'
    regex = re.compile('[^a-zA-Z ]')
    oname = regex.sub('', owner['name'])
    message = Mail(
      from_email=oname + ' via ' + mydomain + ' <' + os.getenv('SENDGRID_FROM') + '>',
      to_emails=em,
      subject="Updated gallery, " + items[0]['name'],
      html_content=html)
    sg = SendGridAPIClient(sendgrid_token)
    response = sg.send(message)
    print('notify ' + em, file=sys.stderr)
  return True

def expired(item):
  if 'expires' in item:
    if not item['expires'] is None:
      from dateutil import tz
      tzinfos = {"-08:00": tz.gettz('US/Pacific')}
      dt = parser.parse(item['expires'], tzinfos=tzinfos)
      if dt < timezone( 'US/Pacific' ).localize( datetime.now() ):
        return True
  return False

def notify_del(id):
  num = randint(100, 999)
  cont = get_user(id)
  if len(cont['phone']) > 0:
    client = Client(twilio_id, twilio_token)
    rl = cont['name'] + " your " + mydomain + " post expired and was deleted "
    message = client.messages.create(
      body=rl,
      from_='+1' + os.getenv('TWILIO_FROM'),
      to=cont['phone']
    )
    print('del notify ' + cont['phone'], file=sys.stderr)
  if len(cont['email']) > 0:
    owner = cont
    em = cont['email']
    message = Mail(
      from_email=owner['name'] + ' via ' + mydomain + ' <' + os.getenv('SENDGRID_FROM') + '>',
      to_emails=em,
      subject=owner['name'] + " your post expired ",
      html_content='<strong><p>your post expired and was deleted</p></strong>')
    sg = SendGridAPIClient(sendgrid_token)
    response = sg.send(message)
    print('del notify ' + em, file=sys.stderr)
  return True

def get_user(id):
  resource = username + 'contacts'
  id = int(id)
  conn = sqlite3.connect('sqlite.db')
  conn.row_factory = dict_factory
  cur = conn.cursor()
  sql = "SELECT * FROM " + resource + " WHERE id = ?"
  try:
    result = conn.cursor().execute(sql,[id])
  except sqlite3.OperationalError:
    return []
  rows = result.fetchall()
  if len(rows) > 0:
    if len(rows[0]['email']) > 0:
      items = get_one_by( 'contacts', rows[0]['email'], 'email' )
      if len(items) > 0:
        for con in items:
          rows[0]['groups'] = json.dumps(json.loads(rows[0]['groups']) + json.loads(con['groups']))
    if len(rows[0]['phone']) > 0:
      items = get_one_by( 'contacts', rows[0]['phone'], 'phone' )
      if len(items) > 0:
        for con in items:
          rows[0]['groups'] = json.dumps(json.loads(rows[0]['groups']) + json.loads(con['groups']))
    rows[0]['groups'] = json.dumps(list(set(json.loads(rows[0]['groups']))))
    return rows[0]
  else:
    return []

def current_user():
  rows = []
  if 'user' in session:
    id = session['user']
    conn = sqlite3.connect('sqlite.db')
    conn.row_factory = dict_factory
    cur = conn.cursor()
    sql = "SELECT * FROM contacts WHERE id = ?"
    result = conn.cursor().execute(sql,[id])
    rows = result.fetchall()
  if len(rows) > 0:
    if len(rows[0]['email']) > 0:
      items = get_one_by( 'contacts', rows[0]['email'], 'email' )
      if len(items) > 0:
        for con in items:
          rows[0]['groups'] = json.dumps(json.loads(rows[0]['groups']) + json.loads(con['groups']))
    if len(rows[0]['phone']) > 0:
      items = get_one_by( 'contacts', rows[0]['phone'], 'phone' )
      if len(items) > 0:
        for con in items:
          rows[0]['groups'] = json.dumps(json.loads(rows[0]['groups']) + json.loads(con['groups']))
    rows[0]['groups'] = json.dumps(list(set(json.loads(rows[0]['groups']))))
    return rows[0]
  return {'user_id':0,'groups':'[0]','code':'xoxo2020'}

def can(action,resource,user,obj=False):
  if user['groups'] is None:
    return False
  groups = json.loads(user['groups'])
  for grp in groups:
    for abb in all_abilities:
      if abb['group_id'] == grp and abb['resource'] == resource:
        if action in abb['actions']:
          if 'conditions' in abb:
            for cond in abb['conditions']:
              if cond[0] in obj:
                if isinstance(obj[cond[0]],str):
                  if isinstance(user[cond[1]],int):
                    if user[cond[1]] == int(obj[cond[0]]):
                      return True
                if isinstance(obj[cond[0]],int):
                  if isinstance(user[cond[1]],int):
                    if user[cond[1]] == obj[cond[0]]:
                      return True
                if not obj[cond[0]] is None:
                  needle = json.loads(obj[cond[0]])
                  if isinstance(needle,list):
                    haystack = json.loads(user[cond[1]])
                    if isinstance(haystack,list):
                      for findit in needle:
                        if findit in haystack:
                          return True
            return False
          else:
            return True
  return False

def randomword(length):
   letters = string.ascii_lowercase
   return ''.join(random.choice(letters) for i in range(length))

@app.route('/csrf_tok',methods=['GET'])
def csrf_tok():
  return session.pop('_csrf_token', '')

@app.route('/clearcodes',methods=['GET'])
def clearcodes():
  dell = ''
  if not request.remote_addr == '24.22.62.218':
    quit()
  item = get_all( 'connectcodes' )
  if len(item) > 0:
    for conn in item:
      del_one( 'connectcodes', conn['id'] )
      dell = dell + str(conn['id']) + '<br>'
  return dell

@app.route('/reportit',methods=['GET'])
def reportit():
  if not request.remote_addr == os.getenv('DEV_IP'):
    print(request.remote_addr)
    quit()
  html = '<table>'
  html = html + '<tr><td>Name</td><td>ID</td><td>Groups</td><td>User ID</td><td>Phone</td><td>Email</td><td>code</td></tr>'
  for gg in get_all('contacts'):
    if not gg['groups'] is None:
      html = html + '<tr><td>' + gg['name'] + '</td><td>' + str(gg['id']) + '</td><td>' + json.dumps(gg['groups']) + '</td><td>' + str(gg['user_id']) + '</td><td>' + gg['phone']+ '</td><td>' + gg['email'] + '</td><td>' + str(gg['code']) + '</td></tr>'
  html = html + '</table>'
  html = html + '<hr><table>'
  html = html + '<tr><td>Name</td><td>ID</td><td>User ID</td></tr>'
  for gg in get_all('groups'):
    html = html + '<tr><td>' + gg['name'] + '</td><td>' + str(gg['id']) + '</td><td>' + str(gg['user_id']) + '</td></tr>'
  html = html + '</table>'
  html = html + '<hr><table>'
  html = html + '<tr><td>Title</td><td>ID</td><td>Groups</td><td>User ID</td></tr>'
  for gg in get_all('posts'):
    html = html + '<tr><td>' + gg['title'] + '</td><td>' + str(gg['id']) + '</td><td>' + json.dumps(gg['groups']) + '</td><td>' + str(gg['user_id']) + '</td></tr>'
  html = html + '</table>'
  return html

def update_abilities():
  global all_abilities, abilities
  all_abilities = abilities
  recs = get_all('groups')
  for item in recs:
    all_abilities.append({
      'group_id':item['id'],
      'resource':'posts',
      'actions':['add']
    })
    all_abilities.append({
      'group_id':item['id'],
      'resource':'posts',
      'actions':['get'],
      'conditions':[['groups','groups']]
    })
    all_abilities.append({
      'group_id':item['id'],
      'resource':'posts',
      'actions':['mod','del'],
      'conditions':[['user_id','id']]
    })

fleet = open(myapp).read()

par = FleetParser()
par.feed(fleet)
par.close()
server = 'global abilities' + "\n" + ''.join(par.data)

server = server.replace('rp.ly',mydomain)
fleet = fleet.replace('rp.ly',mydomain)

if not os.path.exists('sqlite.db'):
  newrec = {
    'name' : 'Group 1',
    'user_id' : 0,
    'created' : str( timezone( 'US/Pacific' ).localize( datetime.now() ) )
  }
  gr1 = add_one( 'groups', newrec )
  newrec = {
    'name' : 'Group 2',
    'user_id' : 0,
    'created' : str( timezone( 'US/Pacific' ).localize( datetime.now() ) )
  }
  gr2 = add_one( 'groups', newrec )
  u = add_one('contacts',{
    'name':'',
    'email':'',
    'phone':'',
    'groups':json.dumps([2]),
    'code':'',
    'user_id':0,
    'created':str(datetime.now())
  })
  add_one('sessions',{'field':'','data':''})
  newrec = {
    'title' : '',
    'image' : '',
    'sound' : '',
    'video' : '',
    'groups' : json.dumps([]),
    'inreplyto' : '',
    'link':'',
    'user_id' : 0,
    'created' : str( timezone( 'US/Pacific' ).localize( datetime.now() ) )
  }
  rid = add_one( 'posts', newrec )
  print('CREATED DB')

abilities = []
all_abilities = []

embedded_text_feature_column = hub.text_embedding_column(
  key="sentence",
  module_spec="https://tfhub.dev/google/nnlm-en-dim128/1")

estimator = tf.estimator.DNNClassifier(
  model_dir=appdir + 'moderation_ai_model',
  hidden_units=[500, 100],
  feature_columns=[embedded_text_feature_column],
  n_classes=2,
  optimizer=tf.train.AdagradOptimizer(learning_rate=0.003))

def moderationCheck(url,crawl,data=''):
  urlkey = ''.join(re.findall('[a-zA-Z0-9_]',url))
  saved = get_one_by( 'cached', urlkey, 'urlkey' )
  if len(saved) > 0:
    return int(saved[0]['result'])
  if 'nytimes' in url:
    return 0
  if not crawl:
    return 1
  h2t.ignore_links = True
  user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.143 Safari/537.36'
  headers = {'User-Agent': user_agent}
  if data == '':
    html = requests.get(url,headers=headers)
    story = h2t.handle(str(html.text))
  else:
    story = h2t.handle(data)
  if "\n" in story:
    story = story.replace("\r", "")
  else:
    story = story.replace("\r", "\n")
  sections = story.split("\n\n")
  story = ''
  for se in sections:
    newlines = se.count("\n")
    if newlines > 0 and se.count(" ") > 10 and len(se.split()) > 10:
      nlratio = newlines / (se.count(" ") + len(se.split()) / 2)
      if nlratio < 0.1 and se.count(".") > 0:
        story = story + se + "\n\n"
  data = {}
  data["sentence"] = []
  data["sentence"].append(story)
  neg_df = pd.DataFrame.from_dict(data)
  test_df = pd.concat([neg_df]).sample(frac=1).reset_index(drop=True)
  predict_test_input_fn = tf.estimator.inputs.pandas_input_fn( test_df, shuffle=False )
  test_predict_generator = estimator.predict( input_fn=predict_test_input_fn )
  output = 0
  for res in test_predict_generator:
    output = int(res['class_ids'][0])
  add_one('cached',{'urlkey':urlkey,'link':url,'story':story,'result':output})
  if not output > 0:
    print(story)
  return output

def getHashedPass( password ):
  return bcrypt.hashpw( password, bcrypt.gensalt() )

def checkPass( password, hashedPassword ):
  return bcrypt.checkpw( password, hashedPassword )

def expandSearch(search_term):
  search_tokens = nltk.word_tokenize(search_term)
  out = []
  for token in search_tokens:
    word = token.lower()
    synonyms = []
    synsets = wordnet.synsets(word)
    if (len(synsets) == 0):
        return []
    for synset in synsets:
        lemma_names = synset.lemma_names()
        for lemma_name in lemma_names:
            lemma_name = lemma_name.lower().replace('_', ' ')
            if (lemma_name != word and lemma_name not in synonyms):
                synonyms.append(lemma_name)
    for o in synonyms:
      out.append(o)
    for o in search_tokens:
      out.append(o)
  return out

exec(server,globals(),{'app':app,'request':request,'abilities':abilities,'estimator':estimator})

update_abilities()

#WSGIRequestHandler.protocol_version = "HTTP/1.1"


# export APP_HOSTNAME=photo.gy
# export FLEET_APP=rp.ly.html
# gunicorn --certfile=fullchain.pem --keyfile=privkey.pem --bind 165.227.57.132:443 --log-file=fleet.log fleet:app
if not sys.argv[0] == 'fleet.py':
  if __name__ == "__main__":
    app.run()

# export APP_HOSTNAME=photo.gy
# export FLEET_APP=rp.ly.html
# python3 fleet.py 165.227.57.132
# python3 fleet.py 165.227.57.132 3000
if sys.argv[0] == 'fleet.py':
  pport = 443
  if len(sys.argv) > 2:
    pport = int(sys.argv[2])
  if sys.argv[0] == 'fleet.py':
    if __name__ == "__main__":
      app.run(host=sys.argv[1],port=pport,ssl_context=('fullchain.pem', 'privkey.pem'))


