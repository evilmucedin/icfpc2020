#include "glyph_decoder.h"
#include "message.h"
#include "message_as_image.h"
#include "message_decoder.h"

#include "common/stl/base.h"

#include "stb/wrapper.h"

#include <string>

namespace {
std::string messages_dir = "../src/mfs/messages/";
}

void PNGExample(const std::string& filename) {
  MessageAsImage mi(filename);
  // mi.Print();
  MessageDecoder md(GlyphDecoder::GetDecoder());
  Message m = md.Decode(mi);
  m.Print();
}

int main() {
  PNGExample("../src/mfs/messages/message4.png");
  return 0;
}
