#Trim path 30chars
#https://askubuntu.com/questions/17723/trim-the-terminal-command-prompt-working-directory
#Showing full path in terminal window
#https://wiki.archlinux.org/title/Bash/Prompt_customization
#looks like: [root@BATOCERA /userdata/…backup/bato_scripts]#
if test -n $PS1; then
    PS1='\[\e]2;BATOCERA - $PWD\a\][\u@\h $(p=${PWD/#"$HOME"/~};((${#p}>30))&&echo "${p::10}…${p:(-19)}"||echo "\w")]\$ '
fi
