#include <SDL2/SDL.h>
#include <SDL2/SDL_image.h>
#include <SDL2/SDL_ttf.h>
#include <curl/curl.h>
#include <openssl/md5.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <unistd.h>
#include <iostream>
#include <string>
#include <vector>
#include <mutex>
#include <thread>
#include <algorithm>
#include <regex>
#include <cmath>

enum DisplayMode { MODE_SYSTEM, MODE_GAME };

std::mutex g_mutex;
DisplayMode g_pending_mode = MODE_SYSTEM;
std::string g_pending_theme = "backglass-default";

// System State Variables
std::string g_pending_sys_fullname = "";
std::string g_pending_sys_logo = "";

// Game State Variables
std::string g_pending_game_name = "";
std::string g_pending_game_desc = "";
std::string g_pending_game_thumbnail = "";
std::string g_pending_game_fanart = "";
std::string g_pending_game_image = "";
std::string g_pending_game_marquee = "";

bool g_pending_update = false;

// Active Theme Tracking
std::string g_current_theme = "backglass-default";

// Decoding and String processing helpers
std::string urlDecode(const std::string& src) {
    std::string dst;
    char a, b;
    for (size_t i = 0; i < src.length(); ++i) {
        if (src[i] == '%' && i + 2 < src.length() &&
            isxdigit(src[i+1]) && isxdigit(src[i+2])) {
            a = src[i+1];
            b = src[i+2];
            dst += (char)((tolower(a) >= 'a' ? tolower(a) - 'a' + 10 : a - '0') * 16 +
                          (tolower(b) >= 'a' ? tolower(b) - 'a' + 10 : b - '0'));
            i += 2;
        } else if (src[i] == '+') {
            dst += ' ';
        } else {
            dst += src[i];
        }
    }
    return dst;
}

std::string md5(const std::string& str) {
    unsigned char digest[MD5_DIGEST_LENGTH];
    MD5((unsigned char*)str.c_str(), str.size(), digest);
    char md5string[33];
    for(int i = 0; i < 16; ++i) {
        sprintf(&md5string[i*2], "%02x", (unsigned int)digest[i]);
    }
    return std::string(md5string);
}

std::string gameShortName(const std::string& path) {
    size_t last_slash = path.find_last_of("/\\");
    std::string base = (last_slash == std::string::npos) ? path : path.substr(last_slash + 1);
    size_t last_dot = base.find_last_of(".");
    if (last_dot != std::string::npos) {
        base = base.substr(0, last_dot);
    }
    base = std::regex_replace(base, std::regex(R"(\([^)]*\))"), "");
    base = std::regex_replace(base, std::regex("[^A-Za-z0-9]"), "");
    std::transform(base.begin(), base.end(), base.begin(), ::tolower);
    return base;
}

size_t WriteCallback(void* contents, size_t size, size_t nmemb, void* userp) {
    ((std::string*)userp)->append((char*)contents, size * nmemb);
    return size * nmemb;
}

std::string httpGet(const std::string& url) {
    CURL* curl = curl_easy_init();
    std::string readBuffer;
    if (curl) {
        curl_easy_setopt(curl, CURLOPT_URL, url.c_str());
        curl_easy_setopt(curl, CURLOPT_WRITEFUNCTION, WriteCallback);
        curl_easy_setopt(curl, CURLOPT_WRITEDATA, &readBuffer);
        curl_easy_perform(curl);
        curl_easy_cleanup(curl);
    }
    return readBuffer;
}

std::string getJsonValue(const std::string& json, const std::string& key) {
    std::string search_key = "\"" + key + "\"";
    size_t pos = json.find(search_key);
    if (pos == std::string::npos) return "";
    
    size_t colon = json.find(":", pos + search_key.length());
    if (colon == std::string::npos) return "";
    
    size_t open_quote = json.find("\"", colon);
    if (open_quote == std::string::npos) return "";
    
    size_t close_quote = open_quote + 1;
    while (close_quote < json.length()) {
        if (json[close_quote] == '\\' && close_quote + 1 < json.length()) {
            close_quote += 2;
            continue;
        }
        if (json[close_quote] == '\"') {
            break;
        }
        close_quote++;
    }
    if (close_quote >= json.length()) return "";
    
    std::string val = json.substr(open_quote + 1, close_quote - open_quote - 1);
    
    std::string clean_val = "";
    for (size_t i = 0; i < val.length(); ++i) {
        if (val[i] == '\\' && i + 1 < val.length()) {
            clean_val += val[i+1];
            i++;
        } else {
            clean_val += val[i];
        }
    }
    return clean_val;
}

