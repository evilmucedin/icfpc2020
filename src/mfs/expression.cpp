#include "expression.h"

#include "glyph.h"
#include "glyph_type.h"

#include "common/base.h"

#include <iostream>

Expression::Expression() {}

Expression::Expression(const Glyph& g) { v.push_back(g); }

Expression::Expression(int64_t value) {
  v.push_back(Glyph(GlyphType::NUMBER, value));
}

bool Expression::operator==(const Expression& r) const { return v == r.v; }

void Expression::Add(const Glyph& g) { v.push_back(g); }

void Expression::Add(const Expression& e) {
  v.insert(v.end(), e.v.begin(), e.v.end());
}

bool Expression::IsNumber() const {
  return (v.size() == 1) && (v[0].type == GlyphType::NUMBER);
}

int64_t Expression::GetNumber() const {
  assert(IsNumber());
  return v[0].value;
}

bool Expression::IsLEF() const {
  return (v.size() == 1) && (v[0].type == GlyphType::LINEAR_ENCODED_FORM);
}

LEF Expression::GetLEF() const {
  assert(IsLEF());
  return v[0].lef;
}

bool Expression::IsList() const {
  if (v.size() == 1) {
    return v[0].ftype == FunctionType::NIL__EMPTY_LIST;
  } else if (v.size() >= 4) {
    if ((v[0].type == GlyphType::OPERAND) &&
        (v[1].type == GlyphType::OPERAND) &&
        (v[2].ftype == FunctionType::CONS__PAIR) &&
        (v.back().ftype == FunctionType::NIL__EMPTY_LIST)) {
      // probably list, more complex check required
      return true;
    }
  }
  return false;
}

void Expression::Print() const {
  std::cout << "[";
  for (auto& g : v) {
    g.Print();
    std::cout << " ";
  }
  std::cout << "]";
}
