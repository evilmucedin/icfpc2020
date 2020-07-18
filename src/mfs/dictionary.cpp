#include "dictionary.h"

#include "common/base.h"

#include <unordered_map>

namespace {
std::unordered_map<unsigned, Expression> dict;
}  // namespace

void AddToDictionary(unsigned index, const Expression& e) {
  auto it = dict.find(index);
  assert(it == dict.end());
  unsigned ats = 0;
  for (auto& g : e.v) {
    if (g.type == GlyphType::OPERAND) ++ats;
  }
  assert(e.v.size() == 2 * ats + 1);
  dict[index] = e;
}

const Expression& GetFromDictionary(unsigned index) {
  auto it = dict.find(index);
  assert(it != dict.end());
  return it->second;
}
