import os

_cmd_pip = "pip install -r requirements.txt"
os.system(_cmd_pip)
_cmd_conda = "conda install -y --file requirements.yml"
os.system(_cmd_conda)



