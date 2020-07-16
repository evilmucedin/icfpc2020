#include "glyph_decoder.h"

#include "common/assert_exception.h"
#include "common/base.h"

#include <vector>

namespace {
uint64_t BOOLEAN_FALSE = 7 + (1 << 8) + (5 << 16);
uint64_t BOOLEAN_TRUE = 7 + (5 << 8) + (1 << 16);

GlyphDecoder gd;
}  // namespace

void GlyphDecoder::RegisterGlyphType(GlyphType type, uint64_t mask) {
  Assert(mask & 1);
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
  RegisterFunctionType(FunctionType::F170,
                       15 * rows[0] + 9 * rows[1] + 11 * rows[2] + 9 * rows[3]);
  RegisterFunctionType(FunctionType::F341, 15 * rows[0] + 11 * rows[1] +
                                               9 * rows[2] + 11 * rows[3]);
}

Glyph GlyphDecoder::Decode(const GlyphCompact& gc) const {
  if (!(gc.mask & 1)) return {GlyphType::NUMBER, DecodeNumber(gc.mask)};
  auto itf = map_mask_function_type.find(gc.mask);
  if (itf != map_mask_function_type.end()) return {itf->second};
  auto itg = map_mask_glyph_type.find(gc.mask);
  if (itg != map_mask_glyph_type.end()) return {itg->second};
  if (gc.mask == BOOLEAN_FALSE) return {GlyphType::BOOLEAN, 0};
  if (gc.mask == BOOLEAN_TRUE) return {GlyphType::BOOLEAN, 1};
  // Check if variable
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
    case GlyphType::BOOLEAN:
      return {g.value ? BOOLEAN_TRUE : BOOLEAN_FALSE};
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

int64_t GlyphDecoder::DecodeVariable(uint64_t) const {
  assert(false);
  return 0;
}

uint64_t GlyphDecoder::EncodeVariable(int64_t) const {
  assert(false);
  return 0;
}

GlyphDecoder& GlyphDecoder::GetDecoder() { return gd; }
