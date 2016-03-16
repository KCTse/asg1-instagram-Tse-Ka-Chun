#!/usr/bin/python

import csci4140
import cgi
import cgitb
import os

cgitb.enable()

form = cgi.FieldStorage()

saveDir = '/var/www/html/data' # Full path or relative path

if not os.path.exists(saveDir):
    os.makedirs(saveDir)

if 'pic' not in form:
    csci4140.setCookie('err', 'No file uploaded. Please try again.')
    csci4140.redirect('index.cgi')
elif not form['pic'].filename:
    csci4140.setCookie('err', 'No file selected. Please try again.')
    csci4140.redirect('index.cgi')
else:
    fileitem = form['pic']

    (name, ext) = os.path.splitext(os.path.basename(fileitem.filename))
    if not csci4140.validName(name):
      csci4140.setCookie('err', 'Invalid file name. Please try again.')
      csci4140.redirect('index.cgi')
      
    else:
      pid = csci4140.randomStr()

      picDir = os.path.join(saveDir, pid)
      if not os.path.exists(picDir):
        os.makedirs(picDir)

      savePath = os.path.join(picDir, '0' + ext)
      open(savePath, 'wb').write(fileitem.file.read())

      (err, result) = csci4140.validPic(savePath)
      if err:
        csci4140.deletePic(savePath)
        csci4140.deletePic(picDir, True)
        csci4140.setCookie('err', err)
        csci4140.redirect('index.cgi')
      else:
        db = csci4140.connDB()
        csci4140.insert(db, 'pic', ['pid', 'name', 'width', 'height', 'size', 'ext'], [pid, name, int(result['width']), int(result['height']), result['size'], ext])
        csci4140.insert(db, 'version', ['pid', 'version', 'filter'], [pid, 0, ''])
        db.close()

        csci4140.setCookie('pid', pid)
        csci4140.setCookie('success', 'File uploaded.')
        csci4140.redirect('edit.cgi')

