#include "expression.h"

#include "evaluation.h"
#include "glyph.h"
#include "glyph_decoder.h"
#include "glyph_type.h"

#include "common/base.h"
#include "common/binary_search_tree/base/right.h"

#include <iostream>
#include <vector>

namespace {
void PrintI(Node* node, GlyphDecoder& gd);

void MakeVectorI(Node* node, std::vector<Glyph>& v) {
  assert(node);
  v.push_back(node->data);
  if (node->data.type == GlyphType::UP) {
    MakeVectorI(node->l, v);
    MakeVectorI(node->r, v);
  }
}

void PrintListI(Node* node, bool first, GlyphDecoder& gd) {
  if ((node->data.type == GlyphType::FUNCTION) &&
      (node->data.ftype == FunctionType::NIL__EMPTY_LIST)) {
    std::cout << (first ? "( " : "") << ") ";
  } else {
    std::cout << (first ? "(" : ", ");
    assert(node->data.type == GlyphType::UP);
    assert(node->l->data.type == GlyphType::UP);
    assert((node->l->l->data.type == GlyphType::FUNCTION) &&
           (node->l->l->data.ftype == FunctionType::CONS__PAIR));
    PrintI(node->l->r, gd);
    PrintListI(node->r, false, gd);
  }
}

void PrintI(Node* node, GlyphDecoder& gd) {
  assert(node);
  if (Expression::IsList(node)) {
    PrintListI(node, true, gd);
  } else {
    std::cout << gd.ToString(node->data) << " ";
    if (node->data.type == GlyphType::UP) {
      PrintI(node->l, gd);
      PrintI(node->r, gd);
    }
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
  PrintI(root, gd);
}

bool Expression::IsList(Node* node) {
  assert(node);
  if ((node->data.type == GlyphType::FUNCTION) &&
      (node->data.ftype == FunctionType::NIL__EMPTY_LIST))
    return true;
  if (node->data.type != GlyphType::UP) return false;
  if (node->l->data.type != GlyphType::UP) return false;
  auto l = node->l->l;
  auto r = bst::base::Right(node);
  return ((r->data.type == GlyphType::FUNCTION) &&
          (r->data.ftype == FunctionType::NIL__EMPTY_LIST) &&
          (l->data.type == GlyphType::FUNCTION) &&
          (l->data.ftype == FunctionType::CONS__PAIR));
}

bool Expression::operator==(const Expression& r) const { return v == r.v; }
