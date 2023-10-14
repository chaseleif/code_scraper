#! /usr/bin/env python3

from http.client import IncompleteRead
from gzip import decompress as gdeflate # gzip
from zlib import decompress as zdeflate # deflate
from brotli import decompress as bdeflate # br
from re import sub
from urllib.request import urlopen, Request

class URLtool:
  err = None
  headers={'Accept': 'text/html,application/xhtml+xml,application/xml;' + \
                      'q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
          'Accept-Encoding': 'gzip, deflate, br',
          'Accept-Language': 'en-US,en;q=0.6',
          'Cache-Control': 'no-cache',
          'DNT': '1',
          'Pragma': 'no-cache',
          'SEC-CH-UA': '\"Chromium\";v=\"112\", ' + \
                        '\"Brave\";v=\"112\", ' + \
                        '\"Not:A-Brand\";v=\"99\"',
          'SEC-CH-UA-MOBILE': '?0',
          'SEC-CH-UA-PLATFORM': '\"Linux\"',
          'SEC-FETCH-DEST': 'document',
          'SEC-FETCH-MODE': 'navigate',
          'SEC-FETCH-SITE': 'none',
          'SEC-FETCH-USER': '?1',
          'SEC-GPC': '1',
          'UPGRADE-INSECURE-REQUESTS': '1',
          'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) ' + \
                        'AppleWebKit/537.36 (KHTML, like Gecko) ' + \
                        'Chrome/112.0.0.0 Safari/537.36',
          }
  req = None

  @classmethod
  def setcontest(cls, contest):
    if cls.req is not None: return
    url = 'https://codeforces.com'
    if contest is not None:
      url += '/contest/' + contest + '/status'
    cls.req = Request(url=url, headers=cls.headers)

  def __new__(cls):
    raise TypeError('This class should not be instantiated')

  @classmethod
  def seterr(cls, err):
    cls.err = sub(':?\s*$', '', err)
    return False

  @classmethod
  def decompress(cls, text):
    try:
      return bdeflate(text).decode()
    except: pass
    try:
      return gdeflate(text).decode()
    except: pass
    try:
      return zdeflate(text).decode()
    except: pass
    try:
      return text.decode()
    except: pass
    return None

  @classmethod
  def gethtml(cls, url, allowincomplete=False):
    cls.req.full_url = url
    try:
      response = urlopen(cls.req, timeout=60)
    except Exception as e:
      try:
        response.close()
      except: pass
      return cls.seterr(str(e))
    if response.url != url:
      try:
        response.close()
      except: pass
      return cls.seterr('Redirect')
    try:
      body = response.read()
    except IncompleteRead as e:
      try:
        response.close()
      except: pass
      cls.seterr(f'IncompleteRead: {e}')
      return cls.decompress(e.partial) if allowincomplete else False
    except Exception as e:
      try:
        response.close()
      except: pass
      return cls.seterr(f'Error reading response: {e}')
    response.close()
    body = cls.decompress(body)
    if not body:
      return cls.seterr(f'Error decoding response: {e}')
    return body
