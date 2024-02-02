# assuming prroperly configured pyenv
**NOTE** plan to run markovizer as independent user w/ systemd supervising
* log in as appropriate user with configured pyenv
* cd to markov_demo (should activate virtualenv)
* confirm python version: `python --version` should be 3.11.7
## Sparse checkout python code
* `git clone --depth 1 --no-checkout https://github.com/Trogluddite/loombreaker`
* `cd loombreaker`
* `git sparse-checkout set markov_demo`
* `git checkout`
## set up bot
* `pip install -r requirements.txt`
* download some starter text -- I grabbed 'The Raven' by E. A. Poe
* `./make_yaml.py --garbage-in raven.txt --garbage-out raven.yaml`
### Run bot in background
* `./main.py --local_server_port 34239 -b raven.yaml -o backup_brain.yaml -n raven &` 



