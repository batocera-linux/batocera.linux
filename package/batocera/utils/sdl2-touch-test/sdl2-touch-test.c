/*
 * This file is part of the batocera distribution (https://batocera.org).
 * Copyright (c) 2026+.
 *
 * Written by dmanlfc when going mad troubleshooting multi-touchscreen devices
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, version 3.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program. If not, see <http://www.gnu.org/licenses/>.
 *
 * YOU MUST KEEP THIS HEADER AS IT IS
 */
#include <SDL2/SDL.h>
#include <SDL2/SDL_ttf.h>
#include <libudev.h>
#include <stdio.h>
#include <stdbool.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>

// Simple color palette to dynamically distinguish separate displays
const SDL_Color DISPLAY_COLORS[] = {
    {180, 0, 0, 255},    // Red (Display 0)
    {0, 150, 0, 255},    // Green (Display 1)
    {0, 0, 180, 255},    // Blue (Display 2)
    {150, 0, 150, 255},  // Purple (Display 3)
    {0, 150, 150, 255}   // Teal (Display 4)
};
const int NUM_COLORS = 5;

// States for application state machine
typedef enum {
    STATE_TESTING,
    STATE_CALIBRATING,
    STATE_VERIFYING
} AppState;

// Simple point structures for float and double representations
typedef struct {
    double x;
    double y;
} Point2D;

typedef struct {
    int x;
    int y;
} PixelPoint;

// Cached properties of the matched active udev device
typedef struct {
    char name[256];
    char devnode[128];
    char id_path[128];
    char devpath[256];
} UdevProperties;

// Struct to store calibration data dynamically for each screen
typedef struct {
    double A, B, C, D, E, F;
    char touch_name[256];
    bool calibrated;
} DisplayCalibration;

// Global flags and state
bool debug_enabled = false;
AppState app_state = STATE_CALIBRATING; // Auto-start directly in calibration mode
int current_cal_display = 0;
int calibration_step = 0; // 0 to 3 for 4 calibration targets
bool all_calibrated = false;

// Targets and inputs for calibration (in normalized coordinates 0.0 to 1.0)
Point2D target_points[4];
Point2D raw_points[4];

// Solved coefficients for x' = A*x + B*y + C and y' = D*x + E*y + F
double matrix_A = 1.0, matrix_B = 0.0, matrix_C = 0.0;
double matrix_D = 0.0, matrix_E = 1.0, matrix_F = 0.0;

// Helper to resolve device name from SDL_TouchID in SDL2
const char* get_touch_name_by_id(SDL_TouchID id) {
    int num_devices = SDL_GetNumTouchDevices();
    for (int i = 0; i < num_devices; i++) {
        if (SDL_GetTouchDevice(i) == id) {
            return SDL_GetTouchName(i);
        }
    }
    return "Unknown Touch Device";
}

// Smart-rounding function to strip human tap noise and neutralize signed zero (-0) formats
double smart_round(double val) {
    double nearest_int = round(val);
    if (fabs(val - nearest_int) < 0.05) {
        return nearest_int + 0.0; // Adding 0.0 neutralizes negative float representation (-0.0)
    }
    if (fabs(val) < 1e-9) {
        return 0.0;
    }
    return val;
}

// Clean DRM/KMS backend display name output containing redundant (null) entries
void clean_display_name(const char* raw_name, char* clean_name, size_t max_len) {
    if (!raw_name) {
        strncpy(clean_name, "Unknown", max_len);
        return;
    }
    char temp[256];
    strncpy(temp, raw_name, sizeof(temp) - 1);
    temp[sizeof(temp) - 1] = '\0';

    // Replace occurrences of "(null)" with empty space
    char* p;
    while ((p = strstr(temp, "(null)")) != NULL) {
        memmove(p, p + 6, strlen(p + 6) + 1);
    }

    // Collapse multiple whitespaces and strip leading/trailing spaces
    char* src = temp;
    char* dst = clean_name;
    char* limit = clean_name + max_len - 1;
    bool last_was_space = true;

    while (*src && dst < limit) {
        if (*src == ' ' || *src == '\t') {
            if (!last_was_space) {
                *dst++ = ' ';
                last_was_space = true;
            }
        } else {
            *dst++ = *src;
            last_was_space = false;
        }
        src++;
    }
    *dst = '\0';

    size_t len = strlen(clean_name);
    if (len > 0 && clean_name[len - 1] == ' ') {
        clean_name[len - 1] = '\0';
        len--;
    }

    // Strip redundant outer parentheses (e.g. "(DSI-2)" -> "DSI-2")
    if (len >= 2 && clean_name[0] == '(' && clean_name[len - 1] == ')') {
        memmove(clean_name, clean_name + 1, len - 2);
        clean_name[len - 2] = '\0';
    }

    if (strlen(clean_name) == 0) {
        strncpy(clean_name, "DSI-Panel", max_len);
    }
}

