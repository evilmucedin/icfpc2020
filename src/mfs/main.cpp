#include "glyph_decoder.h"
#include "linear_encoded_form.h"
#include "message.h"
#include "message_as_image.h"
#include "message_as_text.h"
#include "message_decoder.h"

#include "common/stl/base.h"

#include "stb/wrapper.h"

#include <string>

namespace {
std::string messages_dir = "../src/mfs/messages/";
}

void ReadPNG(const std::string& filename) {
  // MessageAsImage::PrintPNG(filename);
  MessageAsImage mi(filename);
  // mi.Print();
  MessageDecoder md(GlyphDecoder::GetDecoder());
  Message m = md.Decode(mi);
  m.Print();
}

void ReadText(const std::string& filename) {
  MessageAsText mt(filename);
  MessageDecoder md(GlyphDecoder::GetDecoder());
  Message m = md.Decode(mt);
  m.Print();
}

int main(int argc, char* argv[]) {
  string s = "1";
  if (argc >= 2) s = argv[1];
  ReadPNG("../src/mfs/messages/message" + s + ".png");
  cout << endl;
  ReadText("../src/mfs/messages/message" + s + "-decoded.txt");
  // GlyphDecoder gd = GlyphDecoder::GetDecoder();
  //   for (int64_t i = -10; i < 30; ++i) {
  // auto ei = gd.Encode(Glyph(GlyphType::VARIABLE, i));
  //   auto di = gd.Decode(ei);
  //   cout << i << " -> " << ei.mask << " -> " << di.value << endl;
  //     auto ei = LEFEncodeNumber(i);
  //     auto di = LEFDecodeNumber(ei);
  //     cout << i << " -> " << di << endl;
  //   }
  return 0;
}
