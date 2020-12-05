#include "batocera_read_file.h"

#include <stdio.h>
#include <stdlib.h>

void batocera_read_file(const char *fname, char **out_data, size_t *out_size) {
  FILE *f = fopen(fname, "rb");

  if (f == NULL) {
    perror(fname);
    exit(EXIT_FAILURE);
  }

  fseek(f, 0, SEEK_END);
  long fsize = ftell(f);
  fseek(f, 0, SEEK_SET);

  char *data = malloc(fsize + 1);
  if (fread(data, fsize, 1, f) != 1 && ferror(f)) {
    perror(fname);
    exit(1);
  }
  fclose(f);
  data[fsize] = 0;

  *out_data = data;
  *out_size = fsize;
}
