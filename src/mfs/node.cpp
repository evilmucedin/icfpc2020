#include "node.h"

#include "common/nodes_manager.h"

namespace {
NodesManager<Node> manager(1000);
}

Node* NewNode(const Glyph& g) {
  auto node = manager.New();
  node->data = g;
  node->l = node->r = nullptr;
  return node;
}
