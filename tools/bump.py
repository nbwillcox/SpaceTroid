"""Stamps every script tag in index.html with ?v=<stamp> so browsers (and GitHub Pages' CDN) fetch fresh files after a push. Usage: python tools/bump.py [stamp]"""
import re, sys, time, os
p = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'index.html')
stamp = sys.argv[1] if len(sys.argv) > 1 else time.strftime('%Y%m%d%H%M')
s = open(p, encoding='utf-8').read()
s = re.sub(r'<script src="([^"?]+)(\?v=[^"]*)?"></script>', lambda m: '<script src="%s?v=%s"></script>' % (m.group(1), stamp), s)
open(p, 'w', encoding='utf-8').write(s)
print('stamped', len(re.findall(r'\?v=%s' % stamp, s)), 'scripts with', stamp)
