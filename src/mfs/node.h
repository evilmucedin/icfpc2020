#pragma once

#include "glyph.h"

#include "common/node.h"

class Node : public BaseNode {
 public:
  Glyph data;
  Node *l, *r;

  void ApplyAction() {}
};

Node* NewNode(const Glyph& g);
