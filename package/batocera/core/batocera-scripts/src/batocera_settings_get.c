#include "batocera_settings_get.h"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "batocera_ascii.h"

static struct batocera_settings_get_result_t batocera_settings_get_one(
    const char *config_contents, size_t config_size, const char *key,
    size_t key_size) {
  struct batocera_settings_get_result_t result;
  memset(&result, 0, sizeof(result));

  const char *eof = config_contents + config_size;
  const char *line_end = config_contents - 1;
  size_t line_num = 0;
  while (line_end < eof) {
    ++line_num;
    const char *line_begin = line_end + 1;
    line_end = memchr(line_begin, '\n', eof - line_begin);
    if (line_end == NULL) line_end = eof;

    const char *key_begin = skip_leading_whitespace(line_begin, line_end);
    if (key_begin == line_end || *key_begin == '#') continue;

    const char *eq_pos = memchr(key_begin, '=', line_end - key_begin);
    if (eq_pos == NULL) {
      const size_t err_size = 128 + (line_end - line_begin);
      result.error = malloc(err_size);
      result.error_size =
          snprintf(result.error, err_size,
                   "Invalid config file: key '%.*s' has no value on line %zu",
                   (int)(line_end - line_begin), line_begin, line_num);
      return result;
    }
    const char *key_end = skip_trailing_whitespace(key_begin, eq_pos);

    if (key_end - key_begin != key_size ||
        memcmp(key_begin, key, key_size) != 0)
      continue;
    result.key = key_begin;
    result.key_size = key_size;

    const char *value_begin = skip_leading_whitespace(eq_pos + 1, line_end);
    const char *value_end = line_end;
    if (value_end > value_begin && (*(value_end - 1) == '\r')) --value_end;

    result.value = value_begin;
    result.value_size = value_end - value_begin;
    break;  // returns the first found key
  }
  return result;
}

struct batocera_settings_get_result_t batocera_settings_get(
    const char *config_contents, size_t config_size, const char *keys[],
    size_t keys_size) {
  for (size_t i = 0; i < keys_size; ++i) {
    const char *key = keys[i];
    const size_t key_size = strlen(keys[i]);
    struct batocera_settings_get_result_t result =
        batocera_settings_get_one(config_contents, config_size, key, key_size);
    if (result.value != NULL) return result;
  }

  struct batocera_settings_get_result_t result;
  memset(&result, 0, sizeof(result));
  return result;
}
