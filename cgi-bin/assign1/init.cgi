#!/usr/bin/python

import csci4140
import cgitb
import os

cgitb.enable()

db = csci4140.connDB()
csci4140.createTable(db)
csci4140.deleteDir('data/')

saveDir = '/var/www/html/data' # Full path or relative path
if not os.path.exists(saveDir):
    os.makedirs(saveDir)

csci4140.copyFile()

csci4140.redirect('index.cgi', 10)


content = """
  <div class='init details'>
    <h1>System has been initialized</h1>
    <p>you will be redirect to index page after 10 seconds...</p>
    <a class='btn' href='index.cgi'>Or, go to index page now</a>
  </div>
"""


csci4140.body(content)
csci4140.render()