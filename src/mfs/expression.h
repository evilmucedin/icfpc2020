#pragma once

#include "glyph.h"

#include <vector>

class Expression {
 public:
  std::vector<Glyph> v;

  Expression();
  explicit Expression(const Glyph& g);
  explicit Expression(int64_t value);

  bool operator==(const Expression& r) const;

  bool IsNumber() const;
  int64_t GetNumber() const;

  void Add(const Glyph& g);
  void Add(const Expression& e);

  void Print() const;
};
