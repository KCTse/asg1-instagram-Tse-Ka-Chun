# CSCI4140 Assignment 1 - Instagram
# Tse Ka Chun 1155032312

# csci4140.py
# this file mainly handles common features in the web application
# for example the layout and redirection

import os
import subprocess
import string
import random
import Cookie
import time
import re
from shutil import copyfile
import MySQLdb

header = "Content-Type: text/html"
co = ""
meta = ""
content = ""
cwd = '/var/www/html/data/'




def redirect(location, time=0):
  if time > 0:
    global meta
    meta = "<meta http-equiv='refresh' content='%s; url=%s'>" % (str(time), location)
  else:
    global header
    header = "Status: 302 Found\nLocation: %s" % (location)
    render()




def setCookie(key, val):
  global co
  if co == "":
    if not 'HTTP_COOKIE' in os.environ:
      co = Cookie.SimpleCookie()
    else:
      co = Cookie.SimpleCookie(os.environ['HTTP_COOKIE'])
  co[key] = val
  expireTimestamp = time.time() + 1 * 24 * 60 * 60
  expireTime = time.strftime("%a, %d-%b-%Y %T GMT", time.gmtime(expireTimestamp))
  co[key]['expires'] = expireTime



def getCookie(cookie):
  if not 'HTTP_COOKIE' in os.environ:
    return False
  else:
    _co = Cookie.SimpleCookie(os.environ['HTTP_COOKIE'])
    if cookie in _co:
      return _co[cookie].value
    else:
      return False




def deleteCookie(cookie):
  global co
  if co == "":
    if 'HTTP_COOKIE' in os.environ:
      co = Cookie.SimpleCookie(os.environ['HTTP_COOKIE'])
  if cookie in co:
    co[cookie]['expires'] = 'Thu, 01 Jan 1970 00:00:00 GMT'




def setAlert(type, msg):
  return """
    <div class='box %s'>%s</div>
  """ % (type, type.upper()+': '+msg)




def body(body):
  global content
  content = """ 
  <!DOCTYPE html>
  <html>
    <head>
      <title>CSCI 4140 - Assignment 1</title>
      <meta name='viewport' content='width=device-width, initial-scale=1.0'>
      <link rel="stylesheet" type="text/css" href="./style.css">
      %s
    </head>

    <body>
      <div class='container'>
        <div class='row' id='header'><p><b>CSCI 4140</b> - Assignment 1</p></div>
        <div class='row' id='main'>%s</div>
        <div class='row' id='footer'><p>NAME: Tse Ka Chun<br/>SID: 1155032312</p></div>
      </div>
    </body>
  </html>
  """ % (meta, body)




def render():
  print header
  print co
  print
  print content



def randomStr():
  st = ''.join(random.choice(string.ascii_letters+string.digits) for i in range(10))
  return st+str(time.time()).replace('.', '')



def validPic(img):
  global cwd
  cmd = ['identify', '-format', '%e %m %w %h %b', img] #[0]: extension; [1]: file format; [2]: width; [3]: height; [4]: bytes
  p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=cwd)
  (out, err) = p.communicate()
  if err:
    return 'Invalid image. Please try again.', False
  else:
    out = out.replace('\n', '')
    result = out.split(' ')
    ext = result[0].upper()
    if ext == result[1]:
      return False, { 'width': result[2], 'height': result[3], 'size': result[4] }
    else:
      if ext == 'JPG' and result[1] == 'JPEG':
        return False, { 'width': result[2], 'height': result[3], 'size': result[4] }
      else:
        return 'Incorrect extension. File extension: '+ext+', expected '+result[1], False



def validName(name):
  return re.match('^[\sA-Za-z0-9_-]*$', name)



def deletePic(resource, dir=False):
  global cwd
  cmd = []
  if dir:
    cmd = ['rm', '-r', resource]
  else:
    cmd = ['rm', resource]
  p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=cwd)
  (out, err) = p.communicate()
  if err:
    return err
  else:
    return False



def deleteDir(dir):
  cmd = ['rm', '-r', dir]
  p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd='/var/www/html/')
  (out, err) = p.communicate()
  return out, err



def connDB():
  host = 'db'
  user = 'csci4140'
  pwd = 'opensource'
  db = 'instagram'
  return MySQLdb.connect(host=host, user=user, passwd=pwd, db=db)



def createTable(db):
  cursor = db.cursor()
  query = """
    DROP TABLE IF EXISTS pic;
    DROP TABLE IF EXISTS version; 
    DROP TABLE IF EXISTS permalink; 
    CREATE TABLE IF NOT EXISTS pic ( pid VARCHAR(255), name VARCHAR(255), width INT, height INT, size VARCHAR(255), ext VARCHAR(255), created DATETIME );
    CREATE TABLE IF NOT EXISTS version ( pid VARCHAR(255), version TINYINT(8), filter VARCHAR(255), created DATETIME );
    CREATE TABLE IF NOT EXISTS permalink ( link VARCHAR(255), created DATETIME );"""
  cursor.execute(query)
  #cursor.close()



