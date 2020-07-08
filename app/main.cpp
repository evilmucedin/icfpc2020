#include <iostream>
#include "httplib.h"

int main(int argc, char* argv[])
{
    std::string server_url(argv[1]);
    std::string player_key(argv[2]);

    std::cout << "ServerUrl: " << server_url << "; PlayerKey: " << player_key << std::endl;

    auto url = server_url.substr(server_url.find(":") + 3); // Remove schema
    auto colonPosition = url.find(":");
    auto pathPosition = url.find("/") != std::string::npos ? url.find("/") : url.length();
    auto host = url.substr(0, colonPosition);
    auto port = std::stoi(url.substr(colonPosition + 1, pathPosition));
    auto path = url.substr(pathPosition);

    httplib::Client cli(host, port);

    auto res = cli.Get((path + "?playerKey=" + player_key).c_str());

    if (!res || res->status != 200) {
        return 1;
    }

    return 0;
}
