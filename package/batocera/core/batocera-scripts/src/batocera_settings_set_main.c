#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "batocera_read_file.h"
#include "batocera_settings_set.h"

static const char kUsage[] =
    "Usage: batocera-settings-set [-f CONFIG_FILE] <KEY> <VALUE> [KEY "
    "VALUE]...\n\n"
    "Sets value(s) in the config file.\n"
    "If a commented key exists, will uncomment it and set the value in-place"
    " instead of appending a new key\n\n"
    "By default, writes to /userdata/system/batocera.conf\n";

int main(int argc, char *argv[]) {
  if (argc < 2 || strcmp(argv[1], "--help") == 0) {
    fwrite(kUsage, sizeof(char), sizeof(kUsage), stderr);
    return EXIT_FAILURE;
  }
  size_t kvs_size = argc - 1;
  const char **kvs = (const char **)argv + 1;
  const char *config_path = "/userdata/system/batocera.conf";
  if (argv[1][0] == '-' && argv[1][1] == 'f') {
    if (argc < 3) {
      const char message[] = "-f requires an argument\n";
      fwrite(message, sizeof(char), sizeof(message), stderr);
      return EXIT_FAILURE;
    }
    config_path = argv[2];
    kvs += 2;
    kvs_size -= 2;
  }

  if (kvs_size == 0) {
    const char message[] = "-f requires an argument\n";
    fwrite(message, sizeof(char), sizeof(message), stderr);
    return EXIT_FAILURE;
  }

  if (kvs_size % 2 != 0) {
    const char message[] = "the number of key-value arguments must be even\n";
    fwrite(message, sizeof(char), sizeof(message), stderr);
    return EXIT_FAILURE;
  }

  char *config_contents;
  size_t config_contents_size;
  batocera_read_file(config_path, &config_contents, &config_contents_size);

  struct batocera_settings_set_result_t result = batocera_settings_set(
      config_contents, config_contents_size, kvs, kvs_size);
  if (result.error != NULL) {
    fwrite(result.error, sizeof(char), result.error_size, stderr);
    free(result.error);
    goto set_failed;
  }

  FILE *config_file = fopen(config_path, "w");
  if (config_file == NULL) {
    perror(config_path);
    goto set_failed;
  }
  fwrite(result.contents, sizeof(char), result.contents_size, config_file);
  if (ferror(config_file)) {
    perror("write error");
    goto set_failed;
  }
  fclose(config_file);

  free(result.contents);
  free(config_contents);
  return EXIT_SUCCESS;

set_failed:
  free(result.contents);
  free(config_contents);
  return EXIT_FAILURE;
}
