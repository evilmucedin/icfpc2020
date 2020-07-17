#pragma once

#include "expression.h"
#include "glyph.h"
#include "glyph_compact.h"
#include "glyph_decoder.h"
#include "line.h"
#include "matrix_slice.h"
#include "message.h"
#include "message_as_image.h"

#include "common/linear_algebra/matrix.h"

class MessageDecoder {
 protected:
  GlyphDecoder& gd;

 public:
  using TMatrixSlice = MatrixSlice<la::MatrixBool>;

  MessageDecoder(GlyphDecoder& _gd);

  GlyphCompact DecodeGlyphCompact(const TMatrixSlice& ms);
  Glyph DecodeGlyph(const TMatrixSlice& ms);
  Expression DecodeExpression(const TMatrixSlice& ms);
  Line DecodeLine(const TMatrixSlice& s);

  Message Decode(const MessageAsImage& mi);
};