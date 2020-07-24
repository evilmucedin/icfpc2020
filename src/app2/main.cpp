#define CPPHTTPLIB_OPENSSL_SUPPORT

#include "httplib.h"
#include <iostream>
#include <regex>
#include <string>

int main(int /*argc*/, char* argv[]) {
  const std::string playerKey(argv[1]);

  std::cout << "PlayerKey: " << playerKey
            << std::endl;

  const std::string serverName = "https://icfpc2020-api.testkontur.ru";
  httplib::Client2 client(serverName.c_str());
  const std::shared_ptr<httplib::Response> serverResponse =
      client.Post("/aliens/send?apiKey=3bd205ec3d2640ac9b73eccecf9d540e", playerKey.c_str(), "text/plain");

  if (!serverResponse) {
    std::cout << "Unexpected server response:\nNo response from server"
              << std::endl;
    return 1;
  }

  if (serverResponse->status != 200) {
    std::cout << "Unexpected server response:\nHTTP code: "
              << serverResponse->status
              << "\nResponse body: " << serverResponse->body << std::endl;
    std::cout << "Headers:\n";
    for (const auto& h: serverResponse->headers) {
    	std::cout << "\t" << h.first << "=" << h.second << std::endl;
    }
    return 2;
  }

  std::cout << "Server response: " << serverResponse->body << std::endl;
  return 0;
}
