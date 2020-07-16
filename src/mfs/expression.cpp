#include "expression.h"

#include <iostream>

void Expression::Print() const {
  std::cout << "[";
  for (auto& g : v) {
    g.Print();
    std::cout << " ";
  }
  std::cout << "]";
}
