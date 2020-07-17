#include "function.h"

#include "function_type.h"

#include "common/base.h"

unsigned ExpectedParameters(FunctionType ftype) {
  switch (ftype) {
    case FunctionType::SUCCESSOR:
    case FunctionType::PREDECESSOR:
    case FunctionType::MODULATE:
    case FunctionType::DEMODULATE:
    case FunctionType::SEND:
    case FunctionType::NEGATE:
    case FunctionType::POWER_OF_TWO:
    case FunctionType::I_COMBINATOR:
    case FunctionType::CAR__FIRST:
    case FunctionType::CDR__TAIL:
    case FunctionType::NIL__EMPTY_LIST:
      return 1;
    case FunctionType::SUM:
    case FunctionType::PRODUCT:
    case FunctionType::DIVISION:
    case FunctionType::EQUALITY:
    case FunctionType::STRICT_LESS:
    case FunctionType::K_COMBINATOR:
    case FunctionType::FALSE__SECOND:
      return 2;
    case FunctionType::S_COMBINATOR:
    case FunctionType::C_COMBINATOR:
    case FunctionType::B_COMBINATOR:
    case FunctionType::CONS__PAIR:
      return 3;
    default:
      return unsigned(-1);
  }
}

Expression Apply(FunctionType ftype) {
  assert(ExpectedParameters(ftype) == 0);
  assert(false);
  return {};
}

Expression Apply(FunctionType ftype, Expression& e0) {
  assert(ExpectedParameters(ftype) == 1);
  Expression e;
  switch (ftype) {
    case FunctionType::SUCCESSOR:
      return e0.IsNumber() ? Expression(e0.GetNumber() + 1) : Expression();
    case FunctionType::PREDECESSOR:
      return e0.IsNumber() ? Expression(e0.GetNumber() - 1) : Expression();
    case FunctionType::MODULATE:
    case FunctionType::DEMODULATE:
    case FunctionType::SEND:
      return {};
    case FunctionType::NEGATE:
      return e0.IsNumber() ? Expression(-e0.GetNumber()) : Expression();
    case FunctionType::POWER_OF_TWO:
      if (e0.IsNumber()) {
        int64_t v = e0.GetNumber();
        assert(v >= 0);
        return Expression((1ll << v));
      }
      return {};
    case FunctionType::I_COMBINATOR:
      return e0;
    case FunctionType::CAR__FIRST:
      e.Add(Glyph(GlyphType::OPERAND));
      e.Add(e0);
      e.Add(Glyph(FunctionType::K_COMBINATOR));
      return e;
    case FunctionType::CDR__TAIL:
      e.Add(Glyph(GlyphType::OPERAND));
      e.Add(e0);
      e.Add(Glyph(FunctionType::FALSE__SECOND));
      return e;
    case FunctionType::NIL__EMPTY_LIST:
      return Expression(Glyph(FunctionType::K_COMBINATOR));
    default:
      assert(false);
  }
  return {};
}

Expression Apply(FunctionType ftype, Expression& e0, Expression& e1) {
  assert(ExpectedParameters(ftype) == 2);
  switch (ftype) {
    case FunctionType::SUM:
      return (e0.IsNumber() && e1.IsNumber())
                 ? Expression(e0.GetNumber() + e1.GetNumber())
                 : Expression();
    case FunctionType::PRODUCT:
      return (e0.IsNumber() && e1.IsNumber())
                 ? Expression(e0.GetNumber() * e1.GetNumber())
                 : Expression();
    case FunctionType::DIVISION:
      return (e0.IsNumber() && e1.IsNumber())
                 ? Expression(e0.GetNumber() / e1.GetNumber())
                 : Expression();
    case FunctionType::EQUALITY:
      if (e0.IsNumber() && e1.IsNumber())
        return Expression(Glyph((e0.GetNumber() == e1.GetNumber())
                                    ? FunctionType::K_COMBINATOR
                                    : FunctionType::FALSE__SECOND));
      return (e0 == e1) ? Expression(Glyph(FunctionType::K_COMBINATOR))
                        : Expression();
    case FunctionType::STRICT_LESS:
      return (e0.IsNumber() && e1.IsNumber())
                 ? Expression(Glyph((e0.GetNumber() < e1.GetNumber())
                                        ? FunctionType::K_COMBINATOR
                                        : FunctionType::FALSE__SECOND))
                 : Expression();
    case FunctionType::K_COMBINATOR:
      return e0;
    case FunctionType::FALSE__SECOND:
      return e0;
    default:
      assert(false);
  }
  return {};
}

Expression Apply(FunctionType ftype, Expression& e0, Expression& e1,
                 Expression& e2) {
  assert(ExpectedParameters(ftype) == 3);
  Expression e;
  switch (ftype) {
    case FunctionType::S_COMBINATOR:
      e.Add(Glyph(GlyphType::OPERAND));
      e.Add(Glyph(GlyphType::OPERAND));
      e.Add(e0);
      e.Add(e2);
      e.Add(Glyph(GlyphType::OPERAND));
      e.Add(e1);
      e.Add(e2);
      return e;
    case FunctionType::C_COMBINATOR:
      e.Add(Glyph(GlyphType::OPERAND));
      e.Add(Glyph(GlyphType::OPERAND));
      e.Add(e0);
      e.Add(e2);
      e.Add(e1);
      return e;
    case FunctionType::B_COMBINATOR:
      e.Add(Glyph(GlyphType::OPERAND));
      e.Add(e0);
      e.Add(Glyph(GlyphType::OPERAND));
      e.Add(e1);
      e.Add(e2);
      return e;
    case FunctionType::CONS__PAIR:
      e.Add(Glyph(GlyphType::OPERAND));
      e.Add(Glyph(GlyphType::OPERAND));
      e.Add(e2);
      e.Add(e0);
      e.Add(e1);
      return e;
    default:
      assert(false);
  }
  return {};
}
