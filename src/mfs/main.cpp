#include "glyph_decoder.h"

#include "common/stl/base.h"

int main() {
  GlyphDecoder gd = GlyphDecoder::GetDecoder();
  for (int64_t i = -10; i < 30; ++i) {
    auto ei = gd.Encode(Glyph(GlyphType::NUMBER, i));
    auto di = gd.Decode(ei);
    cout << i << " -> " << ei.mask << " -> " << di.value << endl;
  }
  return 0;
}
