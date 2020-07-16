#include "glyph_decoder.h"

#include "common/stl/base.h"

#include "stb/wrapper.h"

void PNGExample(const std::string& filename) {
  PNGWrapper w(filename);
  std::cout << w.getChannels() << " " << w.getWidth() << " " << w.getHeight()
            << std::endl;
  for (size_t i = 0; i < w.getChannels(); ++i) {
    for (size_t j = 0; j < w.getHeight(); ++j) {
      for (size_t k = 0; k < w.getWidth(); ++k) {
        std::cout << unsigned(w.get(i, j, k)) << " ";
      }
      std::cout << std::endl;
    }
    std::cout << std::endl;
  }
}

int main() {
  // PNGExample("../src/mfs/messages/message14.png");
  GlyphDecoder gd = GlyphDecoder::GetDecoder();
  for (int64_t i = -10; i < 30; ++i) {
    auto ei = gd.Encode(Glyph(GlyphType::NUMBER, i));
    auto di = gd.Decode(ei);
    cout << i << " -> " << ei.mask << " -> " << di.value << endl;
  }
  return 0;
}
