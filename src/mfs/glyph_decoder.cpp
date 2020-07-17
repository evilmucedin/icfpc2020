#include "glyph_decoder.h"

#include "common/assert_exception.h"
#include "common/base.h"

#include <vector>

namespace {
uint64_t MASK_DOT = 1 << 8;

GlyphDecoder gd;
}  // namespace

void GlyphDecoder::RegisterGlyphType(GlyphType type, uint64_t mask) {
  Assert((mask & 1) || (mask == MASK_DOT));
  Assert(map_mask_glyph_type.find(mask) == map_mask_glyph_type.end());
  Assert(map_glyph_type_mask.find(type) == map_glyph_type_mask.end());
  map_mask_glyph_type[mask] = type;
  map_glyph_type_mask[type] = mask;
}

void GlyphDecoder::RegisterFunctionType(FunctionType type, uint64_t mask) {
  Assert(mask & 1);
  Assert(map_mask_function_type.find(mask) == map_mask_function_type.end());
  Assert(map_function_type_mask.find(type) == map_function_type_mask.end());
  map_mask_function_type[mask] = type;
  map_function_type_mask[type] = mask;
}

GlyphDecoder::GlyphDecoder() { InitMap(); }

void GlyphDecoder::InitMap() {
  rows.resize(8, 1);
  for (unsigned i = 1; i < 8; ++i) rows[i] = (rows[i - 1] << 8);
  RegisterGlyphType(GlyphType::ONE, rows[0] + rows[1]);
  RegisterGlyphType(GlyphType::DOT, MASK_DOT);
  RegisterGlyphType(GlyphType::EQUALITY, 7 * rows[0] + rows[1] + 7 * rows[2]);
  RegisterGlyphType(GlyphType::OPERAND, 3 * rows[0] + rows[1]);
  RegisterFunctionType(FunctionType::SUCCESSOR,
                       15 * rows[0] + 3 * rows[1] + 9 * rows[2] + 13 * rows[3]);
  RegisterFunctionType(FunctionType::PREDECESSOR,
                       15 * rows[0] + 3 * rows[1] + 5 * rows[2] + 13 * rows[3]);
  RegisterFunctionType(FunctionType::SUM, 15 * rows[0] + 11 * rows[1] +
                                              11 * rows[2] + 11 * rows[3]);
  RegisterFunctionType(FunctionType::PRODUCT,
                       15 * rows[0] + 5 * rows[1] + 5 * rows[2] + 5 * rows[3]);
  RegisterFunctionType(FunctionType::DIVISION,
                       15 * rows[0] + rows[1] + 11 * rows[2] + rows[3]);
  RegisterFunctionType(FunctionType::EQUALITY,
                       15 * rows[0] + rows[1] + rows[2] + 15 * rows[3]);
  RegisterFunctionType(FunctionType::STRICT_LESS,
                       15 * rows[0] + rows[1] + 9 * rows[2] + 13 * rows[3]);
  RegisterFunctionType(FunctionType::MODULATE,
                       15 * rows[0] + 5 * rows[1] + 11 * rows[2] + 5 * rows[3]);
  RegisterFunctionType(
      FunctionType::DEMODULATE,
      15 * rows[0] + 11 * rows[1] + 5 * rows[2] + 11 * rows[3]);
  RegisterFunctionType(FunctionType::SEND, 15 * rows[0] + 13 * rows[1] +
                                               11 * rows[2] + 9 * rows[3]);
  RegisterFunctionType(FunctionType::NEGATE,
                       7 * rows[0] + 5 * rows[1] + 5 * rows[2]);
  RegisterFunctionType(FunctionType::S_COMBINATOR,
                       7 * rows[0] + 7 * rows[1] + 3 * rows[2]);
  RegisterFunctionType(FunctionType::C_COMBINATOR,
                       7 * rows[0] + 5 * rows[1] + 3 * rows[2]);
  RegisterFunctionType(FunctionType::B_COMBINATOR,
                       7 * rows[0] + 3 * rows[1] + 3 * rows[2]);
  RegisterFunctionType(FunctionType::K_COMBINATOR,
                       7 * rows[0] + 5 * rows[1] + 1 * rows[2]);
  RegisterFunctionType(FunctionType::FALSE_SECOND,
                       7 * rows[0] + 1 * rows[1] + 5 * rows[2]);
  RegisterFunctionType(FunctionType::POWER_OF_TWO,
                       127 * rows[0] + 65 * rows[1] + 89 * rows[2] +
                           85 * rows[3] + 69 * rows[4] + 65 * rows[5] +
                           127 * rows[6]);
  RegisterFunctionType(FunctionType::I_COMBINATOR, 3 * rows[0] + 3 * rows[1]);
  RegisterFunctionType(
      FunctionType::CONS_PAIR,
      31 * rows[0] + 21 * rows[1] + 21 * rows[2] + 21 * rows[3] + 31 * rows[4]);
  RegisterFunctionType(
      FunctionType::CAR_FIRST,
      31 * rows[0] + 29 * rows[1] + 21 * rows[2] + 21 * rows[3] + 31 * rows[4]);
}

