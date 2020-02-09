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
echo

# ---- ALIAS VALUES ----
alias mc='mc -x'
alias ls='ls -a'


# Include .bashrc if it exists (for user values)
if [ -n "$BASH_VERSION" ]; then
	# include .bashrc if it exists
	if [ -f "$HOME/.bashrc" ]; then
		. "$HOME/.bashrc"
	fi
fi
