#include "glyph_decoder.h"
#include "message_as_image.h"

#include "common/stl/base.h"

#include "stb/wrapper.h"

#include <string>

namespace {
std::string messages_dir = "../src/mfs/messages/";
}

void PNGExample(const std::string& filename) {
  MessageAsImage m(filename);
  m.Print();
}

int main() {
  PNGExample("../src/mfs/messages/message14.png");
  //   GlyphDecoder gd = GlyphDecoder::GetDecoder();
  //   for (int64_t i = -10; i < 30; ++i) {
  //     auto ei = gd.Encode(Glyph(GlyphType::NUMBER, i));
  //     auto di = gd.Decode(ei);
  //     cout << i << " -> " << ei.mask << " -> " << di.value << endl;
  //   }
  return 0;
}
