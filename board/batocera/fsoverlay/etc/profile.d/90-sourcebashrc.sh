if ! [ -f $HOME/.profile ] && ! [ -f $HOME/.bash_profile ]; then
  [ -f $HOME/.bashrc ] && . $HOME/.bashrc
fi
