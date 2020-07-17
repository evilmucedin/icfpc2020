#include "message_decoder.h"

#include "common/base.h"

MessageDecoder::MessageDecoder(GlyphDecoder& _gd) : gd(_gd) {}

GlyphCompact MessageDecoder::DecodeGlyphCompact(const TMatrixSlice& /*ms*/) {
  return {};
}

Glyph MessageDecoder::DecodeGlyph(const TMatrixSlice& ms) {
  return gd.Decode(DecodeGlyphCompact(ms));
}

Expression MessageDecoder::DecodeExpression(const TMatrixSlice& /*ms*/) {
  return {};
}

Line MessageDecoder::DecodeLine(const TMatrixSlice& /*ms*/) { return {}; }

Message MessageDecoder::Decode(const MessageAsImage& mi) {
  Message m;
  TMatrixSlice ms(mi.m);
  assert(!ms.IsRowEmpty(0));
  for (unsigned rb = 0, re; rb < ms.Rows();) {
    for (re = rb;; ++re) {
      if (ms.IsRowEmpty(re) && ms.IsRowEmpty(re + 1)) break;
    }
    m.v.push_back(DecodeLine(TMatrixSlice(ms, rb, re)));
    rb = re + 2;
  }
  return m;
}
