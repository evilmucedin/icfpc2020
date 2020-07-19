#include "expression.h"

#include "evaluation.h"
#include "glyph.h"
#include "glyph_decoder.h"
#include "glyph_type.h"

#include "common/base.h"

#include <iostream>
#include <vector>

namespace {
void MakeVectorI(Node* node, std::vector<Glyph>& v) {
  assert(node);
  v.push_back(node->data);
  if (node->data.type == GlyphType::UP) {
    MakeVectorI(node->l, v);
    MakeVectorI(node->r, v);
  }
}
};  // namespace

Expression::Expression() {}

Node* Expression::MakeNodeI(unsigned& index) {
  assert(index < v.size());
  Node* node = NewNode(v[index++]);
  if (node->data.type == GlyphType::UP) {
    node->l = MakeNodeI(index);
    node->r = MakeNodeI(index);
  }
  return node;
}

void Expression::Add(const Glyph& g) {
  assert(!root);
  v.push_back(g);
}

Node* Expression::MakeRoot() {
  unsigned index = 0;
  root = MakeNodeI(index);
  assert(index == v.size());
  return root;
}

void Expression::MakeVector() {
  v.clear();
  MakeVectorI(root, v);
}

void Expression::Evaluate() {
  if (!root) MakeRoot();
  ::Evaluate(root);
  MakeVector();
}

void Expression::Print() const {
  auto& gd = GlyphDecoder::GetDecoder();
  std::cout << "[";
  for (auto& g : v) {
    // g.Print();
    // std::cout << " ";
    std::cout << gd.ToString(g) << " ";
  }
  std::cout << "]";
}

bool Expression::operator==(const Expression& r) const { return v == r.v; }
