import os
from pathlib import Path

print(os.listdir(Path.cwd()))
if 'last' in os.listdir(Path.cwd()):
    print('ДА')

os.chdir(str(Path.cwd()) + '\output\прув')
print(Path.cwd())