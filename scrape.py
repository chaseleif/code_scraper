#! /usr/bin/env python3

'''
    scrape.py
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

import os, re

from apihandler import APIHandler
from urltool import URLtool as urltool
from scrape_common import stamp, elapsed, sleepbreak, \
                          infc, binfc, numc, msgc, errc, Scraped

def savesource(contest, sub):
  err = lambda *s: stamp(errc('savesource:', *s),
                          errinfo=f'contest{contest}, sub{sub["id"]}')
  if os.path.isdir('contest' + contest + '/' + sub['lang']):
    for path in os.listdir('contest' + contest + '/' + sub['lang']):
      for name in os.listdir('/'.join(['contest' + contest,
                                        sub['lang'], path])):
        # already saved the source
        try:
          if sub['id'] == name.split('sub')[1].split('_')[0]:
            Scraped.done += 1
            return True
        except: pass
  savesource.errorcount += 1
  if sleepbreak(savesource.sleep, savesource.sleep * savesource.errorcount):
    return None
  if savesource.sleep < savesource.maxsleep:
    savesource.sleep *= 2
  url = 'https://codeforces.com/contest/' + contest + \
                                              '/submission/' + sub['id']
  response = urltool.gethtml(url)
  if urltool.err is not None:
    err(urltool.err)
    urltool.err = None
  if not response:
    return savesource(contest,sub) if savesource.errorcount < 3 else False
  response = response.split(sub['id'])
  # submission wasn't in the html
  if len(response) == 1:
    for thing in response:
      if 'Codeforces is temporarily unavailable' in thing:
        err('Codeforces is temporarily unavailable')
        if sleepbreak(300,600):
          return None
        return False
    with open('fail','w') as outfile:
      for i,thing in enumerate(response):
        outfile.write(str(i) + ': ' + thing)
    err('submission wasn\'t in the response')
    return False
  path = ''
  source = ''
  for i in range(len(response)):
    try:
      if source == '' and '<pre id=\"program-source-text' in response[i]:
        part = response[i].split('program-source-text')[1]
        source = part.split('>')[1].split('<')[0] + '\n'
        source = re.sub('&lt;', '<', source)
        source = re.sub('&gt;', '>', source)
        source = re.sub('&quot;', '\"', source)
        source = re.sub('&apos;', '\'', source)
        source = re.sub('&#39;', '\'', source)
        source = re.sub('&amp;', '&', source)
        source = re.sub('\r', '\n', source)
        source = re.sub('[\s]+\n', '\n', source)
      elif path == '' and 'Accepted' in response[i]:
        part = response[i].split('href=\"/contest')[1]
        path = 'contest' + part.split('\"')[0][1:]
        path = re.sub('problem', sub['lang'], path)
    except: pass
  source = source.rstrip()
  if path == '' or source == '':
    err('didn\'t parse the path or source')
    return False
  source += '\n'
  savesource.errorcount //= 2
  savesource.sleep //= 2
  if savesource.sleep > savesource.minsleep:
    savesource.sleep //= 2
  folders = path.split('/')
  path = ''
  for folder in folders:
    if not os.path.isdir(path + folder):
      os.mkdir(path + folder)
    path += folder + '/'
  name = 'sub' + '_'.join([sub['id'], sub['time'], sub['mem']]) + sub['ext']
  with open(path + name, 'w') as outfile:
    outfile.write(source)
  Scraped.done += 1
  return True

savesource.errorcount = 0
# sleep doubles every error
savesource.maxsleep = 384 # 3*(2**7)
savesource.minsleep = 15
savesource.sleep = savesource.minsleep

def retryskipped(startup=False):
  stamp(binfc('Checking for failed scrape attempts . . .'))
  for contest in os.listdir('progress/'):
    if not contest.startswith('progress'): continue
    missingsubs = 0
    with open('progress/' + contest, 'r') as infile:
      for line in infile.readlines():
        if line.startswith('sub'): missingsubs += 1
    if missingsubs == 0: continue
    if startup:
      Scraped.attempts += missingsubs
      urltool.setcontest(contest.split('progress')[1])
    plural = 's' if missingsubs != 1 else ''
    stamp(infc(f'Contest {contest.split("progress")[1]} has {missingsubs}',
              'missing submission' + plural))
    gotten = updateProgressFile(contest = contest.split('progress')[1],
                                start = 0,
                                retry = 0)
    if gotten is None: return False
    if missingsubs - gotten == 0:
      plural = 's' if gotten != 1 else ''
      stamp(infc('Retrieved', 'all of the' if gotten > 1 else 'the',
            'missing submission' + plural))
    else:
      plural = 's' if gotten != 1 else ''
      stamp(infc(f'Retrieved {gotten} previously missing submission' + plural))
      plural = 's' if missingsubs-gotten != 1 else ''
      stamp(infc(f'{missingsubs-gotten} submission' + plural, 'still missing'))
  stamp(infc('Done checking for failed scrape attempts, continuing . . .'))
  return True

def updateProgressFile(contest, start = 0, retry = None):
  savelines = []
  finalline = ''
  sleepbreak()
  if os.path.isfile('progress/progress' + contest):
    with open('progress/progress' + contest, 'r') as infile:
      for line in infile.readlines():
        line = line.strip()
        if line == '': continue
        if line.startswith('#'):
          finalline = line
          start = -1
        elif not line.startswith('sub'):
          if start >= 0 and start < int(line): start = int(line)
        elif line not in savelines:
          if retry is None:
            savelines.append(line)
          else:
            good = False
            try:
              sub = {}
              for part in line.split('#')[1:-1]:
                parts = part.split('=')
                sub[parts[0]] = parts[1]
              good = savesource(contest, sub)
            except Exception as e:
              stamp(errc(f'updateProgressFile: {e}'),
                                errinfo=f'contest{contest}, sub{sub["id"]}')
            if good is None: return None
            if good: retry += 1
            else: savelines.append(line)
  if start == 0: start = 1
  with open('progress/progress' + contest, 'w') as outfile:
    for line in savelines:
      outfile.write(line + '\n')
    if start > 0: outfile.write(str(start))
    else: outfile.write(finalline)
  if retry is not None: return retry
  return start

def getcontests(api):
  # Get a list of contest ids
  contests = None
  if os.path.isfile('contests'):
    with open('contests', 'r') as infile:
      contests = [ line.strip() for line in infile.readlines() \
                          if line.strip() != '' ]
    stamp(binfc('Loaded'), numc(str(len(contests))), binfc('contests'))
  else:
    urltool.setcontest(None)
    stamp(binfc('Getting a list of contest ids'))
    contests = api.request('contest.list', 'gym=false')
    if contests is None: return None
    if not contests:
      stamp(errc('getcontests unable to get contest list'))
      return None
    stamp(binfc('Retrieved'), numc(str(len(contests))), binfc('contests'))
    contests = [ str(contest['id']) for contest in contests \
                          if contest['phase'] == 'FINISHED' ]
    with open('contests', 'w') as outfile:
      outfile.write('\n'.join(contests))
    stamp(binfc('There are'), numc(str(len(contests))), binfc('contests'))
  # Get to the first contest that hasn't been marked as finished
  skipcontests = []
  for contest in contests:
    start = updateProgressFile(contest)
    if start < 0:
      skipcontests.append(contest)
      continue
    if len(skipcontests) == 0: break
    if len(skipcontests) == 1:
      stamp(infc('Skipped contest'), numc(skipcontests[0]))
      break
    # Don't wrap lines, get maximum printable length
    maxlen = min(80, os.get_terminal_size()[0]) - len(' [hh:mm.ss] ') - 1
    printstr = 'Skipped contests:'
    currlen = len(printstr) + 1 + len(skipcontests[0])
    printstr = infc(printstr) + ' '
    skipstr = skipcontests[0]
    for part in skipcontests[1:]:
      if currlen + 2 + len(part) < maxlen:
        currlen += 2 + len(part)
        skipstr += ', ' + part
      else:
        stamp(printstr + numc(skipstr))
        printstr = '                  '
        skipstr = part
        currlen = len(printstr) + len(part)
    stamp(printstr + numc(skipstr))
    break
  # Remove skipped contests
  for skip in skipcontests: contests.remove(skip)
  if len(contests) == 0: return None
  # Reverse to pop from the back
  contests.reverse()
  return contests

def scrape(step=50):
  api = APIHandler(apifile = 'apikey')
  skippedlangs = []
  if os.path.isfile('progress/skippedlangs'):
    with open('progress/skippedlangs', 'r') as infile:
      skippedlangs = [ line.strip() for line in infile.readlines() \
                          if line.strip() != '' ]
  acceptedlangs = []
  if os.path.isfile('progress/acceptedlangs'):
    with open('progress/acceptedlangs', 'r') as infile:
      acceptedlangs = [ line.strip() for line in infile.readlines() \
                          if line.strip() != '' ]
  contests = getcontests(api)
  if contests is None: return
  # Iterate over unfinished contests
  while len(contests) > 0:
    contest = contests.pop()
    start = updateProgressFile(contest)
    stamp(binfc('Getting submissions for contest'),
          numc(contest),
          binfc('. . .'))
    urltool.setcontest(contest)
    while True:
      submissions = api.request('contest.status',
                                'contestId=' + contest,
                                'from=' + str(start),
                                'count=' + str(step))
      if submissions is None: return
      if Scraped.attempts - Scraped.done > 10 and not retryskipped():
        return
      stamp('     ' + msgc(f'~ {start}-{start+step-1} ~ '), end='')
      # No submissions
      if not submissions or len(submissions) == 0:
        print(msgc('no submissions ~'))
        with open('progress/progress' + contest, 'a') as outfile:
          outfile.write('\n#' + str(start))
        updateProgressFile(contest, start)
        break
      start += len(submissions)
      countlang = 0
      countverdict = 0
      attemptlist = []
      while len(submissions) > 0:
        sub = submissions.pop()
        # only accepted submissions
        if sub['verdict'] != 'OK':
          countverdict += 1
          continue
        # Only C or C++
        if 'GNU C' not in sub['programmingLanguage'] and \
            'C++' not in sub['programmingLanguage'] and \
            'Clang' not in sub['programmingLanguage']:
          countlang += 1
          if sub['programmingLanguage'] not in skippedlangs:
            with open('progress/skippedlangs', 'a') as outfile:
              outfile.write(sub['programmingLanguage'] + '\n')
            skippedlangs.append(sub['programmingLanguage'])
          continue
        if sub['programmingLanguage'] not in acceptedlangs:
          with open('progress/acceptedlangs', 'a') as outfile:
            outfile.write(sub['programmingLanguage'] + '\n')
          acceptedlangs.append(sub['programmingLanguage'])
        Scraped.attempts += 1
        mem = re.sub(' ', '', str(sub['memoryConsumedBytes'])) + 'B'
        ms = re.sub(' ', '', str(sub['timeConsumedMillis'])) + 'ms'
        lang = re.sub(' ', '', str(sub['programmingLanguage']))
        lang = re.sub('\+', 'p', lang)
        lang = re.sub('\(64\)', 'x64', lang)
        lang = re.sub('Diagnostics', 'Diag', lang)
        lang = re.sub('2017', '17', lang)
        ext = '.cpp' if 'pp' in lang else '.c'
        attemptlist.append({'id':str(sub['id']),
                            'mem':mem,
                            'time':ms,
                            'lang':lang,
                            'ext':ext})
      plural = 's' if len(attemptlist) != 1 else ''
      print(msgc(f'getting {len(attemptlist)} submission{plural} ~'))
      countgood = 0
      countbad = 0
      while len(attemptlist) > 0:
        sub = attemptlist.pop()
        good = False
        try:
          good = savesource(contest, sub)
        except Exception as e:
          stamp(errc(f'scrape: {e}'),
                                errinfo=f'contest{contest}, sub{sub["id"]}')
        if good is None: return
        if good: countgood += 1
        else:
          countbad += 1
          with open('progress/progress' + contest, 'a') as outfile:
            outfile.write('\nsub#')
            for key in sub:
              outfile.write(key + '=' + sub[key] + '#')
      stamp(msgc(f'{countgood} scraped, {countbad} not scraped, ' + \
            f'{countverdict} not passing, {countlang} not C/C++'))
      updateProgressFile(contest, start)
    stamp(binfc(f' ~ Finished contest {contest} ~'))
    if not retryskipped():
      return

if __name__ == '__main__':
  if not os.path.isdir('progress'):
    os.mkdir('progress')
  if not os.path.exists('progress/lock'):
    with open('progress/lock', 'w') as outfile: pass
    if os.listdir('progress') == ['lock'] or retryskipped(True):
      scrape()
    try:
      os.remove('progress/lock')
    except: pass
  else:
    stamp('Scrape script is already running!')
    print(' ' * (len(elapsed()) + 4) + binfc('Remove the progress/lock file'))
  print(' ' * (len(elapsed()) + 4) + binfc('Goodbye'))

# vim: tabstop=2 shiftwidth=2 expandtab
