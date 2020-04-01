from app import app


def color_hash(text):
    colors = ['rgb(0,0,127)', 'rgb(0,147,0)', 'rgb(255,0,0)', 'rgb(127,0,0)',
              'rgb(156,0,156)', 'rgb(252,127,0)', 'rgb(255,255,0)', 'rgb(0,252,0)',
              'rgb(0,147,147)', 'rgb(0,255,255)', 'rgb(0,0,252)', 'rgb(255,0,255)',
              'rgb(127,127,127)']
    return colors[sum(ord(c) for c in text) % 11]
