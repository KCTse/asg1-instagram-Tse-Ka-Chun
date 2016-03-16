#!/usr/bin/python

import csci4140
import cgi
import cgitb
import os



################################ CONTROLLER ###############################
cgitb.enable()
form = cgi.FieldStorage()
readDir = '/data'


# check if there is picture currently being used
# redirect to index page if not
pid = csci4140.getCookie('pid')
if not pid:
  csci4140.setCookie('err', 'Please upload image before editting.')
  csci4140.redirect('index.cgi')


# get picture information from database
db = csci4140.connDB()
img = csci4140.find(db, 'pic', 'pid="'+pid+'"')
if len(img) == 0:
  csci4140.setCookie('err', 'Cannot find Image.')
  csci4140.deleteCookie('pid')
  csci4140.redirect('index.cgi')

name = ""
width = 0
height = 0
size = ""
ext = ""
for row in img:
  name = row[1]
  width = row[2]
  height = row[3]
  size = row[4]
  ext = row[5]

ver = csci4140.find(db, 'version', 'pid="'+pid+'"', 'version ASC')
version = 0
filter = ''
for row in ver:
  version = row[1]
  filter = row[2]



# set alert if upload succeed
alert = ""
success = csci4140.getCookie('success')
if success:
  alert = csci4140.setAlert('success', success)
  csci4140.deleteCookie('success')



# implement filter
if 'filter' in form:
  type = form['filter'].value
  (err, _version) = csci4140.filter(pid, version, ext, type)
  if err:
    alert = alert + csci4140.setAlert('error', err)
  else:
    version = _version
    csci4140.insert(db, 'version', ['pid', 'version', 'filter'], [pid, version, type])



#implement annotate
if 'position' in form:
  position = form['position'].value
  if position in ['top', 'bottom']:
    type = 'annotate_'+position;

    if 'msg' in form:
      msg = form['msg'].value
      msg = msg.strip()

      if msg != '':
        if 'font_type' in form:
          font_type = form['font_type'].value

          if font_type in ['Times-Roman', 'Courier', 'Helvetica']:
            if 'font_size' in form:
              font_size = form['font_size'].value

              if int(font_size) >= 10 and int(font_size) <= 48:
                (err, _version) = csci4140.filter(pid, version, ext, type, { 'msg': msg, 'font_type': font_type, 'font_size': font_size })
                if err:
                  alert = alert + csci4140.setAlert('error', err)
                else:
                  version = _version
                  csci4140.insert(db, 'version', ['pid', 'version', 'filter'], [pid, version, type])

              else:
                alert = alert + csci4140.setAlert('error', 'Invalid font size.')
            else:
              alert = alert + csci4140.setAlert('error', 'Missing font size.')
          else:
            alert = alert + csci4140.setAlert('error', 'Invalid font type.')
        else:
          alert = alert + csci4140.setAlert('error', 'Missing font type.')
      else:
        alert = alert + csci4140.setAlert('error', 'Empty message.')
    else:
      alert = alert + csci4140.setAlert('error', 'Empty message.')
  else:
    alert = alert + csci4140.setAlert('error', 'Invalid annotate position.')



# implement action
if 'action' in form:
  action = form['action'].value
  if action == 'undo':
    if version > 0:
      condition = """pid='%s' AND version=%s""" % (pid, version)
      csci4140.delete(db, 'version', condition)
      csci4140.deletePic(pid+'/'+str(version)+ext)
      csci4140.redirect('edit.cgi')
    else:
      alert = alert + csci4140.setAlert('error', 'No previous version.')
  elif action == 'discard':
    condition = """pid='%s'""" % (pid)
    csci4140.delete(db, 'pic', condition)
    csci4140.delete(db, 'version', condition)
    csci4140.deletePic(pid+'/', True)
    csci4140.deleteCookie('pid')
    csci4140.redirect('index.cgi')
  elif action == 'finish':
    csci4140.deleteCookie('pid')
    link = os.path.join(os.environ['HTTP_HOST'], 'data', pid, str(version)+ext)
    csci4140.insert(db, 'permalink', ['link'], [link])
    csci4140.setCookie('link', link)
    csci4140.redirect('display.cgi')
  else:
    alert = alert + csci4140.setAlert('error', 'Sorry, action: '+action+' is no supported.')

################################ CONTROLLER ##############################



################################### VIEW ###################################

disableUndo = ''
if version == 0:
  disableUndo = 'disable'

imgFill = ''
if int(width) >= int(height):
  imgFill = 'full_width'
else:
  imgFill = 'full_height'

content = """
  <div class='row' >
    <div class='display'>
      <img class='%s box' src='%s'/>
      <p class='name'>%s</p>
    </div>

    <div class='edit'>
      <div class='filters row'>
        <p>Filters</p>
        <div class='details'>
          <a class='btn' href='edit.cgi?filter=border'>Border</a>
          <a class='btn' href='edit.cgi?filter=lomo'>Lomo</a>
          <a class='btn' href='edit.cgi?filter=flare'>Lens Flare</a>
          <a class='btn' href='edit.cgi?filter=blackwhite'>Black & White</a>
          <a class='btn' href='edit.cgi?filter=blur'>Blur</a>
        </div>
      </div><!-- end of filters -->

      <div class='annotate'>
        <p>Annotate</p>
        <form class='details' action='edit.cgi' method='POST'>
          <input type='text' name='msg' placeholder='Message' required />

          <div class='sub_details row'>
            <p>Font Type</p>
            <select name='font_type'>
              <option value='Times-Roman'>Times</option>
              <option value='Courier'>Courier</option>
              <option value='Helvetica'>Helvetica</option>
            </select>
          </div>

          <div class='sub_details row'>
            <p>Font Size</p>
            <input name='font_size' type='number' min='10' max='48' value='12' />
          </div>

          <button class='btn' name='position' type='submit' value='top' >Annotate Top</input>
          <button class='btn' name='position' type='submit' value='bottom' >Annotate Bottom</input>
        </form>
      </div><!-- end of annotate -->
    </div><!-- end of edit -->
  </div><!-- end of row -->

  <div class='row action'>
    <div class='holder'>&nbsp;</div>

    <div class='details'>
      <div class='sub_details'>

        <div class='one_third'>
          <a class='btn warn %s' href='edit.cgi?action=undo'>Undo</a>
        </div>
        <div class='one_third'>
          <a class='btn error ' href='edit.cgi?action=discard'>Discard</a>
        </div>
        <div class='one_third'>
          <a class='btn success ' href='edit.cgi?action=finish'>Finish</a>
        </div>
      </div>
    </div>

  </div><!-- end of action -->
  
""" % (imgFill, os.path.join(readDir, pid, str(version)+ext), name+ext, disableUndo)

################################### VIEW ###################################



################################### RENDER ################################
db.close()
csci4140.body(alert+content)
csci4140.render()
################################### RENDER ################################