#include "glyph.h"

#include "glyph_type.h"

#include <iostream>

Glyph::Glyph()
    : type(GlyphType::UNKNOWN), ftype(FunctionType::NONE), value(0) {}

Glyph::Glyph(GlyphType _type)
    : type(_type), ftype(FunctionType::NONE), value(0) {}

Glyph::Glyph(FunctionType _ftype)
    : type(GlyphType::FUNCTION), ftype(_ftype), value(0) {}

Glyph::Glyph(GlyphType _type, int64_t _value)
    : type(_type), ftype(FunctionType::NONE), value(_value) {}

void Glyph::Print() const {
  switch (type) {
    case GlyphType::NUMBER:
      std::cout << value;
      break;
    case GlyphType::ONE:
      std::cout << "I";
      break;
    case GlyphType::DOT:
      std::cout << ".";
      break;
    case GlyphType::EQUALITY:
      std::cout << "===";
      break;
    case GlyphType::OPERAND:
      std::cout << "^";
      break;
    case GlyphType::FUNCTION:
      std::cout << "F" << unsigned(ftype);
      break;
    case GlyphType::VARIABLE:
      std::cout << "V" << value;
      break;
    case GlyphType::BOOLEAN:
      std::cout << (value ? "TRUE" : "FALSE");
      break;
    default:
      std::cout << "UNKNOWN";
      break;
  }
}
