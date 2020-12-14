#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "batocera_read_file.h"
#include "batocera_settings_get.h"

static const char kUsage[] =
    "Usage: batocera-settings-get [-f CONFIG_FILE] <KEY> [KEY]...\n\n"
    "Prints the value of the key or returns a non-zero exit status.\n"
    "If multiple keys are given, tries them in order until it finds a key"
    " that exists.\n\n"
    "By default, reads from /userdata/system/batocera.conf\n";

int main(int argc, char *argv[]) {
  if (argc < 2 || strcmp(argv[1], "--help") == 0) {
    fwrite(kUsage, sizeof(char), sizeof(kUsage), stderr);
    return EXIT_FAILURE;
  }
  size_t num_keys = argc - 1;
  const char **keys = (const char **)argv + 1;
  const char *config_path = "/userdata/system/batocera.conf";
  if (argv[1][0] == '-' && argv[1][1] == 'f') {
    if (argc < 3) {
      const char message[] = "-f requires an argument\n";
      fwrite(message, sizeof(char), sizeof(message), stderr);
      return EXIT_FAILURE;
    }
    config_path = argv[2];
    keys += 2;
    num_keys -= 2;
  }

  if (num_keys == 0) {
    const char message[] = "at least 1 key argument is required\n";
    fwrite(message, sizeof(char), sizeof(message), stderr);
    return EXIT_FAILURE;
  }

  char *config_contents;
  size_t config_contents_size;
  batocera_read_file(config_path, &config_contents, &config_contents_size);

  struct batocera_settings_get_result_t result = batocera_settings_get(
      config_contents, config_contents_size, keys, num_keys);
  if (result.error != NULL) {
    fwrite(result.error, sizeof(char), result.error_size, stderr);
    free(result.error);
    goto get_failed;
  } else if (result.value == NULL) {
    // Key not found.
    goto get_failed;
  }

  fwrite(result.value, sizeof(char), result.value_size, stdout);
  fputc('\n', stdout);
  if (ferror(stdout)) goto get_failed;

  free(config_contents);
  return EXIT_SUCCESS;

get_failed:
  free(config_contents);
  return EXIT_FAILURE;
}
