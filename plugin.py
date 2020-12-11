###
# Copyright (c) 2020, mogad0n
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#   * Redistributions of source code must retain the above copyright notice,
#     this list of conditions, and the following disclaimer.
#   * Redistributions in binary form must reproduce the above copyright notice,
#     this list of conditions, and the following disclaimer in the
#     documentation and/or other materials provided with the distribution.
#   * Neither the name of the author of this software nor the name of
#     contributors to this software may be used to endorse or promote products
#     derived from this software without specific prior written consent.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED.  IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

###

### My libs

import re
import os
import sys
import time
import json
import pickle

### Supybot libs

from supybot import utils, plugins, ircmsgs, ircutils, callbacks, ircdb, conf, log, world
from supybot.commands import *
try:
    from supybot.i18n import PluginInternationalization
    _ = PluginInternationalization('ConnectionLogger')
except ImportError:
    # Placeholder that allows to run the plugin on a bot
    # without the i18n module
    _ = lambda x: x

# use sqlite instead 
filename = conf.supybot.directories.data.dirize("ConnectionLogger.db")


class ConnectionLogger(callbacks.Plugin):
    """Should Log connection information and display in a given channel"""

    threaded = True

    def doNotice (self, irc, msg):
        (target, text) = msg.args
        if target == irc.nick:
            # server notices CONNECT, KILL, XLINE
            text = ircutils.stripFormatting(text)
            if 'CONNECT' in text:
                connregex = "^-CONNECT- Client connected \[?(.+)\] \[u\:~?(.+)\] \[h\:?(.+)\] \[ip\:?(.+)\] \[r\:?(.+)\]$"
                couple = re.match(connregex, text)
                nickname = couple.group(1)
                username = couple.group(2)
                host = couple.group(3)
                ip = couple.group(4)
                realname = couple.group(5)
                ip_seen = 0
                nick_seen = 0
                DictFromSnotice = {'notice': 'connect', 'nickname': nickname, 'username': username, 'host': host, 'ip': ip, 'realname': realname, 'ipCount': ip_seen, 'nickCount': nick_seen}
                re = f"\x02\x1FNOTICE: {DictFromSnotice['notice']}\x0F\x11\x0303==>>\x0F \x02Nick:\x0F {DictFromSnotice['nickname']} \x02Username:\x0F {DictFromSnotice['username']} \x02Hostname:\x0F {DictFromSnotice['host']} \x02IP:\x0F {DictFromSnotice['ip']} \x02Realname:\x0F {DictFromSnotice['realname']} \x02IPcount:\x0F {DictFromSnotice['ipCount']} \x02NickCount:\x0F {DictFromSnotice['nickCount']}"
                self._sendSnotice(irc, msg, re)
            elif 'KILL' in text:
                killregex = "^-KILL- (.+) \[(.+)\] killed (\d) clients with a (KLINE|DLINE) \[(.+)\]$"
                couple = re.match(killregex, text)
                who = couple.group(1)
                who_operator = couple.group(2)
                clients = couple.group(3)
                which_line = couple.group(4)
                nick = couple.group(5)
                DictFromSnotice = {'notice': 'kill', 'who': who, 'operator': who_operator, "client": clients, 'type': which_line, 'nick': nick}
                re = f"\x02\x1FNOTICE: {DictFromSnotice['notice']} \x0F\x11\x0303☠\x0F \x02KilledBy:\x0F {DictFromSnotice['who']} \x02KilledByOper:\x0F {DictFromSnotice['operator']} \x02NumofClientsAffected:\x0F {DictFromSnotice['client']} \x02XLINE Type:\x0F {DictFromSnotice['type']} \x02Nick:\x0F {DictFromSnotice['nick']}"
                self._sendSnotice(irc, msg, re)
            elif 'XLINE' in text and 'temporary' in text:
                xlineregex = "^-XLINE- (.+) \[(.+)\] added a temporary \((.+)\) (K-Line|D-Line) for (.+)$"
                couple = re.match(xlineregex, text)
                who = couple.group(1)
                who_operator = couple.group(2)
                duration = couple.group(3)
                which_line = couple.group(4)
                host_or_ip = couple.group(5)
                DictFromSnotice = {'notice': 'tempban', 'who': who, 'operator': who_operator, 'duration': duration, 'type': which_line, 'target': host_or_ip}
                re = f"\x02\x1FNOTICE: {DictFromSnotice['notice']}\x0F \x11\x0303🚫\x0F \x02BannedBy:\x0F {DictFromSnotice['who']} \x02BannedByOper:\x0F {DictFromSnotice['operator']} \x02Duration:\x0F {DictFromSnotice['duration']} \x02XLINE Type:\x0F {DictFromSnotice['type']} \x02Nick:\x0F {DictFromSnotice['nick']}"
                self._sendSnotice(irc, msg, DictFromSnotice, re)
            elif 'XLINE' in text and 'removed' not in text:
                perm_xline_regex = "^-XLINE- (.+) \[(.+)\] added (D-Line|K-Line) for (.+)$"
                couple = re.match(perm_xline_regex, text)
                who = couple.group(1)
                who_operator = couple.group(2)
                which_line = couple.group(3)
                host_or_ip = couple.group(4)
                DictFromSnotice = {'notice': 'Permaban', 'who': who, 'operator': who_operator, 'duration': duration, 'type': which_line, 'target': host_or_ip}
                re = f"\x02\x1FNOTICE: {DictFromSnotice['notice']} \x0F \x11\x0303🚫\x0F \x02BannedBy:\x0F {DictFromSnotice['who']} \x02BannedByOper:\x0F {DictFromSnotice['operator']} \x02XLINE Type:\x0F {DictFromSnotice['type']} \x02Host/IP:\x0F {DictFromSnotice['target']}"
                self._sendSnotice(irc, msg, re)
            elif 'XLINE' in text and 'removed' in text:
                unxlineregex = "^-XLINE- (.+) removed (D-Line|K-Line) for (.+)$"
                couple = re.match(unxlineregex, text)
                who = couple.group(1)
                which_line = couple.group(4)
                host_or_ip = couple.group(5)
                DictFromSnotice = {'notice': 'unxline', 'who': who, 'type': which_line, 'target': host_or_ip}
                re = f"\x02\x1FNOTICE: {DictFromSnotice['notice']} \x0F\x11\x0303😇\x0F \x02UnbannedBy:\x0F {DictFromSnotice['who']} \x02XLINE type:\x0F {DictFromSnotice['type']} \x02Host/IP:\x0F {DictFromSnotice['target']}"
                self._sendSnotice(irc, msg, re)

    def _sendSnotice(self, irc, msg, re):
        irc.queueMsg(msg=ircmsgs.IrcMsg(command='PRIVMSG',
                    args=('#snotices', re)))

Class = ConnectionLogger


# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79: