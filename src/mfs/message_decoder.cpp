#include "message_decoder.h"

MessageDecoder::MessageDecoder(GlyphDecoder& _gd) : gd(_gd) {}

GlyphCompact MessageDecoder::DecodeGlyphCompact(const MessageAsImage& /*mi*/,
                                                const MatrixSlice& /*s*/) {
  return {};
}

Glyph MessageDecoder::DecodeGlyph(const MessageAsImage& mi,
                                  const MatrixSlice& s) {
  return gd.Decode(DecodeGlyphCompact(mi, s));
}

Expression MessageDecoder::DecodeExpression(const MessageAsImage& /*mi*/,
                                            const MatrixSlice& /*s*/) {
  return {};
}

Line MessageDecoder::DecodeLine(const MessageAsImage& /*mi*/,
                                const MatrixSlice& /*s*/) {
  return {};
}

Message MessageDecoder::Decode(const MessageAsImage& /*mi*/) { return {}; }
