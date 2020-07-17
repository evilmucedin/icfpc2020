#pragma once

#include "line.h"

#include <unordered_map>
#include <vector>

class Message {
 public:
  std::vector<Line> v;
  std::unordered_map<unsigned, Expression> aliases;

  void Compress();
  void Process();
  void Print() const;
};
