#include "linear_encoded_form.h"

#include "common/base.h"

LEF LEFEncodeNumber(int64_t value) {
  int64_t avalue = (value < 0) ? -value : value;
  unsigned l = 0;
  for (; (1ll << (4 * l)) <= avalue;) ++l;
  LEF v(2 + (l + 1) + 4 * l);
  v.Set((value < 0) ? 0 : 1, 1);
  for (unsigned i = 0; i < l; ++i) v.Set(i + 2, 1);
  unsigned k = l + 2;
  for (unsigned i = 0; i < 4 * l; ++i) {
    if (avalue & (1ll << i)) v.Set(k + 4 * l - i, 1);
  }
  return v;
}

int64_t LEFDecodeNumber(const LEF& lef) {
  assert(lef.Get(0) != lef.Get(1));
  int64_t sign = lef.Get(0) ? -1 : 1;
  unsigned l = lef.Size() / 5, k = l + 2;
  assert(lef.Size() == 5 * l + 3);
  for (unsigned i = 0; i < l; ++i) {
    assert(lef.Get(i + 2));
  }
  assert(!lef.Get(l + 2));
  int64_t value = 0;
  for (unsigned i = 0; i < 4 * l; ++i) {
    if (lef.Get(k + 4 * l - i)) value += (1ll << i);
  }
  return sign * value;
}
