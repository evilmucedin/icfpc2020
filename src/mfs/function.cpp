#include "function.h"

#include "function_type.h"
#include "linear_encoded_form.h"

#include "common/base.h"
#include "common/template.h"

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
    case FunctionType::IS_NIL:
    case FunctionType::LOG2:
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
    case FunctionType::VECTOR:
    case FunctionType::IF0:
      return 3;
    default:
      return unsigned(-1);
  }
}

Expression Apply(FunctionType ftype) {
  FakeUse(ftype);
  assert(ExpectedParameters(ftype) == 0);
  assert(false);
  return {};
}

Expression Apply(FunctionType ftype, const Expression& e0) {
  assert(ExpectedParameters(ftype) == 1);
  Expression e;
  switch (ftype) {
    case FunctionType::SUCCESSOR:
      return e0.IsNumber() ? Expression(e0.GetNumber() + 1) : Expression();
    case FunctionType::PREDECESSOR:
      return e0.IsNumber() ? Expression(e0.GetNumber() - 1) : Expression();
    case FunctionType::MODULATE:
      if (e0.IsNumber()) {
        return Expression(Glyph(LEFEncodeNumber(e0.GetNumber())));
      }
      return {};
    case FunctionType::DEMODULATE:
      if (e0.IsLEF()) {
        return Expression(LEFDecodeNumber(e0.GetLEF()));
      }
      return {};
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
    case FunctionType::IS_NIL:
      if (e.IsList()) {
        return Expression(
            Glyph(((e.v.size() == 1) &&
                   (e.v[0].ftype == FunctionType::NIL__EMPTY_LIST))
                      ? FunctionType::K_COMBINATOR
                      : FunctionType::FALSE__SECOND));
      }
      return {};
    case FunctionType::LOG2:
      if (e0.IsNumber()) {
        int64_t v = e0.GetNumber(), r = 0;
        for (; v >= 2; v /= 2) ++r;
        return Expression(r);
      }
      return {};
    default:
      assert(false);
  }
  return {};
}

Expression Apply(FunctionType ftype, const Expression& e0,
                 const Expression& e1) {
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
      return e1;
    default:
      assert(false);
  }
  return {};
}

Expression Apply(FunctionType ftype, const Expression& e0, const Expression& e1,
                 const Expression& e2) {
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
    case FunctionType::VECTOR:
      e.Add(Glyph(GlyphType::OPERAND));
      e.Add(Glyph(GlyphType::OPERAND));
      e.Add(e2);
      e.Add(e0);
      e.Add(e1);
      return e;
    case FunctionType::IF0:
      return e0.IsNumber() ? (e0.GetNumber() ? e2 : e1) : Expression();
    default:
      assert(false);
  }
  return {};
}

Expression Apply(FunctionType ftype, const std::vector<Expression>& v) {
  switch (v.size()) {
    case 0:
      return Apply(ftype);
    case 1:
      return Apply(ftype, v[0]);
    case 2:
      return Apply(ftype, v[0], v[1]);
    case 3:
      return Apply(ftype, v[0], v[1], v[2]);
    default:
      assert(false);
      return {};
  }
}