std::string resolveAsset(const std::string& system, const std::string& path, const std::string& prop, const std::string& es_val) {
    std::string shortname = gameShortName(path);
    std::vector<std::string> extensions = {"png", "jpg", "gif"};
    for (const auto& ext : extensions) {
        std::string local_path = "/userdata/system/backglass/systems/" + system + "/games/" + prop + "/" + shortname + "." + ext;
        if (FILE* f = fopen(local_path.c_str(), "r")) {
            fclose(f);
            return local_path;
        }
    }
    if (!es_val.empty()) {
        if (es_val.rfind("/userdata/", 0) == 0) {
            if (FILE* f = fopen(es_val.c_str(), "r")) {
                fclose(f);
                return es_val;
            }
        }
        if (es_val[0] == '/') {
            std::string url = "http://localhost:1234" + es_val;
            std::string temp_path = "/tmp/backglass_temp_" + prop;
            CURL* curl = curl_easy_init();
            if (curl) {
                FILE* fp = fopen(temp_path.c_str(), "wb");
                if (fp) {
                    curl_easy_setopt(curl, CURLOPT_URL, url.c_str());
                    curl_easy_setopt(curl, CURLOPT_WRITEFUNCTION, NULL);
                    curl_easy_setopt(curl, CURLOPT_WRITEDATA, fp);
                    curl_easy_perform(curl);
                    fclose(fp);
                }
                curl_easy_cleanup(curl);
            }
            return temp_path;
        } else {
            return es_val;
        }
    }
    return "";
}

std::string resolveSystemLogo(const std::string& system, const std::string& es_val) {
    std::vector<std::string> extensions = {"png", "jpg", "gif"};
    for (const auto& ext : extensions) {
        std::string local_path = "/userdata/system/backglass/systems/" + system + "/logo." + ext;
        if (FILE* f = fopen(local_path.c_str(), "r")) {
            fclose(f);
            return local_path;
        }
    }
    if (!es_val.empty()) {
        if (es_val.rfind("/userdata/", 0) == 0) {
            if (FILE* f = fopen(es_val.c_str(), "r")) {
                fclose(f);
                return es_val;
            }
        }
        if (es_val[0] == '/') {
            std::string url = "http://localhost:1234" + es_val;
            std::string temp_path = "/tmp/backglass_temp_logo";
            CURL* curl = curl_easy_init();
            if (curl) {
                FILE* fp = fopen(temp_path.c_str(), "wb");
                if (fp) {
                    curl_easy_setopt(curl, CURLOPT_URL, url.c_str());
                    curl_easy_setopt(curl, CURLOPT_WRITEFUNCTION, NULL);
                    curl_easy_setopt(curl, CURLOPT_WRITEDATA, fp);
                    curl_easy_perform(curl);
                    fclose(fp);
                }
                curl_easy_cleanup(curl);
            }
            return temp_path;
        } else {
            return es_val;
        }
    }
    return "";
}

void restoreActiveState() {
    std::string state_file = "/tmp/es_active_system.txt";
    FILE* f = fopen(state_file.c_str(), "r");
    if (f) {
        char buf[256];
        if (fgets(buf, sizeof(buf), f)) {
            std::string system = buf;
            system.erase(std::remove_if(system.begin(), system.end(), ::isspace), system.end());
            if (!system.empty()) {
                std::string es_url = "http://localhost:1234/systems/" + system;
                std::string json_data = httpGet(es_url);
                std::string es_val = getJsonValue(json_data, "logo");
                std::string resolved_img = resolveSystemLogo(system, es_val);
                std::string system_fullname = getJsonValue(json_data, "fullname");

                {
                    std::lock_guard<std::mutex> lock(g_mutex);
                    g_pending_mode = MODE_SYSTEM;
                    g_pending_sys_fullname = system_fullname;
                    g_pending_sys_logo = resolved_img;
                    g_pending_update = true;
                }
            }
        }
        fclose(f);
    }
}