def insert(db, table, fields, values):
  cursor = db.cursor()
  tableFields = ""
  tableValues = ""

  for i in range(len(fields)):
    tableFields = tableFields + fields[i] + ', '
    if isinstance(values[i], str):
      tableValues = tableValues + '"' + values[i] + '", '
    else:
      tableValues = tableValues + str(values[i]) + ', '
  tableFields = tableFields + 'created'
  tableValues = tableValues + 'NOW()'

  query = """INSERT INTO %s ( %s ) VALUES ( %s )""" % (table, tableFields, tableValues)
  cursor.execute(query)
  db.commit()
  cursor.close()



def find(db, table, condition, order='', one=False):
  cursor = db.cursor()
  query = """SELECT * FROM %s WHERE %s""" % (table, condition)
  if order != '':
    query = query + ' ORDER BY '+order
  cursor.execute(query)
  if one:
    result = cursor.fetchone()
  else:
    result = cursor.fetchall()
  cursor.close()
  return result


def delete(db, table, condition):
  cursor = db.cursor()
  query = """DELETE FROM %s WHERE %s""" % (table, condition)
  cursor.execute(query)
  db.commit()
  cursor.close()


def getSize(pid, version, ext):
  global cwd
  _cwd = os.path.join(cwd, pid)
  curImg = os.path.join(_cwd, version+ext)
  cmd = ['identify', '-format', '%w %h', curImg]
  p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=cwd)
  (out, err) = p.communicate()
  out = out.replace('\n', '').split(' ')
  return int(out[0]), int(out[1])


def copyFile():
  copyfile('/var/www/html/cgi-bin/bwgrad.png', '/var/www/html/data/bwgrad.png')
  copyfile('/var/www/html/cgi-bin/lensflare.png', '/var/www/html/data/lensflare.png')


def filter(pid, ver, ext, type, opt={}):
  global cwd
  _cwd = os.path.join(cwd, pid)
  curImg = str(ver)+ext
  ver = ver+1
  resImg = str(ver)+ext

  if type in ['border', 'lomo', 'flare', 'blackwhite', 'blur', 'annotate_top', 'annotate_bottom']:
    cmd = []

    if type == 'border':
      cmd = ['convert', curImg, '-bordercolor', '#000000', '-border', '10', resImg]

    elif type == 'lomo':
      cmd = ['convert', curImg, '-channel', 'R', '-level', '33%', '-channel', 'G', '-level', '33%', resImg]

    elif type == 'flare':
      cmd = ['identify', '-format', '%w', pid+'/'+curImg]
      p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=cwd)
      (out, err) = p.communicate()
      if err:
        return err, False
      else:
        cmd = ['convert', 'lensflare.png', '-resize', out.replace('\n', ''), pid+'/flare.png']
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=cwd)
        (out, err) = p.communicate()
        if err:
          return err, False
        else:
          cmd = ['composite', '-compose', 'screen', '-gravity', 'northwest', 'flare.png', curImg, resImg]

    elif type == 'blackwhite':
      cmd = ['convert', pid+'/'+curImg, '-type', 'grayscale', pid+'/itm'+ext]
      p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=cwd)
      (out, err) = p.communicate()
      if err:
        return err, False
      else:
        cmd = ['identify', '-format', '%wx%h!', pid+'/'+curImg]
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=cwd)
        (out, err) = p.communicate()
        if err:
          return err, False
        else:
          out = out.replace('\n', '')
          cmd = ['convert', 'bwgrad.png', '-resize', out, pid+'/bwgrad.png']
          p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=cwd)
          (out, err) = p.communicate()
          if err:
            return err, False
          else:
            cmd = ['composite', '-compose', 'softlight', '-gravity', 'center', 'bwgrad.png', 'itm'+ext, resImg]

    elif type == 'blur':
      cmd = ['convert', curImg, '-blur', '0.5x2', resImg]

    elif type == 'annotate_top':
      cmd = ['convert', curImg, '-background', '#ffffff', '-pointsize', opt['font_size'], '-font', opt['font_type'], 'label:'+opt['msg'], '+swap', '-gravity', 'center', '-append', resImg]

    elif type == 'annotate_bottom':
      cmd = ['convert', curImg, '-background', '#ffffff', '-pointsize', opt['font_size'], '-font', opt['font_type'], 'label:'+opt['msg'], '-gravity', 'center', '-append', resImg]

    else:
      return 'Incorrect filter type.', False

    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=_cwd)
    (out, err) = p.communicate()
    if err:
      return err, False
    else:
      if type == 'flare':
        deletePic(pid+'/flare.png')
      if type == 'blackwhite':
        deletePic(pid+'/itm'+ext)
        deletePic(pid+'/bwgrad.png')

      return False, ver

  else:
    return 'Incorrect filter type.', False