// Fallback search to resolve physical touch screen hardware under Wayland wrappers
bool query_udev_fallback(UdevProperties* props) {
    struct udev* udev = udev_new();
    if (!udev) return false;

    struct udev_enumerate* enumerate = udev_enumerate_new(udev);
    udev_enumerate_add_match_subsystem(enumerate, "input");
    udev_enumerate_scan_devices(enumerate);

    struct udev_list_entry* devices = udev_enumerate_get_list_entry(enumerate);
    struct udev_list_entry* entry;
    bool match_found = false;

    udev_list_entry_foreach(entry, devices) {
        const char* syspath = udev_list_entry_get_name(entry);
        struct udev_device* dev = udev_device_new_from_syspath(udev, syspath);
        if (dev) {
            const char* is_touch = udev_device_get_property_value(dev, "ID_INPUT_TOUCHSCREEN");
            if (is_touch && strcmp(is_touch, "1") == 0) {
                const char* kernel_name = udev_device_get_sysattr_value(dev, "name");
                const char* id_path = udev_device_get_property_value(dev, "ID_PATH");
                const char* devpath = udev_device_get_devpath(dev);
                const char* devnode = udev_device_get_devnode(dev);

                memset(props, 0, sizeof(UdevProperties));
                if (kernel_name) strncpy(props->name, kernel_name, sizeof(props->name) - 1);
                if (id_path) strncpy(props->id_path, id_path, sizeof(props->id_path) - 1);
                if (devpath) strncpy(props->devpath, devpath, sizeof(props->devpath) - 1);
                if (devnode) strncpy(props->devnode, devnode, sizeof(props->devnode) - 1);

                match_found = true;
                udev_device_unref(dev);
                break;
            }
            udev_device_unref(dev);
        }
    }

    udev_enumerate_unref(enumerate);
    udev_unref(udev);
    return match_found;
}

// Query the udev database for the matching touchscreen name
bool query_udev_device(const char* sdl_name, UdevProperties* props) {
    // Under Wayland, the device name is abstracted as "wayland_touch". Fallback immediately.
    if (!sdl_name || strcmp(sdl_name, "wayland_touch") == 0) {
        return query_udev_fallback(props);
    }

    struct udev* udev = udev_new();
    if (!udev) return false;

    struct udev_enumerate* enumerate = udev_enumerate_new(udev);
    udev_enumerate_add_match_subsystem(enumerate, "input");
    udev_enumerate_scan_devices(enumerate);

    struct udev_list_entry* devices = udev_enumerate_get_list_entry(enumerate);
    struct udev_list_entry* entry;
    bool match_found = false;

    udev_list_entry_foreach(entry, devices) {
        const char* syspath = udev_list_entry_get_name(entry);
        struct udev_device* dev = udev_device_new_from_syspath(udev, syspath);
        if (dev) {
            const char* kernel_name = udev_device_get_sysattr_value(dev, "name");
            if (kernel_name && strcmp(kernel_name, sdl_name) == 0) {
                const char* id_path = udev_device_get_property_value(dev, "ID_PATH");
                const char* devpath = udev_device_get_devpath(dev);
                const char* devnode = udev_device_get_devnode(dev);

                memset(props, 0, sizeof(UdevProperties));
                strncpy(props->name, kernel_name, sizeof(props->name) - 1);
                if (id_path) strncpy(props->id_path, id_path, sizeof(props->id_path) - 1);
                if (devpath) strncpy(props->devpath, devpath, sizeof(props->devpath) - 1);
                if (devnode) strncpy(props->devnode, devnode, sizeof(props->devnode) - 1);

                match_found = true;
                udev_device_unref(dev);
                break;
            }
            udev_device_unref(dev);
        }
    }

    udev_enumerate_unref(enumerate);
    udev_unref(udev);

    if (!match_found) {
        return query_udev_fallback(props);
    }
    return match_found;
}

// Extract a clean DEVPATH matcher from absolute system paths
void get_devpath_pattern(const char* devpath, char* buffer, size_t max_len) {
    if (!devpath || strlen(devpath) == 0) {
        strncpy(buffer, "*", max_len);
        return;
    }

    const char* i2c_ptr = strstr(devpath, ".i2c");
    if (i2c_ptr) {
        const char* start = i2c_ptr;
        while (start > devpath && *(start - 1) != '/') {
            start--;
        }
        const char* i2c_bus = strstr(i2c_ptr, "/i2c-");
        if (i2c_bus) {
            const char* end = strchr(i2c_bus + 5, '/');
            if (end) {
                size_t segment_len = end - start;
                if (segment_len < max_len - 5) {
                    snprintf(buffer, max_len, "*/%.*s/*", (int)segment_len, start);
                    return;
                }
            }
        }
    }
    snprintf(buffer, max_len, "%s", devpath);
}

// Perform 4-Point Linear Least Squares Regression using Cramer's Rule
bool calculate_calibration_matrix(void) {
    double S_xx = 0, S_xy = 0, S_yy = 0, S_x = 0, S_y = 0;
    double S_xtx = 0, S_xty = 0, S_xt = 0;
    double S_ytx = 0, S_yty = 0, S_yt = 0;
    int N = 4;

    for (int i = 0; i < N; i++) {
        double u = raw_points[i].x;
        double v = raw_points[i].y;
        double tx = target_points[i].x;
        double ty = target_points[i].y;

        S_xx += u * u;
        S_xy += u * v;
        S_yy += v * v;
        S_x  += u;
        S_y  += v;

        S_xtx += tx * u;
        S_xty += tx * v;
        S_xt  += tx;

        S_ytx += ty * u;
        S_yty += ty * v;
        S_yt  += ty;
    }

    double M00 = S_xx, M01 = S_xy, M02 = S_x;
    double M10 = S_xy, M11 = S_yy, M12 = S_y;
    double M20 = S_x,  M21 = S_y,  M22 = N;

    double det = M00 * (M11 * M22 - M12 * M12) -
                 M01 * (M01 * M22 - M12 * M02) +
                 M02 * (M01 * M12 - M11 * M02);

    if (fabs(det) < 1e-9) {
        printf("[SDL2_TOUCH_TEST] ERROR: Singular matrix, calibration points are colinear.\n");
        return false;
    }

    double b0_x = S_xtx, b1_x = S_xty, b2_x = S_xt;
    double detA = b0_x * (M11 * M22 - M12 * M12) -
                  M01  * (b1_x * M22 - M12 * b2_x) +
                  M02  * (b1_x * M12 - M11 * b2_x);
    double detB = M00  * (b1_x * M22 - M12 * b2_x) -
                  b0_x * (M01  * M22 - M12 * M02) +
                  M02  * (M01  * b2_x - b1_x * M02);
    double detC = M00  * (M11  * b2_x - b1_x * M12) -
                  M01  * (M01  * b2_x - b1_x * M02) +
                  b0_x * (M01  * M12 - M11 * M02);

    matrix_A = detA / det;
    matrix_B = detB / det;
    matrix_C = detC / det;

    double b0_y = S_ytx, b1_y = S_yty, b2_y = S_yt;
    double detD = b0_y * (M11 * M22 - M12 * M12) -
                  M01  * (b1_y * M22 - M12 * b2_y) +
                  M02  * (b1_y * M12 - M11 * b2_y);
    double detE = M00  * (b1_y * M22 - M12 * b2_y) -
                  b0_y * (M01  * M22 - M12 * M02) +
                  M02  * (M01  * b2_y - b1_y * M02);
    double detF = M00  * (M11  * b2_y - b1_y * M12) -
                  M01  * (M01  * b2_y - b1_y * M02) +
                  b0_y * (M01  * M12 - M11 * M02);

    matrix_D = detD / det;
    matrix_E = detE / det;
    matrix_F = detF / det;

    return true;
}

