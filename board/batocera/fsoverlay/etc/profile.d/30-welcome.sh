# Add BATOCERA logo and some alias, sourcing of $HOME/.bashrc can be added to $HOME/.profile
echo '
      ____    __   ____  _____  ___  ____  ____    __   
     (  _ \  /__\ (_  _)(  _  )/ __)( ___)(  _ \  /__\  
      ) _ < /(__)\  )(   )(_)(( (__  )__)  )   / /(__)\ 
     (____/(__)(__)(__) (_____)\___)(____)(_)\_)(__)(__)
                 R E A D Y   T O   R E T R O
'
echo
echo "-- type 'batocera-check-updates' to check for stable branch --"
echo "-- add 'butterfly' switch to check for latest arch developments  --"
echo
batocera-info 2>/dev/null
echo "OS version: $(batocera-version)"
echo