void serverThreadFunc(int port) {
    int server_fd = socket(AF_INET, SOCK_STREAM, 0);
    if (server_fd < 0) return;

    int opt = 1;
    setsockopt(server_fd, SOL_SOCKET, SO_REUSEADDR, &opt, sizeof(opt));

    struct sockaddr_in address;
    address.sin_family = AF_INET;
    address.sin_addr.s_addr = INADDR_ANY;
    address.sin_port = htons(port);

    if (bind(server_fd, (struct sockaddr*)&address, sizeof(address)) < 0) {
        close(server_fd);
        return;
    }

    if (listen(server_fd, 3) < 0) {
        close(server_fd);
        return;
    }

    while (true) {
        int addrlen = sizeof(address);
        int new_socket = accept(server_fd, (struct sockaddr*)&address, (socklen_t*)&addrlen);
        if (new_socket < 0) continue;

        char buffer[4096] = {0};
        int valread = read(new_socket, buffer, 4096);
        if (valread > 0) {
            std::string request(buffer, valread);
            size_t first_line_end = request.find("\r\n");
            if (first_line_end != std::string::npos) {
                std::string first_line = request.substr(0, first_line_end);
                size_t get_pos = first_line.find("GET ");
                size_t http_pos = first_line.find(" HTTP/");
                if (get_pos != std::string::npos && http_pos != std::string::npos) {
                    std::string full_path = first_line.substr(get_pos + 4, http_pos - (get_pos + 4));
                    size_t question_mark = full_path.find("?");
                    std::string path = (question_mark == std::string::npos) ? full_path : full_path.substr(0, question_mark);
                    std::string query = (question_mark == std::string::npos) ? "" : full_path.substr(question_mark + 1);

                    std::string system_val = "";
                    std::string path_val = "";
                    std::string url_val = "";

                    size_t pos = 0;
                    while (pos < query.length()) {
                        size_t next_amp = query.find("&", pos);
                        std::string pair = (next_amp == std::string::npos) ? query.substr(pos) : query.substr(pos, next_amp - pos);
                        size_t eq = pair.find("=");
                        if (eq != std::string::npos) {
                            std::string key = pair.substr(0, eq);
                            std::string val = urlDecode(pair.substr(eq + 1));
                            if (key == "system") system_val = val;
                            else if (key == "path") path_val = val;
                            else if (key == "url") url_val = val;
                        }
                        if (next_amp == std::string::npos) break;
                        pos = next_amp + 1;
                    }

                    if (path == "/game" && !system_val.empty() && !path_val.empty()) {
                        std::string game_hash = md5(path_val);
                        std::string es_url = "http://localhost:1234/systems/" + system_val + "/games/" + game_hash;
                        std::string json_data = httpGet(es_url);

                        std::string game_name = getJsonValue(json_data, "name");
                        std::string game_desc = getJsonValue(json_data, "desc");

                        std::string res_thumbnail = resolveAsset(system_val, path_val, "thumbnail", getJsonValue(json_data, "thumbnail"));
                        std::string res_fanart    = resolveAsset(system_val, path_val, "fanart", getJsonValue(json_data, "fanart"));
                        std::string res_image     = resolveAsset(system_val, path_val, "image", getJsonValue(json_data, "image"));
                        std::string res_marquee   = resolveAsset(system_val, path_val, "marquee", getJsonValue(json_data, "marquee"));

                        {
                            std::lock_guard<std::mutex> lock(g_mutex);
                            g_pending_mode = MODE_GAME;
                            g_pending_game_name = game_name;
                            g_pending_game_desc = game_desc;
                            g_pending_game_thumbnail = res_thumbnail;
                            g_pending_game_fanart = res_fanart;
                            g_pending_game_image = res_image;
                            g_pending_game_marquee = res_marquee;
                            g_pending_update = true;
                        }
                    }
                    else if (path == "/system" && !system_val.empty()) {
                        std::string es_url = "http://localhost:1234/systems/" + system_val;
                        std::string json_data = httpGet(es_url);

                        std::string resolved_img = resolveSystemLogo(system_val, getJsonValue(json_data, "logo"));
                        std::string system_fullname = getJsonValue(json_data, "fullname");

                        {
                            std::lock_guard<std::mutex> lock(g_mutex);
                            g_pending_mode = MODE_SYSTEM;
                            g_pending_sys_fullname = system_fullname;
                            g_pending_sys_logo = resolved_img;
                            g_pending_update = true;
                        }
                    }
                    else if (path == "/location" && !url_val.empty()) {
                        std::string new_theme = "backglass-default";
                        size_t bg_pos = url_val.find("backglass/");
                        if (bg_pos != std::string::npos) {
                            size_t slash_pos = url_val.find("/", bg_pos + 10);
                            if (slash_pos != std::string::npos) {
                                new_theme = url_val.substr(bg_pos + 10, slash_pos - (bg_pos + 10));
                            }
                        } else {
                            size_t www_pos = url_val.find("www/");
                            if (www_pos != std::string::npos) {
                                size_t slash_pos = url_val.find("/", www_pos + 4);
                                if (slash_pos != std::string::npos) {
                                    new_theme = url_val.substr(www_pos + 4, slash_pos - (www_pos + 4));
                                }
                            } else {
                                new_theme = url_val;
                            }
                        }
                        {
                            std::lock_guard<std::mutex> lock(g_mutex);
                            g_current_theme = new_theme;
                            g_pending_update = true;
                        }
                    }
                }
            }

            std::string response = "HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nContent-Length: 3\r\nConnection: close\r\n\r\nOK\n";
            write(new_socket, response.c_str(), response.length());
        }
        close(new_socket);
    }
}

