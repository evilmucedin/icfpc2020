#pragma once

#include "function_type.h"
#include "glyph_type.h"

#include "common/base.h"

class Glyph {
 public:
  GlyphType type;
  FunctionType ftype;
  int64_t value;

  Glyph();
  Glyph(GlyphType _type);
  Glyph(FunctionType _ftype);
  Glyph(GlyphType _type, int64_t _value);
};
