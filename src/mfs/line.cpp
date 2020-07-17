#include "line.h"

#include <iostream>

void Line::Compress() {
  for (auto& e : v) e.Compress();
}

void Line::Print() const {
  for (auto& e : v) {
    e.Print();
    std::cout << "  ";
  }
  std::cout << std::endl;
}
