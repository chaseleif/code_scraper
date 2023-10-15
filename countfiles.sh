#! /usr/bin/env bash

#    countfiles.sh
#    Copyright (C) 2023  Chase Phelps
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <https://www.gnu.org/licenses/>.

pad() {
  [ "$#" -gt 1 ] && [ -n "$2" ] && printf "%$2.${2#-}s" "$1"
}

echo "______________________________"
ls progress/progress* > /dev/null 2>&1
if [ $? -ne 0 ] ; then
  echo "No progress files exist"
else
  if [ -f progress/lock ] ; then
    echo -n "$(pad "Running since:" -19)"
    timefile=progress/lock
    totalsecs=$(($(date +"%s")-$(date -r progress/lock +"%s")))
    elapseddays=$(($totalsecs/60/60/24))
    elapsedhours=$(($totalsecs/60/60%24))
    elapsedmins=$(($totalsecs/60%60))
    elapsedsecs=$(($totalsecs%60))
  else
    echo -n "$(pad "Last stopped:" -19)"
    timefile=$(ls -t progress/progress* | head -n1)
  fi
  echo $(date -r $timefile +"%d %b %R")
  if [ ! -z $totalsecs ] ; then
    echo -n "$(pad "Running time:" -19)"
    if [ $elapseddays -gt 0 ] ; then
      echo -n "$elapseddays day"
      if [ $elapseddays -ne 1 ] ; then echo -n "s" ; fi
      docomma=1
    fi
    if [ $elapsedhours -gt 0 ] ; then
      if [ ! -z $docomma ] ; then echo -n ", " ; else docomma=1 ; fi
      echo -n "$elapsedhours hour"
      if [ $elapsedhours -ne 1 ] ; then echo -n "s" ; fi
    fi
    if [ $elapsedmins -gt 0 ] ; then
      if [ ! -z $docomma ] ; then echo -n ", " ; else docomma=1 ; fi
      echo -n "$elapsedmins min"
      if [ $elapsedmins -ne 1 ] ; then echo -n "s" ; fi
    fi
    if [ $elapsedsecs -gt 0 ] ; then
      if [ ! -z $docomma ] ; then echo -n ", " ; fi
      echo -n "$elapsedsecs sec"
      if [ $elapsedsecs -ne 1 ] ; then echo -n "s" ; fi
    fi
    echo ""
  fi
  failedsubs=$(grep -R ^sub progress/progress* | wc -l)
  if [ $failedsubs -ne 0 ] ; then
    echo "$(pad "Failed retrievals:" -19)$failedsubs"
  fi
fi
if [ -f err.log ] ; then
  errors=$(grep ^\# err.log | wc -l)
  echo "$(pad "Errors logged:" -19)$errors"
  if [ ! -z $totalsecs ] ; then
    errorrate=$(echo "scale=4; $(($errors*60*60))/$totalsecs" | bc -l)
    if [[ "$errorrate" =~ ^\. ]] ; then
      errorrate=0$errorrate
    fi
    echo "$(pad "Errors per hour:" -19)$errorrate"
  fi
  echo "$(pad "Last error logged:" -19)$(date -r err.log +"%d %b %R")"
fi
if [ ! -z $1 ] && [ $1 == "-h" ] ; then
  sizes=($(du -c -d0 -h contest*/ 2> /dev/null))
else
  sizes=($(du -c -d0 -BM contest*/ 2> /dev/null))
fi
if [ $? -ne 0 ] ; then
  echo "No contest directories exist"
  echo "______________________________"
  exit
fi
totalfiles=0
for num in $(ls -d contest* | cut -dt -f3 | sort --numeric) ; do
  if [ ! -d contest$num ] ; then
    continue
  fi
  for i in ${!sizes[@]} ; do
    [[ ${sizes[$i]} =~ contest$num ]] && size=${sizes[$(($i-1))]} && break
  done
  filecount=$(find contest$num/ -type f | wc -l)
  totalfiles=$(($totalfiles+$filecount))
  if [ -f progress/progress$num ] ; then
    if [ -z $(grep ^\# progress/progress$num) ] ; then
      ipcount=$filecount
      ipsize=$size
      inprogress=$num
      continue
    fi
  fi
  if [ -z $printedcomplete ] ; then
    echo "______________________________"
    echo "Complete:"
    printedcomplete=1
  fi
  echo "$(pad contest$num -12)-$(pad $filecount 8)$(pad $size 7)"
done
if [ ! -z $inprogress ] ; then
  tput colors > /dev/null 2>&1
  if [ $? -eq 0 ] ; then
    bold=$(tput bold)
    normal=$(tput sgr0)
  fi
  echo "________________________________"
  echo -n $bold
  echo "In progress:"
  echo "$(pad contest$inprogress -12)-$(pad $ipcount 8)$(pad $ipsize 7)"
  echo -n $normal
fi
echo "________________________________"
echo "$(pad total -12)-$(pad $totalfiles 8)$(pad ${sizes[-2]} 7)"
