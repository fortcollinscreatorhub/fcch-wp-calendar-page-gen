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

import base64
import requests
import sys

pagenum = sys.argv[1]
filename = sys.argv[2]

with open('wp-app-password.txt', 'rt') as file:
    wp_user = file.readline().strip()
    wp_pass = file.readline().strip()

with open(filename, 'rt') as file:
    content = file.read()

auth_str = wp_user + ':' + wp_pass
auth_bytes = auth_str.encode('utf-8')
auth_b64_bytes = base64.b64encode(auth_bytes)
auth_b64_str = auth_b64_bytes.decode('ascii')
auth_header_b64_str = 'Basic ' + auth_b64_str

response = requests.post(
    'https://www.fortcollinscreatorhub.org/wp-json/wp/v2/pages/' + pagenum,
    headers = {
        'Authorization': auth_header_b64_str,
    },
    data={
        'content': content,
    }
)
if response.status_code != 200:
    print(repr(response))
    sys.exit(1)
