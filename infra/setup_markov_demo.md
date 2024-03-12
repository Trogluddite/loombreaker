# setup loombot user
```
sudo useradd -m loombot
sudo su - loombot
```
## create github deploy key
```
ssh-keygen -t ed25519 -C loombotdeploy@prototype-solr-scraper.com
cat ~/.ssh/id_ed25519.pub # copy this
```
then add the pubkey to the repo as a deploy key
[https://docs.github.com/en/authentication/connecting-to-github-with-ssh/managing-deploy-keys#deploy-keys](github tutorial)

# checkout the repo & create bot runtime directory
```
git checkout git@github.com:Trogluddite/loombreaker.git ~/loombreaker_git
mkdir ~/botRuntime
ln -s loombreaker_git/markov_demo/ botRuntime
```
# set up python runtime environment
## install pyenv
```
curl https://pyenv.run | bash
```
## edit ~/.bashrc
```
export PYENV_ROOT="$HOME/.pyenv"
[[ -d $PYENV_ROOT/bin ]] && export PATH="$PYENV_ROOT/bin:$PATH"
eval "$(pyenv init -)"
eval "($pyenv virtualenv-init -)"
```
## install late python version
note that this step requires developer C libraries to be installed so that you can compile python
see [https://github.com/pyenv/pyenv-virtualenv](Pyenv Install Notes) for details; they may be present already.

on debian based distros the necessary libs can be apt-get installed
```
pyenv install 3.12.2
```
make the new python version the default for this user
```
pyenv global 3.12.2
```
## create virtualenv
setting the virtualenv in `.python-version`, along with eval "$(pyenv virtualenv-init -)",
makes pyenv automatically activate/de-activate the virtualenv upon entering/leaving the directory
```
pyenv virtualenv botEnv
echo "botEnv" > ~/botRuntime/.python-version
```
# Configure and start the bot
## install requirements into virtualenv
```
cd ~/botRuntime
pip install -r requirements.txt
```
## add .env with discord token
ensure that there's a file called `.env` in ~/botRuntime
its contents should be:
```
TOKEN = <discord bot token>
```
## startup bot in screen
### connect to screen
```
screen -list #check for existing screen session
# if screen exists:
screen -r
# else
screen -S loomBot
```
### start it up
currently, startup initiates a query to SOLR and loads the top 10 returned docs into the live bayesian network
this is somewhat time consuming, so expect startup times of ~10 minutes
```
./discord_test.py
```
### detach from screen
press "ctrl+a", then release and type the letter "d"
if you're somehow in a nested screen session, use
`ctrl+a a d`
```
ctrl-a d
```
# deploy new bot code
as loombot user (`sudo su - loombot`)
## pull the code
```
cd ~/loombot_git
git pull
```
## attach to screen
```
screen -r
```
## stop running instance
```
ctrl+c
```
## start new instance
```
./discord_test.py
```
## detach from screen
```
ctrl+a d
```