// Print udev matrix rule for all calibrated screens to standard output
void print_all_calibration_rules(SDL_Rect* displays, int num_displays, DisplayCalibration* cal_results) {
    printf("\n========================================================================\n");
    printf("[SDL2_TOUCH_TEST] ALL CALIBRATIONS COMPLETE!\n");
    printf("========================================================================\n");

    printf("\n# -------------------------------------------------------------------------\n");
    printf("# Dynamic system rules generated by SDL Touch Diagnostic Utility\n");
    printf("# Place these entries in: /etc/udev/rules.d/99-touchscreen.rules\n");
    printf("# -------------------------------------------------------------------------\n\n");

    for (int i = 0; i < num_displays; i++) {
        if (!cal_results[i].calibrated) continue;

        char clean_disp[128];
        clean_display_name(SDL_GetDisplayName(i), clean_disp, sizeof(clean_disp));

        printf("# Calibration for Display %d (%s) using Touch Device '%s':\n", 
               i, clean_disp, cal_results[i].touch_name);

        UdevProperties props;
        if (query_udev_device(cal_results[i].touch_name, &props)) {
            char devpath_pat[256] = "";
            get_devpath_pattern(props.devpath, devpath_pat, sizeof(devpath_pat));

            if (strlen(props.id_path) > 0) {
                printf("# Option A (Recommended: Match strictly by hardware connection port path):\n");
                printf("SUBSYSTEM==\"input\", KERNEL==\"event*\", \\\n");
                printf("  ENV{ID_INPUT_TOUCHSCREEN}==\"1\", \\\n");
                printf("  ENV{ID_PATH}==\"%s\", \\\n", props.id_path);
                // Print with %g representation to drop redundant decimal trailing zeros
                printf("  ENV{LIBINPUT_CALIBRATION_MATRIX}=\"%g %g %g %g %g %g\"\n\n",
                       smart_round(cal_results[i].A), smart_round(cal_results[i].B), smart_round(cal_results[i].C),
                       smart_round(cal_results[i].D), smart_round(cal_results[i].E), smart_round(cal_results[i].F));
            }

            printf("# Option B (Device and Driver Bus specific signature):\n");
            printf("SUBSYSTEM==\"input\", KERNEL==\"event*\", \\\n");
            printf("  ENV{ID_INPUT_TOUCHSCREEN}==\"1\", \\\n");
            printf("  DEVPATH==\"%s\", \\\n", devpath_pat);
            printf("  ENV{LIBINPUT_CALIBRATION_MATRIX}=\"%g %g %g %g %g %g\"\n\n",
                   smart_round(cal_results[i].A), smart_round(cal_results[i].B), smart_round(cal_results[i].C),
                   smart_round(cal_results[i].D), smart_round(cal_results[i].E), smart_round(cal_results[i].F));
        } else {
            printf("# WARNING: Could not correlate SDL hardware name with udev directly.\n");
            printf("ENV{LIBINPUT_CALIBRATION_MATRIX}=\"%g %g %g %g %g %g\"\n\n",
                   smart_round(cal_results[i].A), smart_round(cal_results[i].B), smart_round(cal_results[i].C),
                   smart_round(cal_results[i].D), smart_round(cal_results[i].E), smart_round(cal_results[i].F));
        }
        printf("# -------------------------------------------------------------------------\n\n");
    }
    printf("========================================================================\n\n");
}

// Dynamic TrueType Font resolver
TTF_Font* load_system_font(void) {
    const char* paths[] = {
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
        "/usr/share/fonts/truetype/freefont/FreeSans.ttf",
        "/usr/share/fonts/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/TTF/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/noto/NotoSans-Regular.ttf"
    };
    int path_count = sizeof(paths) / sizeof(paths[0]);
    for (int i = 0; i < path_count; i++) {
        TTF_Font* font = TTF_OpenFont(paths[i], 18);
        if (font) return font;
    }
    return NULL;
}