// NATIVE GRAPHICS HELPERS

void renderImage(SDL_Renderer* renderer, SDL_Texture* texture, SDL_Rect boundary, const std::string& objectFit, float innerScale = 1.0f) {
    if (!texture) return;

    int texW = 0, texH = 0;
    SDL_QueryTexture(texture, NULL, NULL, &texW, &texH);
    if (texW <= 0 || texH <= 0) return;

    if (innerScale < 1.0f) {
        int newW = boundary.w * innerScale;
        int newH = boundary.h * innerScale;
        boundary.x += (boundary.w - newW) / 2;
        boundary.y += (boundary.h - newH) / 2;
        boundary.w = newW;
        boundary.h = newH;
    }

    SDL_Rect dstrect;
    if (objectFit == "fill") {
        dstrect = boundary;
    } else {
        float texAspect = (float)texW / texH;
        float boundAspect = (float)boundary.w / boundary.h;

        if (texAspect > boundAspect) {
            dstrect.w = boundary.w;
            dstrect.h = (int)(boundary.w / texAspect);
            dstrect.x = boundary.x;
            dstrect.y = boundary.y + (boundary.h - dstrect.h) / 2;
        } else {
            dstrect.h = boundary.h;
            dstrect.w = (int)(boundary.h * texAspect);
            dstrect.y = boundary.y;
            dstrect.x = boundary.x + (boundary.w - dstrect.w) / 2;
        }
    }
    SDL_RenderCopy(renderer, texture, NULL, &dstrect);
}

SDL_Texture* createTextTexture(SDL_Renderer* renderer, TTF_Font* font, const std::string& text, SDL_Color color, int wrapWidth) {
    if (!font || text.empty()) return nullptr;
    SDL_Surface* surface = TTF_RenderUTF8_Blended_Wrapped(font, text.c_str(), color, wrapWidth);
    if (!surface) return nullptr;
    SDL_Texture* texture = SDL_CreateTextureFromSurface(renderer, surface);
    SDL_FreeSurface(surface);
    return texture;
}

void renderHeaderText(SDL_Renderer* renderer, SDL_Texture* texture, SDL_Rect boundary) {
    if (!texture) return;
    int texW = 0, texH = 0;
    SDL_QueryTexture(texture, NULL, NULL, &texW, &texH);
    if (texW <= 0 || texH <= 0) return;

    SDL_Rect dstrect = { 0, 0, texW, texH };

    if (texW > boundary.w || texH > boundary.h) {
        float scaleW = (float)boundary.w / texW;
        float scaleH = (float)boundary.h / texH;
        float minScale = std::min(scaleW, scaleH);
        dstrect.w = (int)(texW * minScale);
        dstrect.h = (int)(texH * minScale);
    }

    dstrect.x = boundary.x + (boundary.w - dstrect.w) / 2;
    dstrect.y = boundary.y + (boundary.h - dstrect.h) / 2;
    SDL_RenderCopy(renderer, texture, NULL, &dstrect);
}

