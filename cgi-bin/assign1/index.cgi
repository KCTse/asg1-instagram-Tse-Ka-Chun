#!/usr/bin/env python

import csci4140
import cgitb
import math
import cgi
import os



################################ CONTROLLER ##############################
cgitb.enable()
form = cgi.FieldStorage()
path = os.environ['HTTP_HOST']
saveDir = '/data'
pics = ''
alert = ""
disables = {'resume': 'disable', 'prev': '', 'next': ''}



resume = csci4140.getCookie('pid')
if resume:
  disables['resume'] = ''

err = csci4140.getCookie('err')
if err:
  alert = csci4140.setAlert('error', err)
  csci4140.deleteCookie('err')



# get picture information from database
db = csci4140.connDB()
img = csci4140.find(db, 'pic', '1', 'created DESC')
link = csci4140.find(db, 'permalink', '1', 'created DESC')
total = int(math.ceil(len(img)/8.0))
if total == 0:
  total = 1


# pagination
cur = 0
curRow = 0
if 'cur' in form:
  cur = int(form['cur'].value)
  if cur < 0 or cur > total-1:
    alert = alert + csci4140.setAlert('error', 'Invalid page index '+str(cur))
    cur = 0

prev = 0
if cur-1 > -1:
  prev = cur-1
else:
  disables['prev'] = 'disable'

pageRange = []
for i in range(8):
  pageRange.append(cur*8+i)

next = 0
if cur+1 <total:
  next = cur+1
else:
  disables['next'] = 'disable'



if len(img) == 0:
  pics = '<p class="no-img">Currently no Images.</p>'
else:
  for row in link:
    if curRow in pageRange:
      img_path = 'http://'+row[0]
      info = row[0].split('/')
      pid = info[len(info)-2]
      file = info[len(info)-1].split('.')
      version = file[0]
      ext = '.'+file[1]

  # for row in img:
  #   if curRow in pageRange:
  #     pid = row[0]
  #     ext = row[5]

      # ver = csci4140.find(db, 'version', 'pid="'+pid+'"')
      # version = ''
      # for r in ver:
      #   version = str(r[1])

      (width, height) = csci4140.getSize(pid, version, ext)

      # img_path = os.path.join(saveDir, pid, version+ext)
      # perm_path = os.path.join(path, img_path)
      pics = pics + '<div class="pic"><a class="box" href="'+img_path+'"><img src="'+img_path+'" class="'
      if width >= height:
        pics = pics + 'full_width'
      else:
        pics = pics + 'full_height'
      pics = pics + '" /></a></div>'
    else:
      pass
    curRow = curRow + 1

################################ CONTROLLER ##############################



################################### VIEW ###################################

pictures = """
  <div class='row'>
    <a class='resume btn %s' href='edit.cgi'>Resume</a>
  </div>

  <div class='row pictures'>
    %s
  </div>

  <div class='row pagination'>
    <a class='btn %s' href='index.cgi?cur=%s'>Previous Page</a>
    <p>Page <b>%s</b> of %s</p>
    <a class='btn %s' href='index.cgi?cur=%s'>Next Page</a>
  </div>
""" % (disables['resume'], pics, disables['prev'], prev, cur+1, total, disables['next'], next)

uploadForm = """
  <form class='row upload' enctype='multipart/form-data' action='upload.cgi' method='POST'>
      <p>Choose an image (.jpg .gif .png):</p>
      <div class='row details'>
        <input class='btn' type='file' name='pic' accept='image/gif, image/jpeg, image/png' />
        <input class='btn success' type='submit' value='Upload' />
      </div>
  </form>
"""

################################### VIEW ###################################



################################### RENDER ################################
db.close()
csci4140.body(alert+pictures+uploadForm)
csci4140.render()
################################### RENDER ################################