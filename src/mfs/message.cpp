#include "message.h"

#include <iostream>

void Message::Print() const {
  for (auto& l : v) l.Print();
}