// Renders wrapping descriptions with real-time delta speed smooth loop-crawling
void renderDescriptionText(SDL_Renderer* renderer, SDL_Texture* texture, SDL_Rect boundary, float elapsed_seconds) {
    if (!texture) return;
    int texW = 0, texH = 0;
    SDL_QueryTexture(texture, NULL, NULL, &texW, &texH);
    if (texW <= 0 || texH <= 0) return;

    int max_scroll = texH - boundary.h;
    int scroll_offset_y = 0;

    if (max_scroll > 0) {
        float pause_top = 3.0f;       // 3.0 seconds pause at the top before starting crawl
        float scroll_speed = 25.0f;   // Comfortable, clean crawling speed (25 pixels per second)
        float scroll_duration = (float)max_scroll / scroll_speed;
        float pause_bottom = 3.0f;    // 3.0 seconds pause at the end of the text block
        float total_cycle = pause_top + scroll_duration + pause_bottom;

        float current_cycle = fmod(elapsed_seconds, total_cycle);
        if (current_cycle > pause_top && current_cycle <= (pause_top + scroll_duration)) {
            scroll_offset_y = (int)((current_cycle - pause_top) * scroll_speed);
        } else if (current_cycle > (pause_top + scroll_duration)) {
            scroll_offset_y = max_scroll;
        }
    }

    SDL_RenderSetClipRect(renderer, &boundary);

    SDL_Rect dstrect = { boundary.x, boundary.y - scroll_offset_y, texW, texH };
    SDL_RenderCopy(renderer, texture, NULL, &dstrect);

    SDL_RenderSetClipRect(renderer, NULL);
}

