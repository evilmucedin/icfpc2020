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
    case FunctionType::LENGTH:
      return 1;
    case FunctionType::SUM:
    case FunctionType::PRODUCT:
    case FunctionType::DIVISION:
    case FunctionType::EQUALITY:
    case FunctionType::STRICT_LESS:
    case FunctionType::K_COMBINATOR:
    case FunctionType::FALSE__SECOND:
    case FunctionType::CONCAT:
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

Expression Evaluate(FunctionType ftype) {
  FakeUse(ftype);
  assert(ExpectedParameters(ftype) == 0);
  assert(false);
  return {};
}

Expression Evaluate(FunctionType ftype, Expression& e0) {
  assert(ExpectedParameters(ftype) == 1);
  Expression etemp;
  switch (ftype) {
    case FunctionType::SUCCESSOR:
      e0.Evaluate();
      assert(e0.IsNumber());
      return Expression(e0.GetNumber() + 1);
    case FunctionType::PREDECESSOR:
      e0.Evaluate();
      assert(e0.IsNumber());
      return Expression(e0.GetNumber() - 1);
    case FunctionType::MODULATE:
      e0.Evaluate();
      if (e0.IsNumber()) {
        return Expression(Glyph(LEFEncodeNumber(e0.GetNumber())));
      }
      return {};
    case FunctionType::DEMODULATE:
      e0.Evaluate();
      if (e0.IsLEF()) {
        return Expression(LEFDecodeNumber(e0.GetLEF()));
      }
      return {};
    case FunctionType::SEND:
      return {};
    case FunctionType::NEGATE:
      e0.Evaluate();
      assert(e0.IsNumber());
      return Expression(-e0.GetNumber());
    case FunctionType::POWER_OF_TWO:
      e0.Evaluate();
      assert(e0.IsNumber());
      assert(e0.GetNumber() >= 0);
      return Expression((1ll << e0.GetNumber()));
    case FunctionType::I_COMBINATOR:
      return e0;
    case FunctionType::CAR__FIRST:
      etemp.Add(Glyph(GlyphType::OPERAND));
      etemp.Add(e0);
      etemp.Add(Glyph(FunctionType::K_COMBINATOR));
      return etemp;
    case FunctionType::CDR__TAIL:
      etemp.Add(Glyph(GlyphType::OPERAND));
      etemp.Add(e0);
      etemp.Add(Glyph(FunctionType::FALSE__SECOND));
      return etemp;
    case FunctionType::NIL__EMPTY_LIST:
      return Expression(Glyph(FunctionType::K_COMBINATOR));
    case FunctionType::IS_NIL:
      while (!e0.IsList()) {
        if (!e0.EvaluateOnce()) {
          break;
        }
      }
      assert(e0.IsList());
      return Expression(Glyph(((e0.v.size() == 1) &&
                               (e0.v[0].ftype == FunctionType::NIL__EMPTY_LIST))
                                  ? FunctionType::K_COMBINATOR
                                  : FunctionType::FALSE__SECOND));
    case FunctionType::LOG2:
      e0.Evaluate();
      assert(e0.IsNumber());
      {
        int64_t v = e0.GetNumber(), r = 0;
        for (; v >= 2; v /= 2) ++r;
        return Expression(r);
      }
    // case FunctionType::LENGTH:
    //   e0.Evaluate();
    //   assert(e0.IsList());
    //   return Expression(e0.v.size() / 4);
    default:
      assert(false);
  }
  return {};
}

Expression Evaluate(FunctionType ftype, Expression& e0, Expression& e1) {
  assert(ExpectedParameters(ftype) == 2);
  switch (ftype) {
    case FunctionType::SUM:
      e0.Evaluate();
      e1.Evaluate();
      assert(e0.IsNumber() && e1.IsNumber());
      return Expression(e0.GetNumber() + e1.GetNumber());
    case FunctionType::PRODUCT:
      e0.Evaluate();
      e1.Evaluate();
      assert(e0.IsNumber() && e1.IsNumber());
      return Expression(e0.GetNumber() * e1.GetNumber());
    case FunctionType::DIVISION:
      e0.Evaluate();
      e1.Evaluate();
      assert(e0.IsNumber() && e1.IsNumber());
      return Expression(e0.GetNumber() / e1.GetNumber());
    case FunctionType::EQUALITY:
      if (e0 == e1) return Expression(FunctionType::K_COMBINATOR);
      e0.Evaluate();
      e1.Evaluate();
      assert(e0.IsNumber() && e1.IsNumber());
      return Expression(Glyph((e0.GetNumber() == e1.GetNumber())
                                  ? FunctionType::K_COMBINATOR
                                  : FunctionType::FALSE__SECOND));
    case FunctionType::STRICT_LESS:
      e0.Evaluate();
      e1.Evaluate();
      assert(e0.IsNumber() && e1.IsNumber());
      return Expression(Glyph((e0.GetNumber() == e1.GetNumber())
                                  ? FunctionType::K_COMBINATOR
                                  : FunctionType::FALSE__SECOND));
    case FunctionType::K_COMBINATOR:
      return e0;
    case FunctionType::FALSE__SECOND:
      return e1;
    case FunctionType::CONCAT:
      e0.Evaluate();
      e1.Evaluate();
      assert(e0.IsList() && e1.IsList());
      {
        Expression e = e0;
        assert(e.v.back().ftype == FunctionType::NIL__EMPTY_LIST);
        e.v.pop_back();
        e.Add(e1);
        return e;
      }
    default:
      assert(false);
  }
  return {};
}

Expression Evaluate(FunctionType ftype, Expression& e0, Expression& e1,
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
    case FunctionType::VECTOR:
      e.Add(Glyph(GlyphType::OPERAND));
      e.Add(Glyph(GlyphType::OPERAND));
      e.Add(e2);
      e.Add(e0);
      e.Add(e1);
      return e;
    case FunctionType::IF0:
      e0.Evaluate();
      assert(e0.IsNumber());
      return e0.GetNumber() ? e2 : e1;
    default:
      assert(false);
  }
  return {};
}

Expression Evaluate(FunctionType ftype, std::vector<Expression>& v) {
  switch (v.size()) {
    case 0:
      return Evaluate(ftype);
    case 1:
      return Evaluate(ftype, v[0]);
    case 2:
      return Evaluate(ftype, v[0], v[1]);
    case 3:
      return Evaluate(ftype, v[0], v[1], v[2]);
    default:
      assert(false);
      return {};
  }
}