Glyph GlyphDecoder::Decode(const GlyphCompact& gc) const {
  if (gc.mask == MASK_DOT) return {GlyphType::DOT};
  if (!(gc.mask & 1)) return {GlyphType::NUMBER, DecodeNumber(gc.mask)};
  auto itf = map_mask_function_type.find(gc.mask);
  if (itf != map_mask_function_type.end()) return {itf->second};
  auto itg = map_mask_glyph_type.find(gc.mask);
  if (itg != map_mask_glyph_type.end()) return {itg->second};
  if (IsVariable(gc.mask))
    return {GlyphType::VARIABLE, DecodeVariable(gc.mask)};
  return {};
}

GlyphCompact GlyphDecoder::Encode(const Glyph& g) const {
  switch (g.type) {
    case GlyphType::NUMBER:
      return {EncodeNumber(g.value)};
    case GlyphType::FUNCTION: {
      auto itf = map_function_type_mask.find(g.ftype);
      Assert(itf != map_function_type_mask.end());
      return {itf->second};
    }
    case GlyphType::VARIABLE:
      return {EncodeVariable(g.value)};
    default: {
      auto itg = map_glyph_type_mask.find(g.type);
      Assert(itg != map_glyph_type_mask.end());
      return {itg->second};
    }
  }
}

bool GlyphDecoder::DecodeNumberSign(uint64_t mask) const {
  for (unsigned i = 1; i < 8; ++i) {
    if ((mask & (1ull << (8 * i))) && !(mask & (1ull << i))) return true;
  }
  return false;
}

int64_t GlyphDecoder::DecodeNumber(uint64_t gmask) const {
  const uint64_t mask = (1u << 7) - 1;
  int64_t m = ((gmask >> 1) & mask) + 1, p = 1, r = 0;
  for (unsigned i = 1; i < 8; ++i) {
    r += p * ((gmask >> (8 * i + 1)) & mask);
    p *= m;
  }
  return {DecodeNumberSign(gmask) ? -r : r};
}

uint64_t GlyphDecoder::EncodeNumber(int64_t value) const {
  uint64_t avalue = (value < 0 ? -value : value);
  unsigned i = 1;
  for (; i < 7; ++i) {
    if (avalue < (1ull << (i * i))) break;
  }
  unsigned mask = (1ull << i) - 1, r = mask << 1;
  for (unsigned j = 0; j < i; ++j)
    r += ((1 + 2 * (((avalue >> (i * j)) & mask))) << (8 * (j + 1)));
  if (value < 0) r += (1ull << (8 * (i + 1)));
  return r;
}

// Current version support only positive indexes for variables
bool GlyphDecoder::IsVariable(uint64_t mask) const {
  unsigned i = 4;
  for (; i < 8; ++i) {
    if ((mask & (1ull << i)) == 0) break;
  }
  uint64_t a = (1ull << i) - 1, b = a + (a << (8 * (i - 1))),
           c = 1 + (1ull << (i - 1));
  if ((mask & b) != b) return false;
  for (unsigned j = 1; j < i - 1; ++j) {
    if (((mask >> (8 * j)) & c) != c) return false;
  }
  return true;
}

int64_t GlyphDecoder::DecodeVariable(uint64_t mask) const {
  unsigned i = 4;
  for (; i < 8; ++i) {
    if ((mask & (1ull << i)) == 0) break;
  }
  for (unsigned j = 0; j < i; ++j) mask ^= ((1ull << i) - 1) << (8 * j);
  return DecodeNumber(mask >> 9);
}

uint64_t GlyphDecoder::EncodeVariable(int64_t value) const {
  assert(value >= 0);
  unsigned i = 1;
  for (; i < 7; ++i) {
    if (value < (1ull << (i * i))) break;
  }
  i += 3;
  uint64_t mask = EncodeNumber(value) << 9;
  for (unsigned j = 0; j < i; ++j) mask ^= ((1ull << i) - 1) << (8 * j);
  return mask;
}

GlyphDecoder& GlyphDecoder::GetDecoder() { return gd; }
