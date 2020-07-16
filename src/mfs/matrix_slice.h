#pragma once

class MatrixSlice {
 protected:
  unsigned i0, i1, j0, j1;

 public:
  unsigned Rows() const { return i1 - i0; }
  unsigned Columns() const { return j1 - j0; }

  template <class TMatrix>
  typename TMatrix::TValue Get(const TMatrix& m, unsigned i, unsigned j) const {
    return m.Get(i0 + i, j0 + j);
  }
};
