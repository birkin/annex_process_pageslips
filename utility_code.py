# -*- coding: utf-8 -*-

import json, os, urllib, urllib2


def checkDirectoryExistence( directory_path ):
  '''
  - Called by: opac_to_las_python_parser_code.controller
  - Purpose: confirm existence of directories before starting processing.
  '''

  import os

  if os.path.exists(directory_path):
    return 'exists'
  else:
    updateLog( message='- directory_path "%s" does not exist' % directory_path, message_importance='high' )
    return 'does_not_exist'

  # end def checkDirectoryExistence()



def checkFileExistence( file_path ):
  '''
  - Called by: opac_to_las_python_parser_code.controller
  - Purpose: to confirm existence of supposedly-copied files in new location
  '''
  try:
    file = open( file_path )
    return 'exists'
  except Exception, e:
    return e

  # end def checkFileExistence()



def convertJosiahLocationCode( code ):
  '''
  - Purpose: input - josiah_location_code; output - las customer_code
  - Called by: utility_code.parseJosiahLocationCode()
  '''

  JOSIAH_LOCATION_TO_LAS_CUSTOMER_CODE_CONVERTER_API_URL_PREFIX = os.environ[u'AN_PR_PA__JOSIAH_LOCATION_TO_LAS_CUSTOMER_CODE_CONVERTER_API_URL_PREFIX']

  full_url = u'%s%s' % ( JOSIAH_LOCATION_TO_LAS_CUSTOMER_CODE_CONVERTER_API_URL_PREFIX, urllib.quote(code) )

  try:
    string_data = urllib.urlopen( full_url ).read()
    json_data = json.loads( string_data )
    result = json_data['result']['returned_las_code']
    return result
  except Exception, e:
    updateLog( message='- in convertJosiahLocationCode(); exception is: %s' % e )
    return 'failure'

  # end def convertJosiahLocationCode()



def convertJosiahPickupAtCode( code ):
  '''
  - Purpose: input - josiah pickup-at code; output - las delivery-stop code
  - Called by: utility_code.parseJosiahPickupAtCode()
  '''

  JOSIAH_PICKUP_AT_TO_LAS_DELIVERY_STOP_CONVERTER_API_URL_PREFIX = os.environ[u'AN_PR_PA__JOSIAH_PICKUP_AT_TO_LAS_DELIVERY_STOP_CONVERTER_API_URL_PREFIX']

  # full_url = settings.JOSIAH_PICKUP_AT_TO_LAS_DELIVERY_STOP_CONVERTER_API_URL_PREFIX + urllib.quote( code )
  full_url = u'%s%s' % ( JOSIAH_PICKUP_AT_TO_LAS_DELIVERY_STOP_CONVERTER_API_URL_PREFIX, urllib.quote(code) )

  try:
    string_data = urllib.urlopen( full_url ).read()
    json_data = json.loads( string_data )
    result = json_data['result']['returned_las_code']
    return result
  except Exception, e:
    updateLog( message='- in convertJosiahPickupAtCode(); exception is: %s' % e )
    return 'failure, exception is: %s' % e

  # end def convertJosiahPickupAtCode()



def determineCount( number_of_parsed_items, pageslip_lines ):
  '''
  - Called by: opac_to_las_python_parser_code.controller
  - Purpose: to verify that the number of items parsed meshes with the count indicator on the pageslip.
  '''

  current_count_estimate_from_lines = 0
  for line in pageslip_lines:
    trimmed_line = line.strip()
    if trimmed_line[0:3] == '38:':
      current_count_estimate_from_lines = int( trimmed_line[3:] )

  if current_count_estimate_from_lines == 0:
    current_count_estimate_from_lines = 1

  if not current_count_estimate_from_lines == number_of_parsed_items:
    updateLog( message='- in utility_code.determineCount(); count discrepancy; number_of_parsed_items is "%s"; 38-method yields "%s"' % ( number_of_parsed_items, current_count_estimate_from_lines ), message_importance='high' )
    return 0
  else:
    return current_count_estimate_from_lines

  # end def determineCount()


