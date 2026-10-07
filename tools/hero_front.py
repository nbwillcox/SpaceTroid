"""Front-facing hero (used when saving): the left half is drawn, the right half is its mirror one shade darker. Result: 34 wide x 47 tall, feet on row 46."""
HALF = [
    # helmet
    "......oooooooo",
    "....oo34444444",
    "...o3444444444",
    "..o34444444433",
    "..o44444433322",
    "..o4444oqVVVVV",
    "..o4443oxVWWWW",
    "..o3332oxVWWWW",
    "..o3322oxvVVVV",
    "...o222ooxxxxx",
    "....o2211yyyyy",
    ".....oo1111yyy",
    # neck + shoulders
    "......ooooooo3",
    "...ooooo344444",
    "..o33444344444",
    ".o3444444333yy",
    ".o44444443332y",
    # chest and arms
    ".o4k3o44322211",
    ".o4yko4332211y",
    ".o3kyo43322111",
    ".o23ko33221111",
    ".o2yko32211ooo",
    ".o23ko3221oMml",
    ".o2yko22211oml",
    ".o23ko211oooLL",
    ".oo2ko2ooyYyyy",
    "..o2yo.oyYwYyY",
    "..oooo.ooooooo",
    # waist
    "....oyYkyyyyyy",
    "....ooooooooo1",
    # legs
    "....o32211111o",
    "....o32211111o",
    "....o32211111o",
    "....o3yyy1111o",
    "....o3yYk1111o",
    "....o32111111o",
    "....o32111111o",
    "....o32111111o",
    "...o321111111o",
    "...o321111111o",
    "...o3211111111",
    "...o3211111111",
    "..o32111111111",
    "..o3221111111o",
    ".oyyy21111111o",
    ".oYyY2111111oo",
    ".ooooooooooooo",
]
SHADE = {'4': '3', '3': '2', '2': '1', 'V': 'v', 'W': 'V', 'Y': 'y', 'y': 'k', 'l': 'm', 'L': 'l'}

def build(pad=3):
    rows = []
    for h in HALF:
        assert len(h) == 14, (len(h), h)
        right = ''.join(SHADE.get(c, c) for c in reversed(h))
        full = h + right
        rows.append('.' * pad + full + '.' * (34 - pad - len(full)))
    top = 47 - len(rows)
    return ['.' * 34] * top + rows

if __name__ == '__main__':
    for r in build(): print(r)
