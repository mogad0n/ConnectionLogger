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

import re
import os
import sys
import time

from supybot import utils, plugins, ircutils, callbacks, ircdb, conf,
from supybot.commands import *
try:
    from supybot.i18n import PluginInternationalization
    _ = PluginInternationalization('ConnectionLogger')
except ImportError:
    # Placeholder that allows to run the plugin on a bot
    # without the i18n module
    _ = lambda x: x

class ConnectionLogger(callbacks.Plugin):
    """Should Log connection information and display in a given channel"""

    threaded = True

    def doNotice (self, irc, msg):
        (targets, text) = msg.args
        if len(targets) and targets[0] == irc.nick:
            # server notices
            text = ircutils.stripFormatting(text)
            connregex = "^-CONNECT- Client\sconnected\s\[(.+)\]\s\[u\:~?(.+)\]\s\[h\:(.+)\]\s\[ip\:(.+)\]\s\[r\:(.+)\]$"
            conn = re.match(connregex, text)
            nick = conn.group(1)
            username = conn.group(2)
            host = conn.group(3)
            ip = conn.group(4)
            realname = conn.group(5)
    irc.queueMsg(msg=ircmsgs.IrcMsg(command='PRIVMSG',
                    args=('#connects', f'nick: {nick} username: {username} hostname: {host} ip: {ip} realname: {realname}')))

Class = ConnectionLogger


# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:
