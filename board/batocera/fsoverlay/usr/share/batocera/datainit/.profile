# ---- Introduce BATOCERA logo ----
echo '
 ____    __   ____  _____  ___  ____  ____    __   
(  _ \  /__\ (_  _)(  _  )/ __)( ___)(  _ \  /__\  
 ) _ < /(__)\  )(   )(_)(( (__  )__)  )   / /(__)\ 
(____/(__)(__)(__) (_____)\___)(____)(_)\_)(__)(__)
              ONLY CORES THAT MATTER
'
echo
echo "BATOCERA Version: $(batocera-es-swissknife --version)"
echo "BATOCERA Architecture: $(batocera-es-swissknife --arch)"
echo "-- type 'batocera-check-stable' or 'batocera-check-beta' --"
echo "-- to check for updates for your platform (stable/beta)  --"
echo

# ---- ALIAS VALUES ----
alias mc='mc -x'
alias ls='ls -a'
alias batocera-check-stable='batocera-es-swissknife --update'
alias batocera-check-beta='batocera-es-swissknife --update beta'

# Include .bashrc if it exists (for user values)
if [ -n "$BASH_VERSION" ]; then
	if [ -f "$HOME/.bashrc" ]; then
		. "$HOME/.bashrc"
	fi
fi
