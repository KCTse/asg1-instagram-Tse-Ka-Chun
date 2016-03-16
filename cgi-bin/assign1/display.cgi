#!/usr/bin/env python

import csci4140
import cgitb
import os

cgitb.enable()

link = csci4140.getCookie('link')
if not link:
  csci4140.setCookie('err', 'Missing link. Please upload an image.')
  csci4140.redirect('index.cgi')
else:
  link = 'http://'+link
  csci4140.deleteCookie('link')

  content = """
    <div class='finalized'>
      <p><b>Permalink:</b></p>
      <a href='%s'>%s</a>
    </div>
    <img src='%s' />
    <div class='row finalized'><a class='btn' href='index.cgi'>Go To Index Page</a></div>

  """ % (link, link, link)


  csci4140.body(content)
  csci4140.render()