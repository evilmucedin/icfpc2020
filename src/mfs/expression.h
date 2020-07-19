#pragma once

#include "glyph.h"
#include "node.h"

#include <vector>

class Expression {
 public:
  std::vector<Glyph> v;
  Node* root = nullptr;

  Expression();
  explicit Expression(const Glyph& g);

 protected:
  Node* MakeNodeI(unsigned& index);

 public:
  void Add(const Glyph& g);
  Node* MakeRoot();
  void MakeVector();
  void Evaluate();
  void Print() const;

  // Expression should be evaluated
  static bool IsList(Node* node);

  bool operator==(const Expression& r) const;
};
