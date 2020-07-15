#include "glyph.h"

Glyph::Glyph()
    : type(GlyphType::UNKNOWN), ftype(FunctionType::NONE), value(0) {}

Glyph::Glyph(GlyphType _type)
    : type(_type), ftype(FunctionType::NONE), value(0) {}

Glyph::Glyph(FunctionType _ftype)
    : type(GlyphType::FUNCTION), ftype(_ftype), value(0) {}

Glyph::Glyph(GlyphType _type, int64_t _value)
    : type(_type), ftype(FunctionType::NONE), value(_value) {}
