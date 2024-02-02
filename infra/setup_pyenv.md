# setup pyenv on prototype-solr-scrraper

# system preliminaries
sudo su - root
apt update -y
apt install build-essential libssl-dev zlib1g-dev \
libbz2-dev libreadline-dev libsqlite3-dev curl \
libncursesw5-dev xz-utils tk-dev libxml2-dev libxmlsec1-dev libffi-dev liblzma-dev
exit

# per user
curl https://pyenv.run | bash
# edit ~/.bashrc, append: 
```
export PYENV_ROOT="$HOME/.pyenv"
command -v pyenv >/dev/null || export PATH="$PYENV_ROOT/bin:$PATH"
eval "$(pyenv init -)"
eval "$(pyenv virtualenv-init -)"
```
source ~/.bashrc
pyenv install 3.11.7
mkdir ~/markov_demo
pyenv local markov_demo
source ~/.bashrc 

# now, cd to ~/markov_demo will activate the virtualenv

