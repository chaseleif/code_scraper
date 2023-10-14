#! /usr/bin/env python3

import os, sys
from math import sqrt

def plotline(count, minv, maxv, meanv, stddev):
  numcols = os.get_terminal_size()[0]
  numrange = maxv-minv
  if numrange == 0:
    minline = (numcols-10)//2
    maxline = minline
    tickwidth = 1
    meanline = minline
  else:
    minline = 10
    maxline = numcols - 2
    screenrange = maxline-minline
    tickwidth = numrange/screenrange
    meanline = minline + int(round((meanv-minv)/tickwidth,0))
  minusdev = meanv - stddev
  plusdev = meanv + stddev
  minusline = meanline - int(round(stddev/tickwidth,0))
  plusline = meanline + int(round(stddev/tickwidth,0))
  for i in range(6, maxline+1):
    if i < minline: print(' ', end='')
    elif i == minusline: print('[', end='')
    elif i == plusline: print(']', end='')
    elif i == minline or i == maxline or i == meanline: print('|', end='')
    else: print('-', end='')
  print('')
  minv = str(minv)
  maxv = str(maxv)
  meanv = str(int(meanv))
  minusdev = str(int(minusdev))
  plusdev = str(int(plusdev))
  numcounter = 0
  print(f'{count} ->', end='')
  for i in range(len(str(count))+3, maxline):
    if i < minline - len(minv) + 1: print(' ', end='')
    elif numcounter > 1: numcounter -= 1
    elif numcounter == 1:
      numcounter = 0
      print(' ', end='')
    elif i == minline - len(minv) + 1:
      print(minv, end='')
      numcounter = len(minv)
    elif i == meanline - len(meanv) + 1:
      print(meanv, end='')
      numcounter = len(meanv)
    elif i == maxline - len(maxv) + 1:
      print(maxv, end='')
      numcounter = len(maxv)
    elif i == minusline - len(minusdev) + 1 and \
        i + len(minusdev) < meanline - len(meanv) + 1:
      print(minusdev, end='')
      numcounter = len(minusdev)
    elif i == plusline - len(plusdev) + 1 and \
        i + len(plusdev) < maxline - len(maxv) + 1:
      print(plusdev, end='')
      numcounter = len(plusdev)
    else: print(' ', end='')
  print('')

def doplots(docontest, viz):
  nums = []
  for contest in os.listdir():
    if not os.path.isdir(contest): continue
    if not contest.startswith('contest'): continue
    if docontest and docontest != contest: continue
    nums.append(int(contest.split('contest')[1]))
  for num in sorted(nums):
    contest = 'contest' + str(num)
    problems = {}
    for lang in os.listdir(contest):
      for problem in os.listdir(contest + '/' + lang):
        if problem not in problems:
          problems[problem] = {'min':99999,'max':0,'mean':0,'var':0,'count':0}
        for code in os.listdir('/'.join([contest, lang, problem])):
          problems[problem]['count'] += 1
          time = int(code.split('_')[1].split('ms')[0])
          if time < problems[problem]['min']: problems[problem]['min'] = time
          if time > problems[problem]['max']: problems[problem]['max'] = time
          oldmean = problems[problem]['mean']
          problems[problem]['mean'] += \
            (time-problems[problem]['mean']) / problems[problem]['count']
          problems[problem]['var'] += \
            (time-problems[problem]['mean']) * (time-oldmean)
    for problem in problems:
      problems[problem]['var'] /= problems[problem]['count']
      problems[problem]['mean'] = int(problems[problem]['mean'])
      problems[problem]['stddev'] = int(sqrt(problems[problem]['var']))
      problems[problem]['var'] = int(problems[problem]['var'])
    if not viz: print(f'{"Count":>12} | Min | Max | Mean | Stddev')
    print(f'{"#"+str(contest):>6}')
    for problem in sorted(list(problems.keys())):
      item = problems[problem]
      if item['min'] == 0: continue
      if viz:
        print(f'{problem:>6}', end='')
        plotline(item['count'],
                item['min'], item['max'], item['mean'], item['stddev'])
      else:
        print(f'{problem:>6}' + \
              f'  {item["count"]:<5} {item["min"]:<5} {item["max"]:<6} ' + \
              f'{item["mean"]:<6} {item["stddev"]:<6}')

if __name__=='__main__':
  docontest = None
  viz = False
  for i in range(1,len(sys.argv)):
    if sys.argv[i].startswith('-'): viz = True
    elif sys.argv[i].startswith('contest'): docontest = sys.argv[i]
  doplots(docontest, viz)
