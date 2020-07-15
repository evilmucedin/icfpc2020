#include "wrapper.h"

#define STB_IMAGE_IMPLEMENTATION
#include "stb_image.h"

class PNGWrapper::Impl {
public:
  	Impl(const std::string& filename) : filename_(filename) {
      		int width, height, channels;
      		unsigned char* img = stbi_load(filename_.c_str(), &width, &height, &channels, 0);
      		if (img == NULL) {
	      		throw std::exception();
      		}
		img_.resize(channels);
		for (size_t i = 0; i < channels; ++i) {
			img_[i].resize(height);
			for (size_t j = 0; j < height; ++j) {
				img_[i][j].resize(width);
				for (size_t k = 0; k < width; ++k) {
					img_[i][j][k] = img[i + k*channels + j*channels*width];
				}
			}
		}
  }

private:
  std::string filename_;
  std::vector<std::vector<std::vector<char>>> img_;
};

PNGWrapper::PNGWrapper(const std::string& filename) : impl_(std::make_unique<Impl>(filename)) { }