// Simple surface-to-texture blitter for standard UI labels
void draw_label(SDL_Renderer* renderer, TTF_Font* font, const char* text, int x, int y, SDL_Color color, bool center) {
    if (!font) return;
    SDL_Surface* surface = TTF_RenderText_Blended(font, text, color);
    if (!surface) return;
    SDL_Texture* texture = SDL_CreateTextureFromSurface(renderer, surface);
    if (texture) {
        SDL_Rect dest = { x, y, surface->w, surface->h };
        if (center) {
            dest.x -= surface->w / 2;
            dest.y -= surface->h / 2;
        }
        SDL_RenderCopy(renderer, texture, NULL, &dest);
        SDL_DestroyTexture(texture);
    }
    SDL_FreeSurface(surface);
}

// Text wrapping utility designed to scale layout for small screens
void draw_wrapped_text(SDL_Renderer* renderer, TTF_Font* font, const char* text, int cx, int y, int max_w, SDL_Color color) {
    if (!font || !text) return;

    char temp[512];
    strncpy(temp, text, sizeof(temp) - 1);
    temp[sizeof(temp) - 1] = '\0';

    char* words[128];
    int word_count = 0;
    char* token = strtok(temp, " ");
    while (token && word_count < 128) {
        words[word_count++] = token;
        token = strtok(NULL, " ");
    }

    char current_line[256] = "";
    int line_y = y;
    int line_spacing = TTF_FontLineSkip(font);
    if (line_spacing <= 0) line_spacing = 22;

    for (int i = 0; i < word_count; i++) {
        char test_line[256];
        if (strlen(current_line) == 0) {
            snprintf(test_line, sizeof(test_line), "%s", words[i]);
        } else {
            snprintf(test_line, sizeof(test_line), "%s %s", current_line, words[i]);
        }

        int w = 0, h = 0;
        TTF_SizeText(font, test_line, &w, &h);

        if (w > max_w && strlen(current_line) > 0) {
            draw_label(renderer, font, current_line, cx, line_y, color, true);
            line_y += line_spacing;
            snprintf(current_line, sizeof(current_line), "%s", words[i]);
        } else {
            snprintf(current_line, sizeof(current_line), "%s", test_line);
        }
    }

    if (strlen(current_line) > 0) {
        draw_label(renderer, font, current_line, cx, line_y, color, true);
    }
}

// Render a thick, flashing colored border around display boundaries
void draw_thick_border(SDL_Renderer* renderer, SDL_Rect rect, int thickness, SDL_Color color) {
    SDL_SetRenderDrawColor(renderer, color.r, color.g, color.b, color.a);
    for (int t = 0; t < thickness; t++) {
        SDL_Rect border_rect = {
            rect.x + t,
            rect.y + t,
            rect.w - 2 * t,
            rect.h - 2 * t
        };
        SDL_RenderDrawRect(renderer, &border_rect);
    }
}

// Display the help documentation in standard terminal outputs
void print_help(void) {
    printf("Agnostic SDL Touch Diagnostic and Calibration Utility\n\n");
    printf("Usage:\n");
    printf("  sdl2-touch-test [options]\n\n");
    printf("Options:\n");
    printf("  -h, --help       Show this help manual\n");
    printf("  -d, --debug      Enable verbose input delta and log tracking\n");
    printf("  -s, --skip-cal   Launch directly into touch testing mode (bypasses calibration startup)\n");
    printf("  -i, --index <id> Target a specific display index directly (default is Display 0)\n\n");
    printf("Interactions:\n");
    printf("  In Testing Mode:\n");
    printf("    Touch the screens to map input positions (indicated by a yellow block).\n");
    printf("    Press 'C' on a keyboard to enter Calibration Mode manually.\n\n");
    printf("  In Calibration Mode:\n");
    printf("    Precisely tap the center of each flashing target sequentially.\n");
    printf("    The screen will highlight active targets in flashing borders.\n\n");
    printf("  In Verification Mode:\n");
    printf("    Test the calibration alignment live on screen (yellow box vs gray crosshair).\n");
    printf("    Tap 'RETRY' (Red) or press 'R' to clear calculations and restart.\n");
    printf("    Tap 'SAVE & NEXT / EXIT' (Green) or press 'ENTER' to accept and output rules.\n\n");
    printf("  Global Keys:\n");
    printf("    Press 'ESC' anywhere to quit the application cleanly.\n\n");
}

