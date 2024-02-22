# make an isolated python environment (recommended)
Set up pyenv: https://github.com/pyenv/pyenv
Set up pyenv virtualenv: https://github.com/pyenv/pyenv-virtualenv 
use pyenv to install python 3.11.2 or greater (should work with 3.5+ but I'm using 3.11.2)

`pyenv virtualenv markov_bot`
`pyenv activate markov_bot`

# install python requirements
`pip install -r requirements.txt`

# discord_demo.py
populate the discoord token in .env
run
`./discod_bot.py`

# docs load test
just run:
`./load_dcs.py`

this is a basic test of the MatrixMarkov class
