#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright (c) 2024-2025 Stephen Warren
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import csv
import json
import os
from pathlib import Path
import subprocess
import sys
import urllib.parse

db_backup_host = 'fcch-web'
db_backup_dir = '/home/u930-v2vbn3xb6dhb/swarren-backups/mysql-www/'
db_backup_file = 'backup.mysql.dbfa8ucrzpcx4d.1'
db_backup_file_gz = db_backup_file + '.gz'
db_backup_path = db_backup_dir + db_backup_file_gz

os.chdir(os.path.dirname(__file__))

if True:
  subprocess.check_call(['rsync', '-e', 'ssh', db_backup_host + ':' + db_backup_dir + db_backup_file_gz, '.'])
  subprocess.check_call(['rm', '-f', db_backup_file])
  subprocess.check_call(['gzip', '-d', db_backup_file_gz])

with open(db_backup_file, 'rt') as file:
  for l in file:
    if 'INSERT INTO `wp_mgcf_bookly_staff` VALUES' in l:
      break
l = l.rstrip()
l = l.rstrip(');')
l = l.strip('INSERT INTO `wp_mgcf_bookly_staff` VALUES (')
csv_data = l.split('),(')

with open('cal_id_to_info.json', 'rt') as file:
  cal_id_to_info = json.loads(file.read())

with open('page_info.json', 'rt') as file:
  page_infos = json.loads(file.read())

def set_default(dict, key, val):
  dict[key] = dict.get(key, val)

csvreader = csv.reader(csv_data, quotechar="'", delimiter=",", escapechar="\\")
for row in csvreader:
  email = row[5]
  google_data_s = row[10]
  if google_data_s != "NULL":
    google_data = json.loads(google_data_s)
    cal_id = google_data['calendar']['id']
    set_default(cal_id_to_info, cal_id, {})
    cal_id_to_info[cal_id]['email'] = email
    set_default(cal_id_to_info[cal_id], 'color', None)
    set_default(cal_id_to_info[cal_id], 'tags', [])

with open('cal_id_to_info.json', 'wt') as file:
    file.write(json.dumps(cal_id_to_info, indent=2))

todo = False
tag_to_cal_ids = {}
for cal_id, info in cal_id_to_info.items():
  if cal_id_to_info[cal_id]['color'] == None:
    print('TODO', cal_id, 'Assign color')
    todo = True
  if cal_id_to_info[cal_id]['tags'] == []:
    print('TODO', cal_id, 'Assign tags')
    todo = True
  for tag in cal_id_to_info[cal_id]['tags']:
    set_default(tag_to_cal_ids, tag, [])
    tag_to_cal_ids[tag].append(cal_id)
if todo:
  sys.exit(1)

iframe_tags = {
  # width setting avoids an extra vertical scroll-bar
  "signage": "<iframe style=\"border: solid 1px #777; position: absolute; left: 0vw; width: 99vw; top: 0vh; height: 99vh;\" frameborder=\"0\" scrolling=\"no\" src=\"",
  "reservations": "<iframe style=\"border: solid 1px #777;\" width=\"800\" height=\"600\" frameborder=\"0\" scrolling=\"no\" src=\"",
}

for page_info in page_infos:
  pagenum = page_info['pagenum']
  fn = 'wp-' + str(pagenum) + '.html'

  style = page_info['style']
  iframe_tag = iframe_tags[style]

  Path(fn).unlink(missing_ok=True)

  with open(fn, 'wt') as file:
    for calendar in page_info['calendars']:
      title = calendar['title']
      title_esc = urllib.parse.quote(title)

      mode = calendar['mode']
      mode_esc = urllib.parse.quote(mode)

      anchor = calendar.get('anchor', None)
      if anchor:
        file.write(f"<a name=\"{anchor}\"></a>\n")

      file.write(iframe_tag)
      file.write("https://calendar.google.com/calendar/embed?")
      file.write("wkst=1&bgcolor=%23ffffff&ctz=America%2FDenver&showCalendars=0&showTz=0&showPrint=0&showTabs=0&")
      file.write(f"mode={mode_esc}&")
      file.write(f"title={title_esc}&")

      tags = calendar['tags']
      for tag in tags:
          cal_ids = tag_to_cal_ids.get(tag, [])
          for cal_id in cal_ids:
            cal_id_esc = urllib.parse.quote(cal_id)
            color = cal_id_to_info[cal_id]['color']
            color_esc = urllib.parse.quote(color)
            file.write(f"src={cal_id_esc}&color={color_esc}&")
      file.write("\"></iframe>\n")

  subprocess.check_call(['./wp-push-page.py', str(pagenum), fn])
