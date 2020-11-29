#ifndef _BATOCERA_STRINGBUF_H_
#define _BATOCERA_STRINGBUF_H_

#include <stddef.h>

struct batocera_stringbuf {
  char *data;
  size_t size;
  size_t capacity;
};

void batocera_stringbuf_init(struct batocera_stringbuf *buf, size_t capacity);

void batocera_stringbuf_append(struct batocera_stringbuf *buf, const char *str,
                               size_t size);

void batocera_stringbuf_append_line(struct batocera_stringbuf *buf,
                                    const char *str, size_t size);

void batocera_stringbuf_append_char(struct batocera_stringbuf *buf, char c);

#endif  // _BATOCERA_STRINGBUF_H_
