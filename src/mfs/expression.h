#pragma once

#include "glyph.h"

#include <vector>

class Expression {
 public:
  std::vector<Glyph> v;

  void Print() const;
};