def makeItemList( lines ):
  '''
  - Called by: opac_to_las_python_parser_code.controller
  - Purpose: to break an original page-slip file into a list of separate page-slips.
  '''

  # lines = the_reference.readlines()
  # print '- lines is: %s' % str(lines)

  return_list = []
  pageslip_lines = []
  copy_to_pageslip_lines = False
  final_line = 'init'
  for line in lines:
    # print '- line is: %s' % line
    # print '- copy_to_pageslip_lines starts: %s' % copy_to_pageslip_lines
    if line.strip() == 'Brown University':   # normal start of True
      # print '- here01'
      copy_to_pageslip_lines = True
    if line.strip()[0:4] in [ 'Mon ', 'Tue ', 'Wed ', 'Thu ', 'Fri ', 'Sat ', 'Sun ' ]:
      copy_to_pageslip_lines = True
    if line.strip() == '38' or line.strip()[0:3] == '38:':   # normal start of False
      # print '- here02'
      copy_to_pageslip_lines = False

    if line.strip() == 'Brown University' and len(pageslip_lines) > 10:   # means an ending '38...' was missing
      # print '- here03'
      return_list.append( pageslip_lines )
      pageslip_lines = []

    if copy_to_pageslip_lines == True:
      # print '- here04'
      pageslip_lines.append( line )
    if copy_to_pageslip_lines == False and len(pageslip_lines) > 0:
      # print '- here05'
      if '38' in line:   # avoids a last-line append when the '38...' is missing
        # print '- here06'
        pageslip_lines.append( line )
      return_list.append( pageslip_lines )
      pageslip_lines = []

  if len(return_list) == 0 and len(pageslip_lines) > 0:   # handles single-file with no '38...' ending
    return_list.append( pageslip_lines )
    # print '- copy_to_pageslip_lines ends: %s' % copy_to_pageslip_lines
    # print '- pageslip_lines is: %s' % pageslip_lines
    # print '--\n--\n--'
  return return_list

  # end def makeItemList()



# def makeItemList( lines ):
#   '''
#   - Called by: opac_to_las_python_parser_code.controller
#   - Purpose: to break an original page-slip file into a list of separate page-slips.
#   '''
#
#   # lines = the_reference.readlines()
#   # print '- lines is: %s' % str(lines)
#
#   return_list = []
#   pageslip_lines = []
#   copy_to_pageslip_lines = False
#   final_line = 'init'
#   for line in lines:
#     # print '- line is: %s' % line
#     # print '- copy_to_pageslip_lines starts: %s' % copy_to_pageslip_lines
#     if line.strip() == 'Brown University':   # normal start of True
#       # print '- here01'
#       copy_to_pageslip_lines = True
#     if line.strip() == '38' or line.strip()[0:3] == '38:':   # normal start of False
#       # print '- here02'
#       copy_to_pageslip_lines = False
#
#     if line.strip() == 'Brown University' and len(pageslip_lines) > 10:   # means an ending '38...' was missing
#       # print '- here03'
#       return_list.append( pageslip_lines )
#       pageslip_lines = []
#
#     if copy_to_pageslip_lines == True:
#       # print '- here04'
#       pageslip_lines.append( line )
#     if copy_to_pageslip_lines == False and len(pageslip_lines) > 0:
#       # print '- here05'
#       if '38' in line:   # avoids a last-line append when the '38...' is missing
#         # print '- here06'
#         pageslip_lines.append( line )
#       return_list.append( pageslip_lines )
#       pageslip_lines = []
#
#   if len(return_list) == 0 and len(pageslip_lines) > 0:   # handles single-file with no '38...' ending
#     return_list.append( pageslip_lines )
#     # print '- copy_to_pageslip_lines ends: %s' % copy_to_pageslip_lines
#     # print '- pageslip_lines is: %s' % pageslip_lines
#     # print '--\n--\n--'
#   return return_list
#
#   # end def makeItemList()



def parseBookBarcode( single_page_slip ):
  '''
  - Purpose: to extract a book-barcode from a page-slip.
  - Called by: opac_to_las_python_parser_code.controller
  '''

  book_barcode = 'init'
  for line in single_page_slip:
    stripped_line = line.strip()
    if 'BARCODE:' in stripped_line:
      temp_string = stripped_line[8:]   # gets everything after 'BARCODE:'
      temp_string = temp_string.strip()   # removes outside whitespace, leaving barcode possibly containing space-characters
      # print '- temp_string is: %s' % temp_string
      return_val = temp_string.replace( ' ', '' )
      break

  return return_val

  # end def parseBookBarcode()



