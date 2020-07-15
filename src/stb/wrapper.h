#pragma once

#include <string>
#include <memory>
#include <vector>

class PNGWrapper {
  public:
    PNGWrapper(const std::string& filename);

  private:
    class Impl;
    std::unique_ptr<Impl> impl_;
};
