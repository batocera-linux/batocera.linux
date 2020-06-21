# Set vt100 as terminal enviroment
TERM=vt100

# Add BATOCERA logo and some alias, sourcing of $HOME/.bashrc can be added to $HOME/.profile
echo '
      ____    __   ____  _____  ___  ____  ____    __   
     (  _ \  /__\ (_  _)(  _  )/ __)( ___)(  _ \  /__\  
      ) _ < /(__)\  )(   )(_)(( (__  )__)  )   / /(__)\ 
     (____/(__)(__)(__) (_____)\___)(____)(_)\_)(__)(__)
                   ONLY CORES THAT MATTER
'
echo
echo "-- type 'batocera-check-updates' to check for stable branch --"
echo "-- add 'beta' switch to check for latest arch developments  --"
echo
batocera-info 2>/dev/null
echo "OS version: $(cat /usr/share/batocera/batocera.version)"
echo

# ---- ALIAS VALUES ----
alias mc='mc -x'
alias batocera-check-updates='batocera-es-swissknife --update'
