# make an isolated python environment (recommended)
Set up pyenv: https://github.com/pyenv/pyenv
Set up pyenv virtualenv: https://github.com/pyenv/pyenv-virtualenv 
use pyenv to install python 3.11.2 or greater (should work with 3.5+ but I'm using 3.11.2)

`pyenv virtualenv markov_bot`
`pyenv activate markov_bot`

# install python requirements
`pip install -r requirements.txt`

# convert arbitrary text to yaml (optional); use this to seed the bot
`./make_yaml.py --garbage-in some_text_file.txt --garbage-out serialized.yaml` 
 
# run the local bot server
`./main.py --local_server_port 7878 -b seriialized.yaml -o backup_brain.yaml -n RobotName`

# connect to the bot
From another window (linux):
`nc localhost 7878`
