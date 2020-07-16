#pragma once

#include "expression.h"
#include "glyph.h"
#include "glyph_compact.h"
#include "glyph_decoder.h"
#include "line.h"
#include "matrix_slice.h"
#include "message.h"
#include "message_as_image.h"

class MessageDecoder {
 protected:
  GlyphDecoder& gd;

 public:
  MessageDecoder(GlyphDecoder& _gd);

  GlyphCompact DecodeGlyphCompact(const MessageAsImage& mi,
                                  const MatrixSlice& s);
  Glyph DecodeGlyph(const MessageAsImage& mi, const MatrixSlice& s);
  Expression DecodeExpression(const MessageAsImage& mi, const MatrixSlice& s);
  Line DecodeLine(const MessageAsImage& mi, const MatrixSlice& s);

  Message Decode(const MessageAsImage& mi);
};
