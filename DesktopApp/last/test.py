import os
from pathlib import Path

if '1.csv' in os.listdir(Path.cwd()):
    print('ДА')
