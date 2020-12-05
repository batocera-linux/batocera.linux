#ifndef _BATOCERA_ASCII_H_
#define _BATOCERA_ASCII_H_

// Returns a pointer to the first non-leading whitespace.
// Only ' ' and '\t' are considered whitespace.
// Requires: begin <= end.
static inline const char *skip_leading_whitespace(const char *begin, const char *end) {
  while (begin != end && (*begin == ' ' || *begin == '\t')) ++begin;
  return begin;
}

// Returns a pointer to the last non-whitespace.
// Only ' ' and '\t' are considered whitespace.
// Requires: begin <= end.
static inline const char *skip_trailing_whitespace(const char *begin,
                                            const char *end) {
  while (begin != end && (*(end - 1) == ' ' || *(end - 1) == '\t')) --end;
  return end;
}

#endif  // _BATOCERA_ASCII_H_
