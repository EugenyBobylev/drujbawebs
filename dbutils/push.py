import shutil
from pathlib import Path


if __name__ == '__main__':
    p = Path.cwd()
    s = p.parent / "webapp"
    d = p.parent.parent / 'drujbawebs' / 'webapp'
    print(p)
    print(s)
    print(d)
    shutil.rmtree(d)
    shutil.copytree(s, d)