int main(int argc, char* argv[]) {
    if (SDL_Init(SDL_INIT_VIDEO | SDL_INIT_EVENTS) < 0) {
        printf("[SDL2_TOUCH_TEST] ERROR: Failed to initialize SDL: %s\n", SDL_GetError());
        return 1;
    }

    // --- WORKAROUND FOR WAYLAND ASYNCHRONOUS OUTPUT ENUMERATION ---
    // Under Wayland, connected displays (outputs) are registered asynchronously as the client 
    // event loop processes registry global events. We must pump events for a brief period 
    // to guarantee all outputs are fully bound and reported by SDL before querying display bounds.
    for (int i = 0; i < 20; i++) {
        SDL_PumpEvents();
        SDL_Delay(15); // Total 300ms sleep warm-up
    }

    int num_displays = SDL_GetNumVideoDisplays();
    int total_w = 0, total_h = 0;
    SDL_Rect* displays = malloc(sizeof(SDL_Rect) * num_displays);

    for (int i = 0; i < num_displays; i++) {
        if (SDL_GetDisplayBounds(i, &displays[i]) == 0) {
            if (displays[i].x + displays[i].w > total_w) total_w = displays[i].x + displays[i].w;
            if (displays[i].h + displays[i].y > total_h) total_h = displays[i].h + displays[i].y;
        }
    }

    // CLI Arguments Parsing
    for (int i = 1; i < argc; i++) {
        if (strcmp(argv[i], "--help") == 0 || strcmp(argv[i], "-h") == 0) {
            print_help();
            free(displays);
            SDL_Quit();
            return 0;
        } else if (strcmp(argv[i], "--debug") == 0 || strcmp(argv[i], "-d") == 0) {
            debug_enabled = true;
        } else if (strcmp(argv[i], "--skip-cal") == 0 || strcmp(argv[i], "-s") == 0) {
            app_state = STATE_TESTING;
        } else if (strcmp(argv[i], "--index") == 0 || strcmp(argv[i], "-i") == 0) {
            if (i + 1 < argc) {
                int target_idx = atoi(argv[i + 1]);
                if (target_idx >= 0 && target_idx < num_displays) {
                    current_cal_display = target_idx;
                }
                i++;
            }
        }
    }

    if (TTF_Init() < 0) {
        printf("[SDL2_TOUCH_TEST] WARNING: Failed to initialize SDL_ttf: %s. Continuing without font rendering.\n", TTF_GetError());
    }

    printf("\n=========================================================\n");
    printf("[SDL2_TOUCH_TEST] SYSTEM DRIVER & ENV DIAGNOSTICS:\n");

    const char* video_driver = SDL_GetCurrentVideoDriver();
    printf("[SDL2_TOUCH_TEST] Active SDL Video Driver: %s\n", video_driver ? video_driver : "Unknown");
    printf("[SDL2_TOUCH_TEST] Number of detected displays: %d\n", num_displays);

    for (int i = 0; i < num_displays; i++) {
        char clean_name[128];
        clean_display_name(SDL_GetDisplayName(i), clean_name, sizeof(clean_name));
        printf("[SDL2_TOUCH_TEST]   Display %d bounds: x=%d, y=%d, w=%d, h=%d (Name: %s)\n",
               i, displays[i].x, displays[i].y, displays[i].w, displays[i].h, clean_name);
    }
    printf("[SDL2_TOUCH_TEST] Combined Virtual Desktop Canvas: %dx%d\n", total_w, total_h);

    int num_touch = SDL_GetNumTouchDevices();
    printf("\n[SDL2_TOUCH_TEST] TOUCH DEVICE DIAGNOSTICS:\n");
    printf("[SDL2_TOUCH_TEST] Number of registered touch devices: %d\n", num_touch);
    for (int i = 0; i < num_touch; i++) {
        SDL_TouchID id = SDL_GetTouchDevice(i);
        printf("[SDL2_TOUCH_TEST]   Touch Device %d - ID: %lld (Name: %s)\n", i, (long long)id, SDL_GetTouchName(i));
    }
    printf("=========================================================\n\n");

    SDL_Window* window = SDL_CreateWindow("Agnostic SDL Touch Test", 0, 0, total_w, total_h, SDL_WINDOW_BORDERLESS | SDL_WINDOW_SHOWN);
    if (!window) {
        printf("[SDL2_TOUCH_TEST] ERROR: Failed to create window: %s\n", SDL_GetError());
        free(displays);
        SDL_Quit();
        return 1;
    }

    SDL_Renderer* renderer = SDL_CreateRenderer(window, -1, SDL_RENDERER_ACCELERATED | SDL_RENDERER_PRESENTVSYNC);
    if (!renderer) {
        printf("[SDL2_TOUCH_TEST] ERROR: Failed to create renderer: %s\n", SDL_GetError());
        SDL_DestroyWindow(window);
        free(displays);
        SDL_Quit();
        return 1;
    }

    // Enable renderer alpha blending for semi-transparent color overlays
    SDL_SetRenderDrawBlendMode(renderer, SDL_BLENDMODE_BLEND);

    // Warm-up and map Wayland Surface (resolves target-drawing initialization errors)
    for (int i = 0; i < 10; i++) {
        SDL_PumpEvents();
        SDL_SetRenderDrawColor(renderer, 0, 0, 0, 255);
        SDL_RenderClear(renderer);
        SDL_RenderPresent(renderer);
        SDL_Delay(20); // Hold for 200ms total loop sequence
    }

    TTF_Font* font = load_system_font();
    if (!font) {
        printf("[SDL2_TOUCH_TEST] WARNING: Could not load default Truetype system font. Labels will not be rendered on screen.\n");
    }

    // Allocate calibration memory for all displays
    DisplayCalibration* cal_results = calloc(num_displays, sizeof(DisplayCalibration));
    for (int i = 0; i < num_displays; i++) {
        strncpy(cal_results[i].touch_name, "Generic Touch Screen", sizeof(cal_results[i].touch_name) - 1);
        cal_results[i].calibrated = false;
    }

    // Configure the baseline targets for the target current_cal_display (safely computed after display sync)
    SDL_Rect bounds = displays[current_cal_display];
    target_points[0] = (Point2D){ (double)(bounds.x + 0.1 * bounds.w) / total_w, (double)(bounds.y + 0.1 * bounds.h) / total_h }; // Top-Left
    target_points[1] = (Point2D){ (double)(bounds.x + 0.9 * bounds.w) / total_w, (double)(bounds.y + 0.1 * bounds.h) / total_h }; // Top-Right
    target_points[2] = (Point2D){ (double)(bounds.x + 0.1 * bounds.w) / total_w, (double)(bounds.y + 0.9 * bounds.h) / total_h }; // Bottom-Left
    target_points[3] = (Point2D){ (double)(bounds.x + 0.9 * bounds.w) / total_w, (double)(bounds.y + 0.9 * bounds.h) / total_h }; // Bottom-Right

    bool running = true;
    SDL_Event event;
    int last_raw_x = -1, last_raw_y = -1;
    int last_cal_x = -1, last_cal_y = -1;

    while (running) {
        while (SDL_PollEvent(&event)) {
            if (event.type == SDL_QUIT) {
                running = false;
            } else if (event.type == SDL_KEYDOWN) {
                if (event.key.keysym.sym == SDLK_ESCAPE) {
                    running = false;
                } else if (event.key.keysym.sym == SDLK_c && app_state == STATE_TESTING) {
                    current_cal_display = 0;
                    calibration_step = 0;
                    app_state = STATE_CALIBRATING;
                } else if (event.key.keysym.sym == SDLK_r && app_state == STATE_VERIFYING) {
                    app_state = STATE_CALIBRATING;
                    calibration_step = 0;
                } else if (event.key.keysym.sym == SDLK_RETURN && app_state == STATE_VERIFYING) {
                    cal_results[current_cal_display].A = matrix_A;
                    cal_results[current_cal_display].B = matrix_B;
                    cal_results[current_cal_display].C = matrix_C;
                    cal_results[current_cal_display].D = matrix_D;
                    cal_results[current_cal_display].E = matrix_E;
                    cal_results[current_cal_display].F = matrix_F;
                    cal_results[current_cal_display].calibrated = true;

                    if (current_cal_display + 1 < num_displays) {
                        current_cal_display++;
                        calibration_step = 0;
                        app_state = STATE_CALIBRATING;

                        SDL_Rect next_bounds = displays[current_cal_display];
                        target_points[0] = (Point2D){ (double)(next_bounds.x + 0.1 * next_bounds.w) / total_w, (double)(next_bounds.y + 0.1 * next_bounds.h) / total_h };
                        target_points[1] = (Point2D){ (double)(next_bounds.x + 0.9 * next_bounds.w) / total_w, (double)(next_bounds.y + 0.1 * next_bounds.h) / total_h };
                        target_points[2] = (Point2D){ (double)(next_bounds.x + 0.1 * next_bounds.w) / total_w, (double)(next_bounds.y + 0.9 * next_bounds.h) / total_h };
                        target_points[3] = (Point2D){ (double)(next_bounds.x + 0.9 * next_bounds.w) / total_w, (double)(next_bounds.y + 0.9 * next_bounds.h) / total_h };
                    } else {
                        print_all_calibration_rules(displays, num_displays, cal_results);
                        // Transition to TESTING state instead of exiting so users can test calibrated swiping on the fly
                        app_state = STATE_TESTING;
                        all_calibrated = true;
                        last_raw_x = -1; last_raw_y = -1;
                        last_cal_x = -1; last_cal_y = -1;
                    }
                }
            } else if (event.type == SDL_FINGERDOWN || event.type == SDL_FINGERMOTION) {
                const char* active_name = get_touch_name_by_id(event.tfinger.touchId);
                if (active_name) {
                    strncpy(cal_results[current_cal_display].touch_name, active_name, sizeof(cal_results[current_cal_display].touch_name) - 1);
                }

                double rx = event.tfinger.x;
                double ry = event.tfinger.y;

                // Hit test checks inside Verification Mode to capture custom Red/Green button taps
                bool ui_element_tapped = false;
                if (app_state == STATE_VERIFYING && event.type == SDL_FINGERDOWN) {
                    SDL_Rect cur_bounds = displays[current_cal_display];
                    SDL_Rect retry_btn = { cur_bounds.x + cur_bounds.w / 4 - 80, cur_bounds.y + cur_bounds.h / 2 + 40, 160, 45 };
                    SDL_Rect accept_btn = { cur_bounds.x + 3 * cur_bounds.w / 4 - 80, cur_bounds.y + cur_bounds.h / 2 + 40, 160, 45 };

                    int tx = (int)(rx * total_w);
                    int ty = (int)(ry * total_h);

                    if (tx >= retry_btn.x && tx < retry_btn.x + retry_btn.w &&
                        ty >= retry_btn.y && ty < retry_btn.y + retry_btn.h) {
                        ui_element_tapped = true;
                        app_state = STATE_CALIBRATING;
                        calibration_step = 0;
                    } else if (tx >= accept_btn.x && tx < accept_btn.x + accept_btn.w &&
                               ty >= accept_btn.y && ty < accept_btn.y + accept_btn.h) {
                        ui_element_tapped = true;

                        cal_results[current_cal_display].A = matrix_A;
                        cal_results[current_cal_display].B = matrix_B;
                        cal_results[current_cal_display].C = matrix_C;
                        cal_results[current_cal_display].D = matrix_D;
                        cal_results[current_cal_display].E = matrix_E;
                        cal_results[current_cal_display].F = matrix_F;
                        cal_results[current_cal_display].calibrated = true;

                        if (current_cal_display + 1 < num_displays) {
                            current_cal_display++;
                            calibration_step = 0;
                            app_state = STATE_CALIBRATING;

                            SDL_Rect next_bounds = displays[current_cal_display];
                            target_points[0] = (Point2D){ (double)(next_bounds.x + 0.1 * next_bounds.w) / total_w, (double)(next_bounds.y + 0.1 * next_bounds.h) / total_h };
                            target_points[1] = (Point2D){ (double)(next_bounds.x + 0.9 * next_bounds.w) / total_w, (double)(next_bounds.y + 0.1 * next_bounds.h) / total_h };
                            target_points[2] = (Point2D){ (double)(next_bounds.x + 0.1 * next_bounds.w) / total_w, (double)(next_bounds.y + 0.9 * next_bounds.h) / total_h };
                            target_points[3] = (Point2D){ (double)(next_bounds.x + 0.9 * next_bounds.w) / total_w, (double)(next_bounds.y + 0.9 * next_bounds.h) / total_h };
                        } else {
                            print_all_calibration_rules(displays, num_displays, cal_results);
                            // Transition to TESTING state instead of exiting so users can test calibrated swiping on the fly
                            app_state = STATE_TESTING;
                            all_calibrated = true;
                            last_raw_x = -1; last_raw_y = -1;
                            last_cal_x = -1; last_cal_y = -1;
                        }
                    }
                }

                if (!ui_element_tapped) {
                    if (app_state == STATE_TESTING) {
                        last_raw_x = (int)(rx * total_w);
                        last_raw_y = (int)(ry * total_h);

                        int mapped_idx = -1;
                        for (int i = 0; i < num_displays; i++) {
                            if (last_raw_x >= displays[i].x && last_raw_x < displays[i].x + displays[i].w &&
                                last_raw_y >= displays[i].y && last_raw_y < displays[i].y + displays[i].h) {
                                mapped_idx = i;
                                break;
                            }
                        }

                        // Apply the corresponding rounded calibration matrix dynamically per screen in testing mode
                        if (mapped_idx != -1 && cal_results[mapped_idx].calibrated) {
                            double cal_x = smart_round(cal_results[mapped_idx].A) * rx +
                                           smart_round(cal_results[mapped_idx].B) * ry +
                                           smart_round(cal_results[mapped_idx].C);
                            double cal_y = smart_round(cal_results[mapped_idx].D) * rx +
                                           smart_round(cal_results[mapped_idx].E) * ry +
                                           smart_round(cal_results[mapped_idx].F);
                            
                            last_cal_x = (int)(cal_x * total_w);
                            last_cal_y = (int)(cal_y * total_h);
                        } else {
                            last_cal_x = last_raw_x;
                            last_cal_y = last_raw_y;
                        }

                        if (debug_enabled) {
                            printf("[SDL2_TOUCH_TEST] %s: touchId=%lld | norm_x=%.4f, norm_y=%.4f | px=%d, py=%d -> DISPLAY: %d\n",
                                   (event.type == SDL_FINGERDOWN) ? "DOWN" : "MOVE",
                                   (long long)event.tfinger.touchId, rx, ry, last_raw_x, last_raw_y, mapped_idx);
                        }
                    } else if (app_state == STATE_CALIBRATING && event.type == SDL_FINGERDOWN) {
                        raw_points[calibration_step] = (Point2D){ rx, ry };
                        if (debug_enabled) {
                            printf("[SDL2_TOUCH_TEST] CALIB CLICK %d: raw_norm_x=%.4f, raw_norm_y=%.4f | target_norm_x=%.4f, target_norm_y=%.4f\n",
                                   calibration_step, rx, ry, target_points[calibration_step].x, target_points[calibration_step].y);
                        }

                        calibration_step++;
                        if (calibration_step == 4) {
                            if (calculate_calibration_matrix()) {
                                app_state = STATE_VERIFYING;
                            } else {
                                calibration_step = 0;
                            }
                        }
                    } else if (app_state == STATE_VERIFYING) {
                        // Apply smart-rounded coefficients during verification rendering
                        double cal_x = smart_round(matrix_A) * rx + smart_round(matrix_B) * ry + smart_round(matrix_C);
                        double cal_y = smart_round(matrix_D) * rx + smart_round(matrix_E) * ry + smart_round(matrix_F);

                        last_raw_x = (int)(rx * total_w);
                        last_raw_y = (int)(ry * total_h);
                        last_cal_x = (int)(cal_x * total_w);
                        last_cal_y = (int)(cal_y * total_h);

                        if (debug_enabled) {
                            printf("[SDL2_TOUCH_TEST] LIVE VERIFY: raw_x=%d, raw_y=%d | cal_x=%d, cal_y=%d\n",
                                   last_raw_x, last_raw_y, last_cal_x, last_cal_y);
                        }
                    }
                }
            }
        }

        SDL_SetRenderDrawColor(renderer, 0, 0, 0, 255);
        SDL_RenderClear(renderer);

        SDL_Color text_color = {255, 255, 255, 255};

        // Render base color display boundaries for all screens underneath active states
        for (int i = 0; i < num_displays; i++) {
            SDL_Color c = DISPLAY_COLORS[i % NUM_COLORS];
            SDL_SetRenderDrawColor(renderer, c.r, c.g, c.b, c.a);
            SDL_RenderFillRect(renderer, &displays[i]);

            char clean_name[128];
            clean_display_name(SDL_GetDisplayName(i), clean_name, sizeof(clean_name));

            char label_buf[192];
            snprintf(label_buf, sizeof(label_buf), "%s (Display %d)", clean_name, i);
            draw_label(renderer, font, label_buf, displays[i].x + displays[i].w / 2, displays[i].y + displays[i].h / 2, text_color, true);
        }

        if (app_state == STATE_TESTING) {
            if (all_calibrated) {
                draw_wrapped_text(renderer, font, "CALIBRATION COMPLETE. Swiping test active (Yellow pointer maps calibrated, Gray crosses map raw). Press ESC to exit.",
                                  total_w / 2, 30, total_w - 40, text_color);
            } else {
                draw_wrapped_text(renderer, font, "NORMAL DIAGNOSTIC MODE. Touch to map yellow block. Press 'C' to start 4-point calibration on display 0.",
                                  total_w / 2, 30, total_w - 40, text_color);
            }

            if (last_raw_x != -1 && last_raw_y != -1) {
                if (all_calibrated) {
                    // Draw raw tracking crosshair
                    SDL_SetRenderDrawColor(renderer, 150, 150, 150, 255);
                    SDL_RenderDrawLine(renderer, last_raw_x - 10, last_raw_y, last_raw_x + 10, last_raw_y);
                    SDL_RenderDrawLine(renderer, last_raw_x, last_raw_y - 10, last_raw_x, last_raw_y + 10);
                    
                    // Draw calibrated yellow pointer
                    SDL_Rect indicator = {last_cal_x - 12, last_cal_y - 12, 24, 24};
                    SDL_SetRenderDrawColor(renderer, 255, 255, 0, 255);
                    SDL_RenderFillRect(renderer, &indicator);
                } else {
                    // Default uncalibrated yellow box
                    SDL_Rect indicator = {last_raw_x - 12, last_raw_y - 12, 24, 24};
                    SDL_SetRenderDrawColor(renderer, 255, 255, 0, 255);
                    SDL_RenderFillRect(renderer, &indicator);
                }
            }
        } else if (app_state == STATE_CALIBRATING) {
            SDL_Rect current_bounds = displays[current_cal_display];
            
            // Highlight target screen with a solid flashing frame border
            bool is_flash_on = (SDL_GetTicks() / 250) % 2 == 0;
            SDL_Color border_col = is_flash_on ? (SDL_Color){255, 255, 0, 255} : (SDL_Color){255, 255, 255, 255};
            draw_thick_border(renderer, current_bounds, 6, border_col);

            // Dynamically scale text width inside target display boundary (placed in center zone to avoid overlap)
            draw_wrapped_text(renderer, font, "TOUCHSCREEN CALIBRATION: Tap precisely on the center of the flashing target",
                              current_bounds.x + current_bounds.w / 2, current_bounds.y + current_bounds.h / 3, current_bounds.w - 40, text_color);

            int tx = (int)(target_points[calibration_step].x * total_w);
            int ty = (int)(target_points[calibration_step].y * total_h);

            int radius = 20 + (int)(5 * sin(SDL_GetTicks() * 0.01));
            SDL_SetRenderDrawColor(renderer, 255, 0, 0, 255);
            SDL_RenderDrawLine(renderer, tx - radius, ty, tx + radius, ty);
            SDL_RenderDrawLine(renderer, tx, ty - radius, tx, ty + radius);

            SDL_Rect box = { tx - 6, ty - 6, 12, 12 };
            SDL_SetRenderDrawColor(renderer, 255, 255, 0, 255);
            SDL_RenderFillRect(renderer, &box);

            char step_lbl[32];
            snprintf(step_lbl, sizeof(step_lbl), "Point %d of 4", calibration_step + 1);
            draw_label(renderer, font, step_lbl, tx, ty - radius - 15, text_color, true);
        } else if (app_state == STATE_VERIFYING) {
            SDL_Rect current_bounds = displays[current_cal_display];
            
            // Highlight target screen verification frame
            SDL_Color verify_col = {50, 255, 50, 255};
            draw_thick_border(renderer, current_bounds, 6, verify_col);

            draw_wrapped_text(renderer, font, "CALIBRATION PREVIEW: Drag your finger across the display to test alignment. Tap Red to Retry, or Green to Save.",
                              current_bounds.x + current_bounds.w / 2, current_bounds.y + current_bounds.h / 3, current_bounds.w - 40, text_color);

            // Retry UI Target Tap Button (moved vertically to prevent overlaps)
            SDL_Rect retry_btn = { current_bounds.x + current_bounds.w / 4 - 80, current_bounds.y + current_bounds.h / 2 + 40, 160, 45 };
            SDL_SetRenderDrawColor(renderer, 200, 50, 50, 255);
            SDL_RenderFillRect(renderer, &retry_btn);
            draw_label(renderer, font, "RETRY", retry_btn.x + retry_btn.w / 2, retry_btn.y + retry_btn.h / 2, text_color, true);

            // Accept UI Save Tap Button (moved vertically to prevent overlaps)
            SDL_Rect accept_btn = { current_bounds.x + 3 * current_bounds.w / 4 - 80, current_bounds.y + current_bounds.h / 2 + 40, 160, 45 };
            SDL_SetRenderDrawColor(renderer, 50, 180, 50, 255);
            SDL_RenderFillRect(renderer, &accept_btn);

            if (current_cal_display + 1 < num_displays) {
                draw_label(renderer, font, "SAVE & NEXT", accept_btn.x + accept_btn.w / 2, accept_btn.y + accept_btn.h / 2, text_color, true);
            } else {
                draw_label(renderer, font, "SAVE & EXIT", accept_btn.x + accept_btn.w / 2, accept_btn.y + accept_btn.h / 2, text_color, true);
            }

            if (last_raw_x != -1 && last_raw_y != -1) {
                SDL_SetRenderDrawColor(renderer, 220, 220, 220, 255);
                SDL_RenderDrawLine(renderer, last_raw_x - 10, last_raw_y, last_raw_x + 10, last_raw_y);
                SDL_RenderDrawLine(renderer, last_raw_x, last_raw_y - 10, last_raw_x, last_raw_y + 10);
                draw_label(renderer, font, "Raw", last_raw_x, last_raw_y + 15, text_color, true);

                SDL_Rect cal_box = { last_cal_x - 8, last_cal_y - 8, 16, 16 };
                SDL_SetRenderDrawColor(renderer, 255, 255, 0, 255);
                SDL_RenderFillRect(renderer, &cal_box);
                draw_label(renderer, font, "Calibrated", last_cal_x, last_cal_y - 18, text_color, true);
            }
        }

        SDL_RenderPresent(renderer);
    }

    if (font) TTF_CloseFont(font);
    TTF_Quit();

    free(cal_results);
    free(displays);
    SDL_DestroyRenderer(renderer);
    SDL_DestroyWindow(window);
    SDL_Quit();
    printf("\n[SDL2_TOUCH_TEST] Test closed successfully.\n");
    return 0;
}
