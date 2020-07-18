#include "expression.h"

#include "dictionary.h"
#include "function.h"
#include "glyph.h"
#include "glyph_type.h"

#include "common/base.h"

#include <iostream>

Expression::Expression() {}

Expression::Expression(const Glyph& g) { v.push_back(g); }

Expression::Expression(int64_t value) {
  v.push_back(Glyph(GlyphType::NUMBER, value));
}

bool Expression::Empty() const { return v.empty(); }

bool Expression::operator==(const Expression& r) const { return v == r.v; }

void Expression::Add(const Glyph& g) { v.push_back(g); }

void Expression::Add(const Expression& e) {
  v.insert(v.end(), e.v.begin(), e.v.end());
}

bool Expression::IsNumber() const {
  return (v.size() == 1) && (v[0].type == GlyphType::NUMBER);
}

int64_t Expression::GetNumber() const {
  assert(IsNumber());
  return v[0].value;
}

bool Expression::IsLEF() const {
  return (v.size() == 1) && (v[0].type == GlyphType::LINEAR_ENCODED_FORM);
}

LEF Expression::GetLEF() const {
  assert(IsLEF());
  return v[0].lef;
}

bool Expression::IsList() const {
  if (v.size() == 0) return false;
  if ((v.size() == 1) && (v[0].ftype == FunctionType::NIL__EMPTY_LIST))
    return true;
  if ((v.size() > 3) && (v[0].type == GlyphType::OPERAND) &&
      (v[1].type == GlyphType::OPERAND) &&
      ((v[2].ftype == FunctionType::CONS__PAIR) ||
       (v[2].ftype == FunctionType::VECTOR)))
    return true;
  return false;
  //   for (unsigned i = 0; i < v.size(); i += 4) {
  //     if ((v[i].ftype == FunctionType::NIL__EMPTY_LIST) && (v.size() == i +
  //     1))
  //       return true;
  //     if (v.size() <= i + 4) return false;
  //     if ((v[i].type != GlyphType::OPERAND) ||
  //         (v[i + 1].type != GlyphType::OPERAND) ||
  //         (v[i + 2].ftype != FunctionType::CONS__PAIR) ||
  //         (v[i + 3].type == GlyphType::OPERAND))
  //       return false;
  //   }
  //   return false;
}

void Expression::ReplaceAlias(unsigned index) {
  assert(v[index].type == GlyphType::ALIAS);
  unsigned a = v[index].value;
  v.erase(v.begin() + index);
  auto e = GetFromDictionary(a);
  v.insert(v.begin() + index, e.v.begin(), e.v.end());
}

Expression Expression::GetOne(unsigned index, unsigned count) {
  Expression e;
  for (; count && (index < v.size()); ++index) {
    // if (v[index].type == GlyphType::ALIAS) {
    //   ReplaceAlias(index--);
    //   continue;
    // } else
    if (v[index].type == GlyphType::OPERAND) {
      ++count;
    } else {
      --count;
    }
    e.Add(v[index]);
  }
  assert(!count);
  return e;
}

bool Expression::EvaluateOnce() {
  for (unsigned i0 = 0; i0 < v.size();) {
    if (v[i0].type == GlyphType::ALIAS) {
      ReplaceAlias(i0);
      return true;
    } else if (v[i0].type != GlyphType::OPERAND) {
      ++i0;
      continue;
    } else {
      unsigned i1 = i0 + 1;
      for (; i1 < v.size();) {
        if (v[i1].type == GlyphType::ALIAS) {
          ReplaceAlias(i1);
          return true;
        } else if (v[i1].type != GlyphType::OPERAND) {
          break;
        } else {
          ++i1;
        }
      }
      assert(v[i1].type == GlyphType::FUNCTION);
      unsigned l = ExpectedParameters(v[i1].ftype), i2 = i1 + 1;
      if (i1 - i0 >= l) {
        std::vector<Expression> ve;
        for (; ve.size() < l; i2 += ve.back().v.size())
          ve.push_back(GetOne(i2));
        auto e = ::Evaluate(v[i1].ftype, ve);
        assert(!e.Empty());
        v.erase(v.begin() + i1 - l, v.begin() + i2);
        v.insert(v.begin() + i1 - l, e.v.begin(), e.v.end());
        return true;
      } else {
        i0 = i1;
      }
    }
  }
  return false;
}

void Expression::Evaluate() {
  for (unsigned i0 = 0; i0 < v.size();) {
    if (v[i0].type == GlyphType::ALIAS) {
      ReplaceAlias(i0);
      continue;
    } else if (v[i0].type != GlyphType::OPERAND) {
      ++i0;
      continue;
    } else {
      unsigned i1 = i0 + 1;
      for (; i1 < v.size();) {
        if (v[i1].type == GlyphType::ALIAS) {
          ReplaceAlias(i1);
          continue;
        } else if (v[i1].type != GlyphType::OPERAND) {
          break;
        } else {
          ++i1;
        }
      }
      assert(v[i1].type == GlyphType::FUNCTION);
      unsigned l = ExpectedParameters(v[i1].ftype), i2 = i1 + 1;
      if (i1 - i0 >= l) {
        std::vector<Expression> ve;
        for (; ve.size() < l; i2 += ve.back().v.size())
          ve.push_back(GetOne(i2));
        auto e = ::Evaluate(v[i1].ftype, ve);
        assert(!e.Empty());
        v.erase(v.begin() + i1 - l, v.begin() + i2);
        v.insert(v.begin() + i1 - l, e.v.begin(), e.v.end());
      } else {
        i0 = i1;
      }
    }
  }
}

// Greedy and slow version
void Expression::Compress() {
  //   for (bool next = true; next;) {
  //     next = false;
  //     unsigned operands = 0, index = 0;
  //     for (; !next && (index < v.size()); ++index) {
  //       switch (v[index].type) {
  //         case GlyphType::OPERAND:
  //           ++operands;
  //           break;
  //         case GlyphType::FUNCTION:
  //           if (ExpectedParameters(v[index].ftype) <= operands) {
  //             std::vector<Expression> ve;
  //             unsigned index1 = index + 1, l =
  //             ExpectedParameters(v[index].ftype); for (; ve.size() < l;
  //             index1 += ve.back().v.size())
  //               ve.push_back(GetOne(index1));
  //             auto e = Apply(v[index].ftype, ve);
  //             if (!e.Empty()) {
  //               // Success
  //               next = true;
  //               v.erase(v.begin() + index - l, v.begin() + index1);
  //               v.insert(v.begin() + index - l, e.v.begin(), e.v.end());
  //               break;
  //             }
  //           }
  //           operands = 0;
  //           break;
  //         default:
  //           break;
  //       }
  //     }
  //   }
}

void Expression::Print() const {
  std::cout << "[";
  for (auto& g : v) {
    g.Print();
    std::cout << " ";
  }
  std::cout << "]";
}
