#pragma once

#include "glyph.h"

#include <vector>

class Expression {
 public:
  std::vector<Glyph> v;

  Expression();
  explicit Expression(const Glyph& g);
  explicit Expression(int64_t value);

  bool Empty() const;
  bool operator==(const Expression& r) const;

  bool IsNumber() const;
  int64_t GetNumber() const;
  bool IsLEF() const;
  LEF GetLEF() const;
  bool IsList() const;

  void Add(const Glyph& g);
  void Add(const Expression& e);

  Expression GetOne(unsigned index, unsigned count = 1);
  void Compress();

  void Print() const;
};
