#!/usr/bin/env python3

# timerBeetle is a terminal timer.
# Its name is an allusion to the tiger beetle,
# a ferocious predator that runs fast.
# Like time.

# I use this by aliasing it to "t" in ~/.bashrc,
#     alias t="path/to/timerBeetle.py"
# and easily calling it in a dropdown terminal like Yakuake.
#     Dropdown,
#     punch in "t 20",
#     rollup,
#     hear the alarm when it finishes.

import sys
import re
import time
import subprocess
# Non-blocking input stuff,
# cargo culted from https://stackoverflow.com/a/2409034
import select
import tty
import termios

# ANSI color escape codes:
# https://en.wikipedia.org/wiki/ANSI_escape_code#3/4_bit
brightYellow = '\033[93m'
brightGreen = '\033[92m'
yellow = '\033[33m'
blinking = '\033[5m'
inverted = '\033[7m'
dim = '\033[2m'
reset = '\033[0m'

###############################################################################
# Returns total time in seconds given by user                                 #
#                                                                             #
# The input, sys.argv[1] and onwards, can have several formats:               #
# "23" = 23 minutes                                                           #
# "23m" = 23 minutes                                                          #
# "2h" = 2 hours                                                              #
# "6s" = 6 seconds                                                            #
# "1d" = 1 day                                                                #
# "1h 30m" = 1 hour, 30 minutes                                               #
# "1d12h30m30s" = 1 day, 12 hours, 30 minutes, 30 seconds                     #
###############################################################################
def parseTimeInSecs():
    timeIn = ''

    # Get time args
    if len(sys.argv) == 1:
        print('ERROR: Missing input! ' +\
            brightGreen +\
            ',' +\
            yellow +\
            '?' +\
            brightGreen +\
            'w' +\
            yellow +\
            '?' +\
            brightGreen +\
            ',' +\
            reset +\
            ' Put like \"1h30m\" or just like \"25\" for minutes.')
        sys.exit(1)
    if len(sys.argv) == 2:
        timeIn = sys.argv[1]
    else:
        for i in range(1, len(sys.argv)):
            timeIn += sys.argv[i]

    # Simple min format
    if timeIn.isdigit():
        return int(timeIn) * 60

    # Multiunit format
    timeIn = timeIn.lower()
    wholeMatchObj = re.match('^(\\d+[dhms])[ ]*\
(\\d+?[dhms])?[ ]*\
(\\d+?[dhms])?[ ]*\
(\\d+?[dhms])?[ ]*$', timeIn)

    gotDay = False
    gotHr = False
    gotMin = False
    gotSec = False

    if wholeMatchObj is None:
        print('ERROR: Bad input! ' +\
            brightGreen +\
            ',' +\
            yellow +\
            '>' +\
            brightGreen +\
            'w' +\
            yellow +\
            '<' +\
            brightGreen +\
            ',' +\
            reset +\
            ' Do like \"1h30m\" or just like \"25\" for minutes.')
        sys.exit(1)
    else:
        totalSecs = 0

        for group in wholeMatchObj.groups():
            if group is not None:
                # A group has something like " 12h"
                groupMatchObj = re.match('^[ ]*(\\d+)([dhms])$', group)
                amount = int(groupMatchObj.group(1))
                unit = groupMatchObj.group(2)

                if unit == 'd' and not gotDay:
                    gotDay = True
                    totalSecs += amount * 24 * 60 * 60
                elif unit == 'h' and not gotHr:
                    gotHr = True
                    totalSecs += amount * 60 * 60
                elif unit == 'm' and not gotMin:
                    gotMin = True
                    totalSecs += amount * 60
                elif unit == 's' and not gotSec:
                    gotSec = True
                    totalSecs += amount
                else:
                    print('ERROR: Repeated units in input! ' +\
                        brightGreen +\
                        ',' +\
                        yellow +\
                        '¬' +\
                        brightGreen +\
                        'w' +\
                        yellow +\
                        '¬' +\
                        brightGreen +\
                        ',' +\
                        reset)
                    sys.exit(1)

        return totalSecs

###############################################################################
# Non-blocking input sensing                                                  #
###############################################################################
def gotInput():
    return select.select([sys.stdin], [], [], 0) == ([sys.stdin], [], [])

