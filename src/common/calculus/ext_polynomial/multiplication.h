#pragma once

#include "common/base.h"
#include "common/calculus/ext_polynomial/function.h"
#include "common/calculus/ext_polynomial/term.h"

namespace calculus {
namespace ext_polynomial {
template <class TValueF, class TValueTerm, class TTerm>
inline Function<TValueF, TValueTerm, TTerm> MultiplicationTerms(
    const TTerm& l, const TTerm& r) {
  if (l.IsMultiplicable(r)) {
    return l * r;
  }
  assert(false);
  return {};
}

template <class TValueF, class TValueTerm, class TTerm>
inline Function<TValueF, TValueTerm, TTerm> operator*(
    const Function<TValueF, TValueTerm, TTerm>& f1,
    const Function<TValueF, TValueTerm, TTerm>& f2) {
  Function<TValueF, TValueTerm, TTerm> f;
  for (auto& t1 : f1.terms) {
    for (auto& t2 : f2.terms) {
      if (t1.IsMultiplicable(t2)) {
        f.AddTermUnsafe(t1 * t2);
      } else {
        f.AddTermsUnsafe(
            MultiplicationTerms<TValueF, TValueTerm, TTerm>(t1, t2));
      }
    }
  }
  f.Compress();
  return f;
}

template <class TValueF, class TValueTerm, class TTerm>
inline Function<TValueF, TValueTerm, TTerm> operator*(
    const Function<TValueF, TValueTerm, TTerm>& f1, const TTerm& t2) {
  return f1 * Function<TValueF, TValueTerm, TTerm>(t2);
}

template <class TValueF, class TValueTerm, class TTerm>
inline Function<TValueF, TValueTerm, TTerm> operator*(
    const TTerm& t1, const Function<TValueF, TValueTerm, TTerm>& f2) {
  return Function<TValueF, TValueTerm, TTerm>(t1) * f2;
}

template <class TValueF, class TValueTerm, class TTerm>
inline Function<TValueF, TValueTerm, TTerm>& operator*=(
    Function<TValueF, TValueTerm, TTerm>& f1, const TTerm& t2) {
  return f1 = (f1 * t2);
}

template <class TValueF, class TValueTerm, class TTerm>
inline Function<TValueF, TValueTerm, TTerm>& operator*=(
    Function<TValueF, TValueTerm, TTerm>& f1,
    const Function<TValueF, TValueTerm, TTerm>& f2) {
  return f1 = (f1 * f2);
}
}  // namespace ext_polynomial
}  // namespace calculus
