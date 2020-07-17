#include "message_decoder.h"

#include "common/base.h"

MessageDecoder::MessageDecoder(GlyphDecoder& _gd) : gd(_gd) {}

GlyphCompact MessageDecoder::DecodeGlyphCompact(const TMatrixSlice& ms) {
  assert((ms.Rows() <= 8) && (ms.Columns() <= 8));
  uint64_t v = 0;
  for (unsigned r = 0; r < ms.Rows(); ++r) {
    for (unsigned c = 0; c < ms.Columns(); ++c) {
      v += (ms.Get(r, c) ? 1ull : 0ull) << (8 * r + c);
    }
  }
  return {v};
}

Glyph MessageDecoder::DecodeGlyph(const TMatrixSlice& ms) {
  return gd.Decode(DecodeGlyphCompact(ms));
}

Expression MessageDecoder::DecodeExpression(const TMatrixSlice& ms) {
  Expression e;
  for (unsigned cb = 0, ce; cb < ms.Columns();) {
    assert(!ms.IsColumnEmpty(cb));
    for (ce = cb; ce < ms.Columns(); ++ce) {
      if (ms.IsColumnEmpty(ce)) break;
    }
    e.v.push_back(DecodeGlyph(TMatrixSlice(ms, 0, ms.Rows(), cb, ce)));
    cb = ce + 1;
    if (ms.IsColumnEmpty(cb)) ++cb;
  }
  return e;
}

Line MessageDecoder::DecodeLine(const TMatrixSlice& ms) {
  Line l;
  for (unsigned cb = 0, ce; cb < ms.Columns();) {
    assert(!ms.IsColumnEmpty(cb));
    for (ce = cb; ce + 2 < ms.Columns(); ++ce) {
      if (ms.IsColumnEmpty(ce) && ms.IsColumnEmpty(ce + 1) &&
          ms.IsColumnEmpty(ce + 2))
        break;
    }
    l.v.push_back(DecodeExpression(TMatrixSlice(ms, 0, ms.Rows(), cb, ce + 2)));
    for (cb = ce + 3; (cb < ms.Columns()) && ms.IsColumnEmpty(cb);) ++cb;
  }
  return l;
}

Message MessageDecoder::Decode(const MessageAsImage& mi) {
  Message m;
  TMatrixSlice ms(mi.m);
  assert(!ms.IsRowEmpty(0));
  for (unsigned rb = 0, re; rb < ms.Rows();) {
    for (re = rb; re + 1 < ms.Rows(); ++re) {
      if (ms.IsRowEmpty(re) && ms.IsRowEmpty(re + 1)) break;
    }
    m.v.push_back(DecodeLine(TMatrixSlice(ms, rb, re)));
    rb = re + 2;
  }
  return m;
}
