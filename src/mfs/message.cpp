#include "message.h"

#include "common/base.h"
#include "common/data_structures/unsigned_set.h"

#include <algorithm>
#include <iostream>

void Message::Compress() {
  for (auto& l : v) l.Compress();
}

void Message::Process() {
  ds::UnsignedSet us(v.size());
  for (unsigned i = 0; i < v.size(); ++i) {
    assert(v[i].v.size() == 1);
    assert(v[i].v[0].v.size() >= 3);
    assert(v[i].v[0].v[1].type == GlyphType::EQUALITY);
    if (v[i].v[0].v[0].type == GlyphType::ALIAS) us.Insert(i);
  }

  for (bool next = true; next;) {
    next = false;
    auto rows = us.List();
    for (auto row : rows) {
      const auto& l = v[row].v[0];
      Expression e;
      bool good = true;
      for (unsigned i = 2; i < l.v.size(); ++i) {
        if (l.v[i].type == GlyphType::ALIAS) {
          auto it = aliases.find(l.v[i].value);
          if (it == aliases.end()) {
            good = false;
            break;
          } else {
            e.Add(it->second);
          }
        } else {
          e.Add(l.v[i]);
        }
      }
      if (good) {
        std::cout << "Processing line " << row << std::endl;
        l.Print();
        std::cout << std::endl;
        e.Print();
        std::cout << std::endl;
        e.Compress();
        e.Print();
        std::cout << std::endl;
        aliases[l.v[0].value] = e;
        us.Remove(row);
        next = true;
      }
    }
  }

  std::cout << std::endl << "Lines left: " << us.Size() << std::endl;
  auto rows = us.List();
  std::sort(rows.begin(), rows.end());
  for (unsigned row : rows) {
    const auto& l = v[row].v[0];
    l.Print();
    std::cout << std::endl;
    Expression e;
    for (unsigned i = 2; i < l.v.size(); ++i) {
      if (l.v[i].type == GlyphType::ALIAS) {
        auto it = aliases.find(l.v[i].value);
        if (it == aliases.end()) {
          e.Add(l.v[i]);
        } else {
          e.Add(it->second);
        }
      } else {
        e.Add(l.v[i]);
      }
    }
    e.Print();
    std::cout << std::endl;
  }
  // for (auto& l : v) {
  //   l.Print();
  //   l.Compress();
  //   l.Print();
  //   std::cout << std::endl;
  // }
}

void Message::Print() const {
  for (auto& l : v) l.Print();
}
