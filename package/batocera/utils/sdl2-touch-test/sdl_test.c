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
#include <stdio.h>
#include <stdbool.h>

// Simple color pallete to dynamically distinguish separate displays
const SDL_Color DISPLAY_COLORS[] = {
    {180, 0, 0, 255},    // Red (Display 0)
    {0, 150, 0, 255},    // Green (Display 1)
    {0, 0, 180, 255},    // Blue (Display 2)
    {150, 0, 150, 255},  // Purple (Display 3)
    {0, 150, 150, 255}   // Teal (Display 4)
};
const int NUM_COLORS = 5;

int main(int argc, char* argv[]) {
    // Initialize SDL2 Video and Input Events
    if (SDL_Init(SDL_INIT_VIDEO | SDL_INIT_EVENTS) < 0) {
        printf("[SDL_TEST] ERROR: Failed to initialize SDL: %s\n", SDL_GetError());
        return 1;
    }

    printf("\n=========================================================\n");
    printf("[SDL_TEST] SYSTEM DRIVER & ENV DIAGNOSTICS:\n");
    
    // Log the active video driver (verifies native Wayland vs XWayland/X11)
    const char* video_driver = SDL_GetCurrentVideoDriver();
    printf("[SDL_TEST] Active SDL Video Driver: %s\n", video_driver ? video_driver : "Unknown");

    // Query and Log Display Geometry dynamically
    int num_displays = SDL_GetNumVideoDisplays();
    printf("[SDL_TEST] Number of detected displays: %d\n", num_displays);
    
    int total_w = 0, total_h = 0;
    SDL_Rect* displays = malloc(sizeof(SDL_Rect) * num_displays);

    for (int i = 0; i < num_displays; i++) {
        if (SDL_GetDisplayBounds(i, &displays[i]) == 0) {
            printf("[SDL_TEST]   Display %d bounds: x=%d, y=%d, w=%d, h=%d\n", 
                   i, displays[i].x, displays[i].y, displays[i].w, displays[i].h);
            
            // Calculate total bounding box of the virtual desktop
            if (displays[i].x + displays[i].w > total_w) total_w = displays[i].x + displays[i].w;
            if (displays[i].h + displays[i].y > total_h) total_h = displays[i].h + displays[i].y;
        }
    }
    printf("[SDL_TEST] Combined Virtual Desktop Canvas: %dx%d\n", total_w, total_h);

    // Query and Log Registered Touch Devices
    int num_touch = SDL_GetNumTouchDevices();
    printf("\n[SDL_TEST] TOUCH DEVICE DIAGNOSTICS:\n");
    printf("[SDL_TEST] Number of registered touch devices: %d\n", num_touch);
    for (int i = 0; i < num_touch; i++) {
        SDL_TouchID id = SDL_GetTouchDevice(i);
        printf("[SDL_TEST]   Touch Device %d - ID: %lld\n", i, (long long)id);
    }
    printf("=========================================================\n\n");

    // Create Window covering the entire virtual desktop area
    SDL_Window* window = SDL_CreateWindow("Agnostic SDL Touch Test", 0, 0, total_w, total_h, SDL_WINDOW_BORDERLESS | SDL_WINDOW_SHOWN);
    if (!window) {
        printf("[SDL_TEST] ERROR: Failed to create window: %s\n", SDL_GetError());
        free(displays);
        SDL_Quit();
        return 1;
    }

    SDL_Renderer* renderer = SDL_CreateRenderer(window, -1, SDL_RENDERER_ACCELERATED | SDL_RENDERER_PRESENTVSYNC);
    if (!renderer) {
        printf("[SDL_TEST] ERROR: Failed to create renderer: %s\n", SDL_GetError());
        SDL_DestroyWindow(window);
        free(displays);
        SDL_Quit();
        return 1;
    }
    // Initialize SDL2 Video and Input Events
    // Compares window size to physical renderer output (detects compositor-side High-DPI scaling)
    int win_w, win_h, out_w, out_h;
    SDL_GetWindowSize(window, &win_w, &win_h);
    SDL_GetRendererOutputSize(renderer, &out_w, &out_h);
    printf("[SDL_TEST] Window Size: %dx%d | Physical Framebuffer Output: %dx%d\n", win_w, win_h, out_w, out_h);
    if (win_w != out_w || win_h != out_h) {
        printf("[SDL_TEST] NOTE: High-DPI/Compositor scaling is active (Scale multiplier: %.2fx)\n", (float)out_w / win_w);
    }

    printf("\n[SDL_TEST] TEST WINDOW IS LIVE. PRESS 'ESC' IN SSH TO QUIT.\n");
    printf("[SDL_TEST] MONITORING LIVE TOUCH EVENTS...\n\n");

    bool running = true;
    SDL_Event event;
    int last_touch_x = -1;
    int last_touch_y = -1;

    while (running) {
        while (SDL_PollEvent(&event)) {
            if (event.type == SDL_QUIT) {
                running = false;
            } else if (event.type == SDL_KEYDOWN) {
                if (event.key.keysym.sym == SDLK_ESCAPE) {
                    running = false;
                }
            } else if (event.type == SDL_FINGERDOWN || event.type == SDL_FINGERMOTION) {
                // Map the normalized coordinates (0.0 to 1.0) directly across our virtual canvas width/height
                int px = (int)(event.tfinger.x * total_w);
                int py = (int)(event.tfinger.y * total_h);

                // Dynamically find which physical display bounds the mapped coordinate falls into
                int mapped_display_idx = -1;
                for (int i = 0; i < num_displays; i++) {
                    if (px >= displays[i].x && px < displays[i].x + displays[i].w &&
                        py >= displays[i].y && py < displays[i].y + displays[i].h) {
                        mapped_display_idx = i;
                        break;
                    }
                }

                printf("[SDL_TEST] %s: touchId=%lld | normalized_x=%.4f, normalized_y=%.4f | mapped_x=%d, mapped_y=%d -> MAPPED TO DISPLAY: %d\n",
                       (event.type == SDL_FINGERDOWN) ? "DOWN" : "MOVE",
                       (long long)event.tfinger.touchId,
                       event.tfinger.x, event.tfinger.y,
                       px, py, mapped_display_idx);

                last_touch_x = px;
                last_touch_y = py;
            }
        }

        // Draw the background
        SDL_SetRenderDrawColor(renderer, 0, 0, 0, 255);
        SDL_RenderClear(renderer);

        // Dynamically color each screen's bounds with a unique color
        for (int i = 0; i < num_displays; i++) {
            SDL_Color c = DISPLAY_COLORS[i % NUM_COLORS];
            SDL_SetRenderDrawColor(renderer, c.r, c.g, c.b, c.a);
            SDL_RenderFillRect(renderer, &displays[i]);
        }

        // Draw a yellow circle/square where touched
        if (last_touch_x != -1 && last_touch_y != -1) {
            SDL_Rect indicator = {last_touch_x - 12, last_touch_y - 12, 24, 24};
            SDL_SetRenderDrawColor(renderer, 255, 255, 0, 255);
            SDL_RenderFillRect(renderer, &indicator);
        }

        SDL_RenderPresent(renderer);
    }

    free(displays);
    SDL_DestroyRenderer(renderer);
    SDL_DestroyWindow(window);
    SDL_Quit();
    printf("\n[SDL_TEST] Test closed successfully.\n");
    return 0;
}
