# Check the user-services for proper filenames, report broken ones
batocera-services list user | grep '\*$' | head -1
