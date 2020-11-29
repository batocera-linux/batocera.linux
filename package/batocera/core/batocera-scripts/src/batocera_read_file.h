
#ifndef _BATOCERA_READ_FILE_H_
#define _BATOCERA_READ_FILE_H_

#include <stddef.h>

/* Reads the file. Exits on error. */
void batocera_read_file(const char *fname, char **out_data, size_t *out_size);

#endif  // _BATOCERA_READ_FILE_H_
