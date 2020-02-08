# include .bashrc if it exists
if [ -n "$BASH_VERSION" ]; then
        if [ -f "$HOME/.bashrc" ]; then
                . "$HOME/.bashrc"
        fi
fi