def parseJosiahLocationCode( single_page_slip ):
  '''
  - Purpose: to extract an las 'customer-code' from a page-slip's josiah 'location-code'.
  - Called by: opac_to_las_python_parser_code.controller
  '''

  return_val = '?'
  for line in single_page_slip:
    stripped_line = line.strip()
    if 'LOCATION:' in stripped_line:
      temp_string = stripped_line[9:]   # gets everything after 'LOCATION:'
      temp_string = temp_string.strip()   # removes outside whitespace, leaving Josiah location
      if not temp_string == '':
        return_val = convertJosiahLocationCode( temp_string )
      break

  return return_val

  # end def parseJosiahLocationCode()



# def parseJosiahLocationCode( single_page_slip ):
#   '''
#   - Purpose: to extract an las 'customer-code' from a page-slip's josiah 'location-code'.
#   - Called by: opac_to_las_python_parser_code.controller
#   '''
#
#   return_val = 'init'
#   for line in single_page_slip:
#     stripped_line = line.strip()
#     if 'LOCATION:' in stripped_line:
#       temp_string = stripped_line[9:]   # gets everything after 'LOCATION:'
#       temp_string = temp_string.strip()   # removes outside whitespace, leaving Josiah location
#       return_val = convertJosiahLocationCode( temp_string )
#       break
#
#   return return_val
#
#   # end def parseJosiahLocationCode()



def parseJosiahPickupAtCode( single_page_slip ):
  '''
  - Purpose: to extract an las 'delivery-stop-code' from a page-slip's josiah 'pickup-at-code'.
  - Called by: opac_to_las_python_parser_code.controller
  '''

  return_val = '?'
  for line in single_page_slip:
    stripped_line = line.strip()
    if 'PICKUP AT:' in stripped_line:
      temp_string = stripped_line[10:]   # gets everything after 'PICKUP AT:'
      temp_string = temp_string.strip()   # removes outside whitespace, leaving Josiah pickup-at code
      if not temp_string == '':
        return_val = convertJosiahPickupAtCode( temp_string )
      break

  return return_val

  # end def parseJosiahPickupAtCode()



# def parseJosiahPickupAtCode( single_page_slip ):
#   '''
#   - Purpose: to extract an las 'delivery-stop-code' from a page-slip's josiah 'pickup-at-code'.
#   - Called by: opac_to_las_python_parser_code.controller
#   '''
#
#   return_val = 'init'
#   for line in single_page_slip:
#     stripped_line = line.strip()
#     if 'PICKUP AT:' in stripped_line:
#       temp_string = stripped_line[10:]   # gets everything after 'PICKUP AT:'
#       temp_string = temp_string.strip()   # removes outside whitespace, leaving Josiah pickup-at code
#       # print '- temp_string is: %s' % temp_string
#       return_val = convertJosiahPickupAtCode( temp_string )
#       break
#
#   return return_val
#
#   # end def parseJosiahPickupAtCode()



def parseNote( pageslip_lines ):
  '''
  - Purpose: to extract a possible note from the lines of a pageslip.
  - Called by: opac_to_las_python_parser_code.controller
  '''

  note = ''
  ready_flag = 'red'
  for line in pageslip_lines:
    # print '- line is: %s and the ready_flag is"%s"' % ( line, ready_flag )
    if 'PICKUP AT:' in line:
      ready_flag = 'yellow'
    elif 'NOTE:' in line and ready_flag == 'yellow':
      ready_flag = 'green'
      temp_string = line.replace( 'NOTE:', '' )
      temp_string = temp_string.strip()
      note = temp_string
    elif ready_flag == 'green' and len( line.strip() ) > 0 and '38' not in line:
      temp_string = line.strip()
      note = note + ' ' + temp_string
    else:
      pass

  cleaned_note = note.replace( '  ', ' ' )
  cleaned_note = cleaned_note.replace( '  ', ' ' )   # one more time just to be thorough
  cleaned_note = cleaned_note.replace( '"', "'" )

  if len( cleaned_note ) < 2:   # note could be blank or just a single space
    return '?'
  else:
    return cleaned_note

  # end def parseNote()



