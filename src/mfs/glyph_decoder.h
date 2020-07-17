#pragma once

#include "function_type.h"
#include "glyph.h"
#include "glyph_compact.h"
#include "glyph_type.h"

#include <unordered_map>
#include <vector>

class GlyphDecoder {
 protected:
  std::vector<uint64_t> rows;
  std::unordered_map<uint64_t, GlyphType> map_mask_glyph_type;
  std::unordered_map<uint64_t, FunctionType> map_mask_function_type;
  std::unordered_map<GlyphType, uint64_t> map_glyph_type_mask;
  std::unordered_map<FunctionType, uint64_t> map_function_type_mask;

  void RegisterGlyphType(GlyphType type, uint64_t mask);
  void RegisterFunctionType(FunctionType type, uint64_t mask);

 public:
  GlyphDecoder();

  void InitMap();

  Glyph Decode(const GlyphCompact& gc) const;
  GlyphCompact Encode(const Glyph& g) const;

  bool DecodeNumberSign(uint64_t mask) const;
  int64_t DecodeNumber(uint64_t mask) const;
  uint64_t EncodeNumber(int64_t value) const;

  bool IsVariable(uint64_t mask) const;
  int64_t DecodeVariable(uint64_t mask) const;
  uint64_t EncodeVariable(int64_t value) const;

  static GlyphDecoder& GetDecoder();
};
