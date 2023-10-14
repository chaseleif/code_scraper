#! /usr/bin/env python3

from datetime import datetime
from secrets import choice, randbelow
from re import sub
from sys import stdout, stderr
from time import sleep, time

class Scraped:
  done = 0
  attempts = 0
  def __new__(cls):
    raise TypeError('This class should not be instantiated')

def exclaim():
  word = choice(exclaim.nxt)
  exclaim.nxt.remove(word)
  if len(exclaim.nxt) == 0: exclaim.nxt = exclaim.words.copy()
  return word

exclaim.words = ['Scheiße!','Mist!','Autsch!','Zur Hölle damit!',
          'Zum Teufel!','Verdammt nochmal ...','Idioten!','Arschlöcher!',
          'Zicken!','Luschen!','Arschmaden!','Fotzen!','Schlampen!',
          'Huren!','Scheißer!','Drecksäue!','Popiraten!']
exclaim.nxt = max(len(s) for s in exclaim.words)
exclaim.words = [' ' * ((exclaim.nxt-len(s))//2) + s for s in exclaim.words]
exclaim.words = [s + ' ' * (1+exclaim.nxt-len(s)) for s in exclaim.words]
exclaim.nxt = exclaim.words.copy()

INFO = '\033[38;5;98m'
BINFO = '\033[34;1m'
NUM = '\033[36;1m'
MSG = '\033[38;5;35m'
ERROR = '\033[38;5;1;1m'
WARN1 = '\033[33;1m'
WARN2 = '\033[38;5;196m'
WARN3 = '\033[38;5;52m'
GREEN = '\033[32m'
RESET = '\033[0m'
UNDERLINE = '\033[4m'

infc = lambda *text: INFO + ' '.join(text) + RESET
binfc = lambda *text: BINFO + ' '.join(text) + RESET
numc = lambda *text: NUM + ' '.join(text) + RESET
msgc = lambda *text: MSG + ' '.join(text) + RESET
errc = lambda *text: ERROR + exclaim() + ' '.join(text) + RESET
warn1 = lambda *text: WARN1 + ' '.join(text) + RESET
warn2 = lambda *text: WARN2 + ' '.join(text) + RESET
warn3 = lambda *text: WARN3 + ' '.join(text) + RESET
grnc = lambda *text: GREEN + ' '.join(text) + RESET

def stamp(*args, **opts):
  # Clear the line, some short messages may not clear previous text
  print('\x1b[0K', end='\r')
  ofile = stderr if any(ERROR in arg for arg in args) else stdout
  ending = opts['end'] if 'end' in opts else '\n'
  mytime = datetime.now()
  msg = grnc(f' [{mytime.hour:02d}:{mytime.minute:02d}.{mytime.second:02d}]')
  msg += ' ' + ' '.join(args)
  print(msg, end=ending, file=ofile, flush=True)
  if ofile == stderr:
    msg = f'[{mytime.hour:02d}:{mytime.minute:02d}.{mytime.second:02d}]'
    for arg in args:
      msg += ' ' + sub('\s+\s', ' ', arg.lstrip(ERROR).rstrip(RESET)).strip()
    msg += '\n#'
    if 'errinfo' in opts: msg += ' ' + opts['errinfo']
    with open('err.log', 'a') as outfile:
      outfile.write(msg + '\n')

def elapsed():
  seconds = int(round(time() - elapsed.start, 0))
  timestr = ''
  hours = seconds//3600
  seconds -= hours*3600
  days = ''
  if hours > 99:
    days = str(hours//24) + ':'
    hours %= 24
  mins = seconds//60
  seconds -= mins*60
  return f'{days}{hours:02d}:{mins:02d}.{seconds:02d}'

elapsed.start = time()

def sleepbreak(*args):
  scraperate = lambda: '' if Scraped.done == 0 \
              else f' (avg {round((time()-elapsed.start)/Scraped.done,1)}s)'
  basemsg = lambda: numc(f' [{elapsed()}] ' + \
                      f'{Scraped.done}/{Scraped.attempts} sources scraped' + \
                      scraperate())
  duration = args[0] if len(args) == 1 else 0
  if len(args) == 2:
    maxsleep = args[1]-args[0]+1
    if maxsleep > 0: duration = args[0] + randbelow(maxsleep)
  if duration < 1:
    print(basemsg(), end='\r')
    return False
  try:
    for delay in range(duration, -1, -1):
      msg = basemsg() + ' '
      warnc = 'warn1' if delay > 1 else 'warn2' if delay == 1 else 'warn3'
      msg += eval(warnc)('<use ctrl-c to quit within ') + \
                UNDERLINE + warn1(f'{delay}s') + \
                eval(warnc)('>') + '\x1b[0K'
      print(msg, end='\r')
      sleep(1)
  except KeyboardInterrupt:
    print('\r\x1b[0K' + basemsg())
    return True
  # CSI K - Erase cursor to end of line
  print(basemsg() + '\x1b[0K', end='\r')
  return False