# def parseNote( pageslip_lines ):
#   '''
#   - Purpose: to extract a possible note from the lines of a pageslip.
#   - Called by: opac_to_las_python_parser_code.controller
#   '''
#
#   note = ''
#   ready_flag = 'red'
#   for line in pageslip_lines:
#     print '- line is: %s and the ready_flag is"%s"' % ( line, ready_flag )
#     if 'PICKUP AT:' in line:
#       ready_flag = 'yellow'
#     elif 'NOTE:' in line and ready_flag == 'yellow':
#       ready_flag = 'green'
#       temp_string = line.replace( 'NOTE:', '' )
#       temp_string = temp_string.strip()
#       note = temp_string
#     elif ready_flag == 'green' and '38' in line:   # last line; don't process
#       print '- in 38 line with ready_flag green'
#       break
#     elif ready_flag == 'green' and len(line.strip()) > 0:
#       temp_string = line.strip()
#       note = note + ' ' + temp_string
#     elif len(line.strip()) == 0:   # don't process empty line
#       pass
#     elif ready_flag == 'yellow':   # all conditions that would change it have already been tested
#       pass
#     elif ready_flag == 'red':   # all conditions that would change it have already been tested
#       pass
#     else:
#       print '- oops'
#       print '- oops line is: %s' % line
#       print '- oops len is: %s' % len(line)
#       updateLog( message='in utility_code.parseNote(); unhandled "else"; note so far is: "%s"' % note, message_importance='high' )
#
#   cleaned_note = note.replace( '  ', ' ' )
#   cleaned_note = cleaned_note.replace( '  ', ' ' )   # one more time just to be thorough
#   cleaned_note = cleaned_note.replace( '"', "'" )
#
#   if len( cleaned_note ) < 2:   # note could be blank or just a single space
#     return '?'
#   else:
#     return cleaned_note
#
#   # end def parseNote()



def parsePatronBarcode( pageslip_lines ):
  '''
  - Purpose: to extract the patron name from the lines of a pageslip.
  - Called by: opac_to_las_python_parser_code.controller
  '''

  name = 'init'
  name_line = 'init'
  line_counter = 0
  blank_line_counter = 0

  for line in pageslip_lines:
    if len( line.strip() ) == 0:
      blank_line_counter = blank_line_counter + 1
    else:
      blank_line_counter = 0
    if blank_line_counter == 4:   # means we've had 4 blank lines
      patron_barcode_line = pageslip_lines[ line_counter + 1 ]
      break
    line_counter = line_counter + 1

  patron_barcode = patron_barcode_line.strip()
  spaceless_patron_barcode = patron_barcode.replace( ' ', '' )
  if spaceless_patron_barcode == '':   # patron barcode sometimes doesn't exist
    return '?'
  else:
    return spaceless_patron_barcode

  # end def parsePatronBarcode()



def parsePatronName( pageslip_lines ):
  '''
  - Purpose: to extract the patron name from the lines of a pageslip.
  - Called by: opac_to_las_python_parser_code.controller
  '''

  name = 'init'
  name_line = 'init'
  line_counter = 0
  blank_line_counter = 0

  for line in pageslip_lines:
    if len( line.strip() ) == 0:
      blank_line_counter = blank_line_counter + 1
    else:
      blank_line_counter = 0
    if blank_line_counter == 4:   # means we've had 4 blank lines
      name_line = pageslip_lines[ line_counter + 2 ]
      break
    line_counter = line_counter + 1

  name = name_line.strip()
  return name

  # end def parsePatronName()



def parseRecordNumber( single_page_slip ):
  '''
  - Purpose: to extract a record number from a page-slip.
  - Called by: opac_to_las_python_parser_code.controller
  '''

  record_number = 'init'
  for line in single_page_slip:
    stripped_line = line.strip()
    if 'REC NO:' in stripped_line:
      record_number = stripped_line[-10:]
      break

  return record_number

  # end def parseRecordNumber()



def parseTitle( pageslip_lines ):
  '''
  - Purpose: to extract the item title from the lines of a pageslip.
  - Called by: opac_to_las_python_parser_code.controller
  '''

  counter = 0
  title_line = ''

  for line in pageslip_lines:
    if 'TITLE:' in line:
      title_line = line.replace( 'TITLE:', '' )
      break
    elif 'PUB DATE:' in line:   # means that the title was too long to have a label
      title_line = pageslip_lines[ counter - 2 ]   # two lines above 'PUB DATE:'
      break
    counter = counter + 1

  stripped_title = title_line.strip()
  dequoted_title = stripped_title.replace( '"', "'" )

  return dequoted_title

  # end def parseTitle()