int main(int argc, char* argv[]) {
    std::string target_display_name = "";
    std::string theme_path = "";

    for (int i = 1; i < argc; ++i) {
        std::string arg = argv[i];
        if (arg == "--output" && i + 1 < argc) {
            target_display_name = argv[++i];
        } else if (arg == "--www" && i + 1 < argc) {
            theme_path = argv[++i];
        }
    }

    if (!theme_path.empty()) {
        size_t bg_pos = theme_path.find("backglass/");
        if (bg_pos != std::string::npos) {
            size_t slash_pos = theme_path.find("/", bg_pos + 10);
            if (slash_pos != std::string::npos) {
                g_current_theme = theme_path.substr(bg_pos + 10, slash_pos - (bg_pos + 10));
            }
        } else {
            size_t www_pos = theme_path.find("www/");
            if (www_pos != std::string::npos) {
                size_t slash_pos = theme_path.find("/", www_pos + 4);
                if (slash_pos != std::string::npos) {
                    g_current_theme = theme_path.substr(www_pos + 4, slash_pos - (www_pos + 4));
                }
            } else {
                g_current_theme = theme_path;
            }
        }
    }

    curl_global_init(CURL_GLOBAL_ALL);

    if (SDL_Init(SDL_INIT_VIDEO) < 0) return 1;
    if (!(IMG_Init(IMG_INIT_PNG | IMG_INIT_JPG) & (IMG_INIT_PNG | IMG_INIT_JPG))) return 1;
    if (TTF_Init() < 0) return 1;

    // Separate Bold (Headers) from Regular weight (Descriptions)
    std::string font_path_header = "";
    std::vector<std::string> header_font_candidates = {
        "/usr/share/fonts/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
    };
    for (const auto& path : header_font_candidates) {
        if (FILE* f = fopen(path.c_str(), "r")) {
            fclose(f);
            font_path_header = path;
            break;
        }
    }

    std::string font_path_desc = "";
    std::vector<std::string> desc_font_candidates = {
        "/usr/share/fonts/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/TTF/DejaVuSans.ttf",
        "/usr/share/fonts/TTF/LiberationSans-Regular.ttf"
    };
    for (const auto& path : desc_font_candidates) {
        if (FILE* f = fopen(path.c_str(), "r")) {
            fclose(f);
            font_path_desc = path;
            break;
        }
    }

    int win_x = 0;
    int win_y = 0;
    int win_w = 800;
    int win_h = 600;

    if (!target_display_name.empty()) {
        int num_displays = SDL_GetNumVideoDisplays();
        int matched_index = -1;

        std::string s_target = target_display_name;
        std::transform(s_target.begin(), s_target.end(), s_target.begin(), ::tolower);

        for (int i = 0; i < num_displays; ++i) {
            const char* name = SDL_GetDisplayName(i);
            if (name) {
                std::string s_name(name);
                std::transform(s_name.begin(), s_name.end(), s_name.begin(), ::tolower);
                if (s_name.find(s_target) != std::string::npos || s_target.find(s_name) != std::string::npos) {
                    matched_index = i;
                    break;
                }
            }
        }

        if (matched_index != -1) {
            SDL_Rect bounds;
            if (SDL_GetDisplayBounds(matched_index, &bounds) == 0) {
                win_x = bounds.x;
                win_y = bounds.y;
                win_w = bounds.w;
                win_h = bounds.h;
            }
        }
    } else {
        SDL_Rect bounds;
        if (SDL_GetDisplayBounds(0, &bounds) == 0) {
            win_x = bounds.x;
            win_y = bounds.y;
            win_w = bounds.w;
            win_h = bounds.h;
        }
    }

    SDL_Window* window = SDL_CreateWindow("backglass", win_x, win_y, win_w, win_h, SDL_WINDOW_SHOWN | SDL_WINDOW_BORDERLESS);
    if (!window) return 1;

    SDL_Renderer* renderer = SDL_CreateRenderer(window, -1, SDL_RENDERER_ACCELERATED | SDL_RENDERER_PRESENTVSYNC);
    if (!renderer) return 1;

    int header_font_size = std::max(24, (int)(win_h * 0.10f));
    int desc_font_size   = std::max(16, (int)(win_h * 0.04f));

    TTF_Font* font_header = nullptr;
    TTF_Font* font_desc = nullptr;
    if (!font_path_header.empty()) {
        font_header = TTF_OpenFont(font_path_header.c_str(), header_font_size);
    }
    if (!font_path_desc.empty()) {
        font_desc = TTF_OpenFont(font_path_desc.c_str(), desc_font_size);
    }

    restoreActiveState();

    std::thread server_thread(serverThreadFunc, 2033);
    server_thread.detach();

    bool running = true;
    SDL_Event event;

    DisplayMode current_mode = MODE_SYSTEM;
    std::string sys_fullname = "";
    std::string sys_logo_path = "";
    std::string game_name = "";
    std::string game_desc = "";
    std::string game_thumbnail_path = "";
    std::string game_fanart_path = "";
    std::string game_image_path = "";
    std::string game_marquee_path = "";

    SDL_Texture* tex_sys_logo = nullptr;
    SDL_Texture* tex_game_thumbnail = nullptr;
    SDL_Texture* tex_game_fanart = nullptr;
    SDL_Texture* tex_game_image = nullptr;
    SDL_Texture* tex_game_marquee = nullptr;

    SDL_Texture* tex_sys_fullname = nullptr;
    SDL_Texture* tex_game_name = nullptr;
    SDL_Texture* tex_game_desc = nullptr;

    Uint32 start_time = SDL_GetTicks();

    while (running) {
        while (SDL_PollEvent(&event)) {
            if (event.type == SDL_QUIT) {
                running = false;
            }
        }

        bool update_needed = false;
        {
            std::lock_guard<std::mutex> lock(g_mutex);
            if (g_pending_update) {
                current_mode = g_pending_mode;
                sys_fullname = g_pending_sys_fullname;
                sys_logo_path = g_pending_sys_logo;
                game_name = g_pending_game_name;
                game_desc = g_pending_game_desc;
                game_thumbnail_path = g_pending_game_thumbnail;
                game_fanart_path = g_pending_game_fanart;
                game_image_path = g_pending_game_image;
                game_marquee_path = g_pending_game_marquee;

                update_needed = true;
                g_pending_update = false;
            }
        }

        if (update_needed) {
            // Re-sync delta timer dynamically on game switch
            start_time = SDL_GetTicks();

            if (tex_sys_logo) { SDL_DestroyTexture(tex_sys_logo); tex_sys_logo = nullptr; }
            if (tex_game_thumbnail) { SDL_DestroyTexture(tex_game_thumbnail); tex_game_thumbnail = nullptr; }
            if (tex_game_fanart) { SDL_DestroyTexture(tex_game_fanart); tex_game_fanart = nullptr; }
            if (tex_game_image) { SDL_DestroyTexture(tex_game_image); tex_game_image = nullptr; }
            if (tex_game_marquee) { SDL_DestroyTexture(tex_game_marquee); tex_game_marquee = nullptr; }
            if (tex_sys_fullname) { SDL_DestroyTexture(tex_sys_fullname); tex_sys_fullname = nullptr; }
            if (tex_game_name) { SDL_DestroyTexture(tex_game_name); tex_game_name = nullptr; }
            if (tex_game_desc) { SDL_DestroyTexture(tex_game_desc); tex_game_desc = nullptr; }

            int winW, winH;
            SDL_GetWindowSize(window, &winW, &winH);
            SDL_Color whiteColor = {255, 255, 255, 255};

            if (!sys_logo_path.empty()) tex_sys_logo = IMG_LoadTexture(renderer, sys_logo_path.c_str());
            if (!game_thumbnail_path.empty()) tex_game_thumbnail = IMG_LoadTexture(renderer, game_thumbnail_path.c_str());
            if (!game_fanart_path.empty()) tex_game_fanart = IMG_LoadTexture(renderer, game_fanart_path.c_str());
            if (!game_image_path.empty()) tex_game_image = IMG_LoadTexture(renderer, game_image_path.c_str());
            if (!game_marquee_path.empty()) tex_game_marquee = IMG_LoadTexture(renderer, game_marquee_path.c_str());

            if (!sys_fullname.empty()) tex_sys_fullname = createTextTexture(renderer, font_header, sys_fullname, whiteColor, (int)(winW * 0.9f));
            if (!game_name.empty()) tex_game_name = createTextTexture(renderer, font_header, game_name, whiteColor, (int)(winW * 0.9f));
            
            int desc_wrap_width = (winW >= winH) ? (int)(winW * 0.4f * 0.90f) : (int)(winW * 0.80f);
            if (!game_desc.empty()) tex_game_desc = createTextTexture(renderer, font_desc, game_desc, whiteColor, desc_wrap_width);
        }

        SDL_SetRenderDrawColor(renderer, 0, 0, 0, 255);
        SDL_RenderClear(renderer);

        int winW, winH;
        SDL_GetWindowSize(window, &winW, &winH);
        
        // Calculate the absolute elapsed seconds cleanly using the GPU timer offset
        float elapsed_seconds = (float)(SDL_GetTicks() - start_time) / 1000.0f;

        if (current_mode == MODE_SYSTEM) {
            if (tex_sys_logo) {
                SDL_Rect boundary = {0, 0, winW, winH};
                renderImage(renderer, tex_sys_logo, boundary, "contain", 0.95f);
            } else if (tex_sys_fullname) {
                SDL_Rect boundary = {0, 0, winW, winH};
                renderHeaderText(renderer, tex_sys_fullname, boundary);
            }
        } 
        else {
            if (g_current_theme == "backglass-boxart") {
                if (tex_game_thumbnail) {
                    SDL_Rect boundary = {0, 0, winW, winH};
                    renderImage(renderer, tex_game_thumbnail, boundary, "contain");
                } else if (tex_game_name) {
                    SDL_Rect boundary = {0, 0, winW, (int)(winH * 0.25f)};
                    renderHeaderText(renderer, tex_game_name, boundary);
                }
            } 
            else if (g_current_theme == "backglass-fanart") {
                if (tex_game_fanart) {
                    SDL_Rect boundary = {0, 0, winW, winH};
                    renderImage(renderer, tex_game_fanart, boundary, "fill");
                } else if (tex_game_name) {
                    SDL_Rect boundary = {0, 0, winW, (int)(winH * 0.25f)};
                    renderHeaderText(renderer, tex_game_name, boundary);
                }
            } 
            else if (g_current_theme == "backglass-image") {
                if (tex_game_image) {
                    SDL_Rect boundary = {0, 0, winW, winH};
                    renderImage(renderer, tex_game_image, boundary, "contain");
                } else if (tex_game_name) {
                    SDL_Rect boundary = {0, 0, winW, (int)(winH * 0.25f)};
                    renderHeaderText(renderer, tex_game_name, boundary);
                }
            } 
            else if (g_current_theme == "backglass-marquee") {
                if (tex_game_marquee) {
                    SDL_Rect boundary = {0, 0, winW, winH};
                    renderImage(renderer, tex_game_marquee, boundary, "contain");
                } else if (tex_game_name) {
                    SDL_Rect boundary = {0, 0, winW, (int)(winH * 0.25f)};
                    renderHeaderText(renderer, tex_game_name, boundary);
                }
            } 
            else {
                SDL_Rect topRect = {0, 0, winW, (int)(winH * 0.25f)};
                if (tex_game_marquee) {
                    renderImage(renderer, tex_game_marquee, topRect, "contain");
                } else if (tex_game_name) {
                    renderHeaderText(renderer, tex_game_name, topRect);
                }

                if (winW >= winH) {
                    SDL_Rect imgRect = {0, (int)(winH * 0.25f), (int)(winW * 0.6f), (int)(winH * 0.75f)};
                    if (tex_game_image) {
                        renderImage(renderer, tex_game_image, imgRect, "contain", 0.95f);
                    }

                    if (tex_game_desc) {
                        SDL_Rect descRect = {(int)(winW * 0.6f), (int)(winH * 0.25f), (int)(winW * 0.4f), (int)(winH * 0.75f)};
                        int marginX = descRect.w * 0.05f;
                        int marginY = descRect.h * 0.05f;
                        descRect.x += marginX;
                        descRect.y += marginY;
                        descRect.w = descRect.w * 0.90f;
                        descRect.h = descRect.h * 0.90f;

                        renderDescriptionText(renderer, tex_game_desc, descRect, elapsed_seconds);
                    }
                } 
                else {
                    SDL_Rect imgRect = {0, (int)(winH * 0.25f), winW, (int)(winH * 0.55f)};
                    if (tex_game_image) {
                        renderImage(renderer, tex_game_image, imgRect, "contain", 0.95f);
                    }

                    if (tex_game_desc) {
                        SDL_Rect descRect = {0, (int)(winH * 0.80f), winW, (int)(winH * 0.20f)};
                        int marginX = descRect.w * 0.10f;
                        int marginY = descRect.h * 0.05f;
                        descRect.x += marginX;
                        descRect.y += marginY;
                        descRect.w = descRect.w * 0.80f;
                        descRect.h = descRect.h * 0.90f;

                        renderDescriptionText(renderer, tex_game_desc, descRect, elapsed_seconds);
                    }
                }
            }
        }

        SDL_RenderPresent(renderer);
        SDL_Delay(16);
    }

    if (tex_sys_logo) SDL_DestroyTexture(tex_sys_logo);
    if (tex_game_thumbnail) SDL_DestroyTexture(tex_game_thumbnail);
    if (tex_game_fanart) SDL_DestroyTexture(tex_game_fanart);
    if (tex_game_image) SDL_DestroyTexture(tex_game_image);
    if (tex_game_marquee) SDL_DestroyTexture(tex_game_marquee);
    if (tex_sys_fullname) SDL_DestroyTexture(tex_sys_fullname);
    if (tex_game_name) SDL_DestroyTexture(tex_game_name);
    if (tex_game_desc) SDL_DestroyTexture(tex_game_desc);

    if (font_header) TTF_CloseFont(font_header);
    if (font_desc) TTF_CloseFont(font_desc);
    SDL_DestroyRenderer(renderer);
    SDL_DestroyWindow(window);

    TTF_Quit();
    IMG_Quit();
    SDL_Quit();
    curl_global_cleanup();

    return 0;
}
