#! /usr/bin/env python3

from hashlib import sha512
from json import loads
from time import time
from math import ceil
from secrets import randbelow
from urltool import URLtool as urltool

from scrape_common import sleepbreak, stamp, errc

'''
    apihandler.py
    Copyright (C) 2023  Chase Phelps

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
'''

'''
  API Handler for CodeForces API
'''
class APIHandler:
  APIBASEADDR = 'https://codeforces.com/api/'
  def __init__(self, apifile=None, secret=None, key=None):
    self.secret = secret
    self.key = key
    if apifile:
      with open(apifile, 'r') as infile:
        for line in infile.readlines():
          if line.startswith('apikey='):
            self.key = line.split('=')[1].rstrip()
          elif line.startswith('secret='):
            self.secret = line.split('=')[1].rstrip()
    if not self.secret or not self.key:
      raise AttributeError('APIHandler requires secret and key')
    self.errorcount = 0
    # sleep is multiplied by 3 every error
    self.minAPItime = 10
    self.maxAPItime = 486 # 2*(3**5)
    self.APIsleep = self.minAPItime

  def request(self, method, *params):
    err = lambda *s: stamp(errc('API:',*s),
                          errinfo=method+'?'+'&'.join(params))
    self.errorcount += 1
    if sleepbreak(self.APIsleep, self.APIsleep * self.errorcount):
      return None
    url = self.APIBASEADDR + method + '?'
    for param in params:
      url += param + '&'
    url += 'apiKey=' + self.key + '&time=' + str(ceil(time()))
    # six digit number
    rand = str(randbelow(900000) + 100000)
    apiSig = rand + '/' + method + '?'
    for param in sorted(url.split('?')[1].split('&')):
      apiSig += param + '&'
    apiSig = apiSig[:-1] + '#' + self.secret
    url += '&apiSig=' + rand + sha512(apiSig.encode('utf-8')).hexdigest()
    self.APIsleep *= 3
    response = urltool.gethtml(url, allowincomplete=True)
    if urltool.err is not None:
      err(urltool.err)
      urltool.err = None
    if not response:
      return self.request(method, *params)
    try:
      ret = loads(response)
    except:
      try:
        if 'Codeforces is temporarily unavailable' in ret and \
            'Please, return in several minutes' in ret:
          err('Codeforces is temporarily unavailable')
          self.errorcount = 0
          self.APIsleep = self.minAPItime
          if sleepbreak(4*60, 7*60): return None
          return self.request(method, *params)
      except: pass
      err('error parsing json from response')
      return self.request(method, *params)
    if 'status' not in ret or 'result' not in ret:
      err('status or result isn\'t in response')
      return self.request(method, *params)
    if ret['status'] != 'OK':
      err(f'received bad response {ret["status"]}')
      return self.request(method, *params)
    self.APIsleep //= 3
    if self.APIsleep > self.minAPItime:
      self.APIsleep //= 3
    self.errorcount //= 2
    return ret['result']