# def parseTitle( pageslip_lines ):
#   '''
#   - Purpose: to extract the item title from the lines of a pageslip.
#   - Called by: opac_to_las_python_parser_code.controller
#   '''
#
#   line_counter = 0
#
#   for line in pageslip_lines:
#     title_line = 'init'
#     if 'AUTHOR:' in line:
#       title_line = pageslip_lines[ line_counter + 1 ]
#       break
#     line_counter = line_counter + 1
#
#   if title_line == 'init':
#       return '?'
#
#   if 'TITLE:' in title_line:
#     title_line_2 = title_line.replace( 'TITLE:', '' )
#     stripped_title = title_line_2.strip()
#   else:
#     stripped_title = title_line.strip()
#
#   dequoted_title = stripped_title.replace( '"', "'" )
#
#   return dequoted_title
#
#   # end def parseTitle()



def postFileData( identifier, file_data, update_type ):
  '''
  - Purpose: to post the file data from the opened-&-read file.
  - Called by: opac_to_las_python_parser_code.controller
  '''

  import urllib, urllib2

  if update_type == 'original_file':
    values = {
      'key': settings.JOSIAH_TO_LAS_LOG_KEY,
      'identifier': identifier,
      'original_file_data': file_data
      }
  else:
    values = {
      'key': settings.JOSIAH_TO_LAS_LOG_KEY,
      'identifier': identifier,
      'parsed_file_data': file_data
      }

  try:
    data = urllib.urlencode(values)
    request = urllib2.Request( settings.JOSIAH_TO_LAS_LOG_URL, data )
    response = urllib2.urlopen(request)
    returned_data = response.read()
    return returned_data
  except Exception, e:
    return '- in postFileData(); exception is: %s' % e

  # end def sampleOriginalDataPostingScript()




def prepareDateTimeStamp( date_stamp ):
  '''
  - Called by: opac_to_las_python_parser_code.controller
  - Purpose: to create a time-stamp string for the files to be archived, like '2005-07-13T13-41-39'
  '''

  iso_datestamp = date_stamp.isoformat()
  custom_datestamp = iso_datestamp[0:19]

  return str( custom_datestamp )

  # end def prepareDateTimeStamp()



def prepareLasDate( date_object=None ):
  '''
  - Called by: opac_to_las_python_parser_code.controller
  - Purpose: to create a date string like 'Wed Jul 01 2005'. In practice, no date will be passed in, but the 'date_object=None' allows for easy testing.
  '''

  from datetime import datetime

  if date_object == None:
    date_object = datetime.now()

  return date_object.strftime( '%a %b %d %Y' )

  # end def prepareLasDate()



def updateLog( message, message_importance='low', identifier='' ):
  '''
  - Called by: opac_to_las_python_parser_code.controller
  - Purpose: update web-accessible log.
  '''

  LOG_ENTRY_MINIMUM_IMPORTANCE_LEVEL = os.environ[u'AN_PR_PA__LOG_ENTRY_MINIMUM_IMPORTANCE_LEVEL']
  LOG_KEY = os.environ[u'AN_PR_PA__LOG_KEY']
  LOG_URL = os.environ[u'AN_PR_PA__LOG_URL']

  update_log_flag = 'init'

  if message_importance == 'high':
    update_log_flag = 'yes'
  elif (message_importance == 'low' and LOG_ENTRY_MINIMUM_IMPORTANCE_LEVEL == 'low' ):
    update_log_flag = 'yes'
  else:
    pass   # there definitely are many other conditions that will get us here -- but the whole point is not to log everything.

  if update_log_flag == 'yes':
    try:
      values = { 'message':message, 'identifier':identifier, 'key':LOG_KEY }
      data = urllib.urlencode(values)
      request = urllib2.Request(LOG_URL, data)
      response = urllib2.urlopen(request)
      returned_data = response.read()
      return returned_data
    except Exception, e:
      pass   # TO_DO: output exception to a log-file
      # raise Exception( '- in utility_code(); exception is: %s' % e )

  # end def updateLog()