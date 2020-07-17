#include "message.h"

#include <iostream>

void Message::Compress() {
  for (auto& l : v) l.Compress();
}

void Message::Print() const {
  for (auto& l : v) l.Print();
}
