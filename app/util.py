from flask import Markup
from re import compile, sub, IGNORECASE
from time import localtime, strftime

from app import app


url_re = compile(r'(https?:\/\/(?:www\.)?([^: \/]+\.[^: \/]+)(?::\d+)?\/?[^\" ]*)', IGNORECASE)
irc_color_re = compile(r'(\x03(\d{1,2}(,\d{1,2})?)|[\x00\x01\x02\x03\x04\x05\x06\x07\x08\x09\x0a\x0b\x0c\x0d\x0e\x0f\x10\x11\x12\x13\x14\x15\x16\x17\x18\x19\x1a\x1b\x1c\x1d\x1e\x1f\x7f])')
formats = {
    'PRIVMSG': u'{time} < <span style="color: {color}">{nick}</span>> {msg}',
    'ACTION': u'{time} {msg}',
    'PART': u'{time} -!- {nick} [{user}] has left {chan} [{msg}]',
    'JOIN': u'{time} -!- {nick} [{user}] has joined {chan}',
    'MODE': u'{time} -!- mode/{chan} [{msg}] by {nick}',
    'KICK': u'{time} -!- {who} was kicked from {chan} by {nick} with reason {msg}',
    'TOPIC': u'{time} -!- {nick} changed the topic of {chan} to: {msg}',
    'QUIT': u'{time} -!- {nick} has quit IRC [{msg}]',
    'NICK': u'{time} -!- {nick} [{user}] is now known as {msg}',
}


def format_line(line):
    line['link'] = '/logviewer/{}/{}/{}'.format(line['chan'].strip('#'), *line['time'].split())
    line['time'] = line['time'][11:]

    line['msg'] = irc_color_re.sub('', line['msg'])
    line['msg'] = str(Markup.escape(line['msg'].encode('ascii', 'ignore')))
    line['msg'] = url_re.sub(r'<a href="\1">\1</a>', line['msg'])

    if line['action'] == 'KICK':
        line['who'], line['msg'] = line['msg'].split(' ', 1)

    line['msg'] = Markup(formats[line['action']].format(color=color_hash(line['nick']), **line))

    return line


def format_quote(quote):
    quote['date'] = "{} {}".format("Early" if int(strftime("%d", localtime(float(quote['uts'])))) < 15 else "Late",
        strftime("%b %Y", localtime(float(quote['uts']))))

    return quote


def color_hash(text):
    colors = ['rgb(0,51,187)', 'rgb(0,187,0)', 'rgb(255,85,85)', 'rgb(187,0,0)',
              'rgb(187,0,187)', 'rgb(187,187,0)', 'rgb(229,229,0)', 'rgb(85,252,85)',
              'rgb(0,187,187)', 'rgb(85,255,255)', 'rgb(85,85,252)', 'rgb(255,85,255)',
              'rgb(85,85,85)']
    return colors[sum(ord(c) for c in text.lower()) % 11]