###############################################################################
# Main                                                                        #
####################################################################\UwU/######
def main():
    secsIn = parseTimeInSecs()

    alarmSoundPath = sys.path[0] + '/assets/alarm_sound.wav'
    iconPath = sys.path[0] + '/assets/icon.png'

    # Non-blocking input boilerplate
    oldSettings = termios.tcgetattr(sys.stdin)
    try:
        tty.setcbreak(sys.stdin.fileno())

        # Countdown
        while secsIn:
            mins, secs = divmod(secsIn, 60) # (quotient, remainder)
            hrs, mins = divmod(mins, 60)
            days, hrs = divmod(hrs, 24)

            # '{:02d}:{:02d}'.format(mins, secs) # "0q:0r"
            format = ''

            if days > 0:
                if days > 99:
                    # Time output strings maintain a base length of 50 chars
                    format = '# ' +\
                        inverted +\
                        '>99:{:02d}:{:02d}:{:02d}'.format(hrs, mins, secs) +\
                        reset +\
                        ' ######### '
                else:
                    format = '# ' +\
                        inverted +\
                        '{:02d}:{:02d}:{:02d}:{:02d}'.format(days, hrs, mins,
                            secs) +\
                        reset +\
                        ' ########## '
            elif hrs > 0:
                format = '# ' +\
                    inverted +\
                    '{:02d}:{:02d}:{:02d}'.format(hrs, mins, secs) +\
                    reset +\
                    ' ############# '
            else:
                format = '# ' +\
                    inverted +\
                    '{:02d}:{:02d}'.format(mins, secs) +\
                    reset +\
                    ' ################ '
            # Mascot animation
            # />w>/
            # \<w<\
            # Searching for prey...
            if secsIn % 2 == 0:
                format += brightGreen +\
                    '/' +\
                    yellow +\
                    '>' +\
                    brightGreen +\
                    'w' +\
                    yellow +\
                    '>' +\
                    brightGreen +\
                    '/' +\
                    reset +\
                    dim +\
                    ' Hit Space to pause.' +\
                    reset
            else:
                format += brightGreen +\
                    '\\' +\
                    yellow +\
                    '<' +\
                    brightGreen +\
                    'w' +\
                    yellow +\
                    '<' +\
                    brightGreen +\
                    '\\' +\
                    reset +\
                    dim +\
                    ' Hit Space to pause.' +\
                    reset
            print(format, end='\r') # '\r' to avoid newlines

            # Pause/Resume
            if gotInput(): # Non-blocking wait for pause key
                pauseIn = sys.stdin.read(1)

                if pauseIn == ' ':
                    pauseIn = '';
                    print(brightYellow +\
                        '#' +\
                        blinking +\
                        ' Hit Space to resume. ' +\
                        reset +\
                        brightGreen +\
                        ',' +\
                        yellow +\
                        'u' +\
                        brightGreen +\
                        'w' +\
                        yellow +\
                        'u' +\
                        brightGreen +\
                        ',' +\
                        reset +\
                        '                      ',
                        end='\r')
                    while pauseIn != ' ': # Blocking wait for resume key
                        pauseIn = sys.stdin.read(1)
                    # Somehow, 2 secs are consumed by all this; give them back
                    secsIn += 2

            time.sleep(1)
            secsIn -= 1
    finally:
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, oldSettings)

    # Finished; play alert sound and show notification
    finishTime = time.strftime('%H:%M:%S')

    subprocess.Popen(['aplay', '-q', alarmSoundPath])
    subprocess.Popen(['notify-send', '-t', '5000', '-u', 'normal', '-i',
        iconPath, '\\OwO/\n*Timer beetle BITES!* (@ ' + finishTime + ')'])
    print('*Timer beetle BITES!* ' +\
        brightGreen +\
        '\\' +\
        yellow +\
        'O' +\
        brightGreen +\
        'w' +\
        yellow +\
        'O' +\
        brightGreen +\
        '/' +\
        reset +\
        dim +\
        ' (@ ' +\
        finishTime +\
        ')' +\
        reset +\
        '          ')

if __name__ == '__main__': main()
