from app import app


def color_hash(text):
    colors = ['rgb(0,51,187)', 'rgb(0,187,0)', 'rgb(255,85,85)', 'rgb(187,0,0)',
              'rgb(187,0,187)', 'rgb(187,187,0)', 'rgb(229,229,0)', 'rgb(85,252,85)',
              'rgb(0,187,187)', 'rgb(85,255,255)', 'rgb(85,85,252)', 'rgb(255,85,255)',
              'rgb(85,85,85)']
    return colors[sum(ord(c) for c in text) % 11]
