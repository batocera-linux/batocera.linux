#define _GNU_SOURCE
#include <dlfcn.h>
#include <SDL2/SDL.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>

// --- Minimal GLES2 types and constants (no libGLESv2 header dependency) ---
typedef unsigned int  GLenum;
typedef unsigned int  GLuint;
typedef int           GLint;
typedef int           GLsizei;
typedef unsigned char GLboolean;
typedef float         GLfloat;
typedef char          GLchar;
typedef void          GLvoid;

#define GL_FALSE                0
#define GL_FRAGMENT_SHADER      0x8B30
#define GL_VERTEX_SHADER        0x8B31
#define GL_COMPILE_STATUS       0x8B81
#define GL_LINK_STATUS          0x8B82
#define GL_TEXTURE_2D           0x0DE1
#define GL_TEXTURE_MIN_FILTER   0x2801
#define GL_TEXTURE_MAG_FILTER   0x2800
#define GL_NEAREST              0x2600
#define GL_LINEAR               0x2601
#define GL_VIEWPORT             0x0BA2
#define GL_CURRENT_PROGRAM      0x8B8D
#define GL_ARRAY_BUFFER         0x8892
#define GL_ARRAY_BUFFER_BINDING 0x8894
#define GL_FLOAT                0x1406
#define GL_TRIANGLE_STRIP       0x0005
#define GL_BLEND                0x0BE2
#define GL_SCISSOR_TEST         0x0C11

// --- GLES2 function pointers resolved at runtime ---
static GLuint (*p_glCreateShader)(GLenum) = NULL;
static void (*p_glShaderSource)(GLuint, GLsizei, const GLchar *const *, const GLint *) = NULL;
static void (*p_glCompileShader)(GLuint) = NULL;
static void (*p_glGetShaderiv)(GLuint, GLenum, GLint *) = NULL;
static void (*p_glDeleteShader)(GLuint) = NULL;
static GLuint (*p_glCreateProgram)(void) = NULL;
static void (*p_glAttachShader)(GLuint, GLuint) = NULL;
static void (*p_glBindAttribLocation)(GLuint, GLuint, const GLchar *) = NULL;
static void (*p_glLinkProgram)(GLuint) = NULL;
static void (*p_glGetProgramiv)(GLuint, GLenum, GLint *) = NULL;
static void (*p_glDeleteProgram)(GLuint) = NULL;
static GLint (*p_glGetUniformLocation)(GLuint, const GLchar *) = NULL;
static void (*p_glUniform1i)(GLint, GLint) = NULL;
static void (*p_glUniform2f)(GLint, GLfloat, GLfloat) = NULL;
static void (*p_glTexParameteri)(GLenum, GLenum, GLint) = NULL;
static void (*p_glGetIntegerv)(GLenum, GLint *) = NULL;
static void (*p_glViewport)(GLint, GLint, GLsizei, GLsizei) = NULL;
static void (*p_glUseProgram)(GLuint) = NULL;
static void (*p_glBindBuffer)(GLenum, GLuint) = NULL;
static void (*p_glEnableVertexAttribArray)(GLuint) = NULL;
static void (*p_glDisableVertexAttribArray)(GLuint) = NULL;
static void (*p_glVertexAttribPointer)(GLuint, GLint, GLenum, GLboolean, GLsizei, const GLvoid *) = NULL;
static void (*p_glDrawArrays)(GLenum, GLint, GLsizei) = NULL;
static void (*p_glEnable)(GLenum) = NULL;
static void (*p_glDisable)(GLenum) = NULL;

// --- Shader state ---
#define SHADER_NONE 0 // No shader; use GL's built-in bilinear filtering (default)
#define SHADER_SHARP_BILINEAR 1
#define SHADER_SHARP_SHIMMERLESS 2
#define SHADER_QUILEZ 3
#define SHADER_SCANLINES 4
#define SHADER_LCD3X 5

static int shader_mode = SHADER_NONE;
static int gl_renderer_desktop = 0; // 1 when SDL uses "opengl" renderer (not "opengles2")
static GLuint shader_program = 0;
static GLint loc_texture = -1;
static GLint loc_texture_size = -1;
static GLint loc_output_size = -1; // sharp-bilinear only
static int shader_frame_calls = 0;

// --- DS / window state (declared before all functions that use them) ---
static int ds_screen_width = 256;
static int ds_screen_height = 192;
static int last_x = -1;
static int last_y = -1;
static int xy_idx = 0;
static int phys_width = -1;
static int phys_height = -1;
static int logical_width = -1;
static int logical_height = -1;
static int actual_touch = 0;

// --- Dynamic screen bounding geometry resolved at runtime ---
static SDL_Rect display0_rect = {0, 0, 0, 0};
static SDL_Rect display1_rect = {0, 0, 0, 0};
static int has_display_rects = 0;
static int num_displays = 0;

// --- Microphone monitoring ---
static SDL_AudioDeviceID mic_device = 0;
static int mic_key_held = 0;
static float mic_threshold = 0.0f;
static int mic_enabled = 0;
static float mic_baseline = 0.0f;
static int mic_baseline_samples = 0;

static SDL_Texture* screens[4];
static SDL_Texture* stylus_tex[2];
static SDL_Rect touch_rect_storage = {0};
static SDL_Rect* touch_rect = NULL;

// --- SDL2 real function pointers ---
static SDL_Renderer* renderer = NULL;
static SDL_Window* (*real_SDL_CreateWindow)(const char*, int, int, int, int, Uint32) = NULL;
static void (*real_SDL_SetWindowSize)(SDL_Window* window, int w, int h) = NULL;
static SDL_Renderer* (*real_SDL_CreateRenderer)(SDL_Window*, int, Uint32) = NULL;
static int (*real_SDL_RenderSetLogicalSize)(SDL_Renderer*, int, int) = NULL;
static SDL_Texture* (*real_SDL_CreateTexture)(SDL_Renderer*, Uint32, int, int, int) = NULL;
static int (*real_SDL_RenderCopy)(SDL_Renderer*, SDL_Texture*, const SDL_Rect*, const SDL_Rect*) = NULL;
static int (*real_SDL_PollEvent)(SDL_Event*) = NULL;
static int (*real_SDL_PushEvent)(SDL_Event*) = NULL;
static Uint32 (*real_SDL_WasInit)(Uint32) = NULL;
static int (*real_SDL_InitSubSystem)(Uint32) = NULL;
static SDL_AudioDeviceID (*real_SDL_OpenAudioDevice)(const char*, int, const SDL_AudioSpec*, SDL_AudioSpec*, int) = NULL;
static void (*real_SDL_PauseAudioDevice)(SDL_AudioDeviceID, int) = NULL;
static void (*real_SDL_CloseAudioDevice)(SDL_AudioDeviceID) = NULL;
static int (*real_SDL_GetNumAudioDevices)(int) = NULL;
static const char* (*real_SDL_GetAudioDeviceName)(int, int) = NULL;
static void (*real_SDL_RenderPresent)(SDL_Renderer*) = NULL;

// ---------------------------------------------------------------------------
// GLES2 runtime loader
// ---------------------------------------------------------------------------

static void init_gl_funcs(void) {
    // SDL_GL_GetProcAddress resolves against the GL context SDL is actually using.
    // This works on both libmali (GLES2) and Mesa/panfrost regardless of whether
    // SDL picked the GLES2 or OpenGL renderer, unlike dlsym on libGLESv2.so.2
    // which can return stubs that dispatch to the wrong EGL API on Mesa.
#define GLSYM(name) p_##name = (void *)SDL_GL_GetProcAddress(#name)
    GLSYM(glCreateShader);
    GLSYM(glShaderSource);
    GLSYM(glCompileShader);
    GLSYM(glGetShaderiv);
    GLSYM(glDeleteShader);
    GLSYM(glCreateProgram);
    GLSYM(glAttachShader);
    GLSYM(glBindAttribLocation);
    GLSYM(glLinkProgram);
    GLSYM(glGetProgramiv);
    GLSYM(glDeleteProgram);
    GLSYM(glGetUniformLocation);
    GLSYM(glUniform1i);
    GLSYM(glUniform2f);
    GLSYM(glTexParameteri);
    GLSYM(glGetIntegerv);
    GLSYM(glViewport);
    GLSYM(glUseProgram);
    GLSYM(glBindBuffer);
    GLSYM(glEnableVertexAttribArray);
    GLSYM(glDisableVertexAttribArray);
    GLSYM(glVertexAttribPointer);
    GLSYM(glDrawArrays);
    GLSYM(glEnable);
    GLSYM(glDisable);
#undef GLSYM
    if (!p_glCreateShader) {
        // SDL_GL_GetProcAddress failed (no GL context yet, or software renderer).
        // Fall back to RTLD_DEFAULT to catch any GLES2 symbols already in process.
#define GLSYM(name) if (!p_##name) p_##name = (void *)dlsym(RTLD_DEFAULT, #name)
        GLSYM(glCreateShader);
        GLSYM(glShaderSource);
        GLSYM(glCompileShader);
        GLSYM(glGetShaderiv);
        GLSYM(glDeleteShader);
        GLSYM(glCreateProgram);
        GLSYM(glAttachShader);
        GLSYM(glBindAttribLocation);
        GLSYM(glLinkProgram);
        GLSYM(glGetProgramiv);
        GLSYM(glDeleteProgram);
        GLSYM(glGetUniformLocation);
        GLSYM(glUniform1i);
        GLSYM(glUniform2f);
        GLSYM(glTexParameteri);
        GLSYM(glGetIntegerv);
        GLSYM(glViewport);
        GLSYM(glUseProgram);
        GLSYM(glBindBuffer);
        GLSYM(glEnableVertexAttribArray);
        GLSYM(glDisableVertexAttribArray);
        GLSYM(glVertexAttribPointer);
        GLSYM(glDrawArrays);
        GLSYM(glEnable);
        GLSYM(glDisable);
#undef GLSYM
    }
}

// ---------------------------------------------------------------------------
// Shader GLSL sources
// ---------------------------------------------------------------------------

// Vertex shader shared by both filter shaders
static const char *VERT_SRC =
    "attribute vec2 a_position;\n"
    "attribute vec2 a_texcoord;\n"
    "varying vec2 v_texcoord;\n"
    "void main() {\n"
    "    gl_Position = vec4(a_position, 0.0, 1.0);\n"
    "    v_texcoord = a_texcoord;\n"
    "}\n";

// Themaister sharp-bilinear with minimum prescale of 2.
// Minimum of 2 ensures correct behaviour with Hi-Res 3D (512×384→640×480)
// where floor(scale)=1 would otherwise fall back to pure bilinear.
static const char *FRAG_SHARP_BILINEAR =
    "precision mediump float;\n"
    "varying vec2 v_texcoord;\n"
    "uniform sampler2D u_texture;\n"
    "uniform vec2 u_texture_size;\n"
    "uniform vec2 u_output_size;\n"
    "void main() {\n"
    "    vec2 scale = max(vec2(2.0), floor(u_output_size / u_texture_size));\n"
    "    vec2 texel = v_texcoord * u_texture_size;\n"
    "    vec2 texel_floored = floor(texel);\n"
    "    vec2 s = fract(texel);\n"
    "    vec2 region_range = 0.5 - 0.5 / scale;\n"
    "    vec2 center_dist = s - 0.5;\n"
    "    vec2 f = (center_dist - clamp(center_dist, -region_range, region_range)) * scale + 0.5;\n"
    "    vec2 mod_texel = texel_floored + f;\n"
    "    gl_FragColor = SWIZ(texture2D(u_texture, mod_texel / u_texture_size));\n"
    "}\n";

// Scanlines: sharp-bilinear-2x base with every other output row darkened
static const char *FRAG_SCANLINES =
    "precision mediump float;\n"
    "varying vec2 v_texcoord;\n"
    "uniform sampler2D u_texture;\n"
    "uniform vec2 u_texture_size;\n"
    "uniform vec2 u_output_size;\n"
    "void main() {\n"
    "    vec2 scale = max(vec2(2.0), floor(u_output_size / u_texture_size));\n"
    "    vec2 texel = v_texcoord * u_texture_size;\n"
    "    vec2 texel_floored = floor(texel);\n"
    "    vec2 s = fract(texel);\n"
    "    vec2 region_range = 0.5 - 0.5 / scale;\n"
    "    vec2 center_dist = s - 0.5;\n"
    "    vec2 f = (center_dist - clamp(center_dist, -region_range, region_range)) * scale + 0.5;\n"
    "    vec2 mod_texel = texel_floored + f;\n"
    "    vec4 color = SWIZ(texture2D(u_texture, mod_texel / u_texture_size));\n"
    "    float scan = mod(floor(gl_FragCoord.y), 2.0);\n"
    "    color.rgb *= mix(1.0, 0.65, scan);\n"
    "    gl_FragColor = color;\n"
    "}\n";

// LCD3x: sharp-bilinear-2x base with RGB subpixel columns and pixel gap rows.
// Simulates the NDS LCD panel's visible subpixel structure.
// Branchless mask selection via step/mix; *2.0+clamp compensates for the ~50%
// average brightness loss the subpixel mask would otherwise cause.
static const char *FRAG_LCD3X =
    "precision mediump float;\n"
    "varying vec2 v_texcoord;\n"
    "uniform sampler2D u_texture;\n"
    "uniform vec2 u_texture_size;\n"
    "uniform vec2 u_output_size;\n"
    "void main() {\n"
    "    vec2 scale = max(vec2(2.0), floor(u_output_size / u_texture_size));\n"
    "    vec2 texel = v_texcoord * u_texture_size;\n"
    "    vec2 texel_floored = floor(texel);\n"
    "    vec2 s = fract(texel);\n"
    "    vec2 region_range = 0.5 - 0.5 / scale;\n"
    "    vec2 center_dist = s - 0.5;\n"
    "    vec2 f = (center_dist - clamp(center_dist, -region_range, region_range)) * scale + 0.5;\n"
    "    vec2 mod_texel = texel_floored + f;\n"
    "    vec4 color = SWIZ(texture2D(u_texture, mod_texel / u_texture_size));\n"
    "    float px = mod(floor(gl_FragCoord.x), 3.0);\n"
    "    vec3 col_r = vec3(1.0, 0.25, 0.25);\n"
    "    vec3 col_g = vec3(0.25, 1.0, 0.25);\n"
    "    vec3 col_b = vec3(0.25, 0.25, 1.0);\n"
    "    vec3 mask = mix(col_r, col_g, step(1.0, px));\n"
    "    mask = mix(mask, col_b, step(2.0, px));\n"
    "    float py = mod(floor(gl_FragCoord.y), 3.0);\n"
    "    mask *= mix(0.5, 1.0, step(1.0, py));\n"
    "    color.rgb = min(color.rgb * mask * 2.0, vec3(1.0));\n"
    "    gl_FragColor = color;\n"
    "}\n";

// Sharp-shimmerless: nearest-neighbor within source texels; boundary-crossing output
// pixels sample a fixed sub-texel position so blend ratios don't drift with sub-pixel
// scroll, eliminating shimmer.
static const char *FRAG_SHARP_SHIMMERLESS =
    "precision mediump float;\n"
    "varying vec2 v_texcoord;\n"
    "uniform sampler2D u_texture;\n"
    "uniform vec2 u_texture_size;\n"
    "uniform vec2 u_output_size;\n"
    "void main() {\n"
    "    vec2 pixel = v_texcoord * u_output_size;\n"
    "    vec2 scale = u_output_size / u_texture_size;\n"
    "    vec2 invscale = u_texture_size / u_output_size;\n"
    "    vec2 pixel_tl = floor(pixel);\n"
    "    vec2 pixel_br = floor(pixel + vec2(1.0));\n"
    "    vec2 texel_tl = floor(invscale * pixel_tl);\n"
    "    vec2 texel_br = floor(invscale * pixel_br);\n"
    "    vec2 mod_texel = texel_br + vec2(0.5);\n"
    "    mod_texel -=\n"
    "        (vec2(1.0) - step(texel_br, texel_tl))\n"
    "        * (scale * texel_br - pixel_tl);\n"
    "    gl_FragColor = SWIZ(texture2D(u_texture, mod_texel / u_texture_size));\n"
    "}\n";

// Inigo Quilez smooth Hermite interpolation (smootherstep)
static const char *FRAG_QUILEZ =
    "precision mediump float;\n"
    "varying vec2 v_texcoord;\n"
    "uniform sampler2D u_texture;\n"
    "uniform vec2 u_texture_size;\n"
    "void main() {\n"
    "    vec2 p = v_texcoord * u_texture_size + vec2(0.5);\n"
    "    vec2 i = floor(p);\n"
    "    vec2 f = p - i;\n"
    "    f = f * f * f * (f * (f * 6.0 - vec2(15.0)) + vec2(10.0));\n"
    "    p = i + f;\n"
    "    p = (p - vec2(0.5)) / u_texture_size;\n"
    "    gl_FragColor = SWIZ(texture2D(u_texture, p));\n"
    "}\n";

// ---------------------------------------------------------------------------
// Shader program helpers
// ---------------------------------------------------------------------------

static GLuint make_gl_shader(GLenum type, const char *preamble, const char *src) {
    if (!p_glCreateShader) return 0;
    GLuint s = p_glCreateShader(type);
    if (!s) return 0;
    const GLchar *srcs[] = { preamble, src };
    p_glShaderSource(s, 2, (const GLchar *const *)srcs, NULL);
    p_glCompileShader(s);
    GLint ok = GL_FALSE;
    p_glGetShaderiv(s, GL_COMPILE_STATUS, &ok);
    if (!ok) { p_glDeleteShader(s); return 0; }
    return s;
}

static GLuint make_gl_program(const char *vert_src, const char *frag_src) {
    // GLSL ES 1.00 (GLES2) shaders need two tweaks to compile under desktop OpenGL:
    //   - Prepend "#version 120" so attribute/varying/texture2D are available
    //   - Drop "precision mediump float;" which is GLES2-only and invalid in desktop GLSL
    static const char FRAG_ES_PREFIX[] = "precision mediump float;\n";
    // SDL's desktop OpenGL renderer stores textures as GL_RGBA → no swizzle needed.
    // SDL's GLES2 renderer (both libmali and Mesa/Panfrost) uses GL_BGRA_EXT when the
    // GL_EXT_texture_format_BGRA8888 extension is available, so .bgra corrects channels.
    const char *vpreamble = gl_renderer_desktop
        ? "#version 120\n#define SWIZ(c) (c)\n"
        : "#define SWIZ(c) (c).bgra\n";
    const char *fpreamble = gl_renderer_desktop
        ? "#version 120\n#define SWIZ(c) (c)\n"
        : "#define SWIZ(c) (c).bgra\n";
    const char *fbody     = frag_src;
    if (gl_renderer_desktop &&
            strncmp(frag_src, FRAG_ES_PREFIX, sizeof(FRAG_ES_PREFIX) - 1) == 0)
        fbody = frag_src + sizeof(FRAG_ES_PREFIX) - 1;

    GLuint vert = make_gl_shader(GL_VERTEX_SHADER, vpreamble, vert_src);
    if (!vert) return 0;
    GLuint frag = make_gl_shader(GL_FRAGMENT_SHADER, fpreamble, fbody);
    if (!frag) { p_glDeleteShader(vert); return 0; }
    GLuint prog = p_glCreateProgram();
    if (!prog) { p_glDeleteShader(vert); p_glDeleteShader(frag); return 0; }
    p_glAttachShader(prog, vert);
    p_glAttachShader(prog, frag);
    // Pin attribute locations before linking so we can use constants
    p_glBindAttribLocation(prog, 0, "a_position");
    p_glBindAttribLocation(prog, 1, "a_texcoord");
    p_glLinkProgram(prog);
    p_glDeleteShader(vert);
    p_glDeleteShader(frag);
    GLint ok = GL_FALSE;
    p_glGetProgramiv(prog, GL_LINK_STATUS, &ok);
    if (!ok) { p_glDeleteProgram(prog); return 0; }
    return prog;
}

// Called from SDL_CreateRenderer once the GLES2 context is live
static void init_shader_program(void) {
    if (shader_mode == SHADER_NONE) return;
    init_gl_funcs();
    fprintf(stderr, "[drastouch] init_shader: mode=%d glCreateShader=%s\n",
            shader_mode, p_glCreateShader ? "ok" : "NULL");
    if (!p_glCreateShader) { shader_mode = SHADER_NONE; return; }
    const char *frag;
    switch (shader_mode) {
        case SHADER_SHARP_SHIMMERLESS: frag = FRAG_SHARP_SHIMMERLESS; break;
        case SHADER_QUILEZ:            frag = FRAG_QUILEZ;            break;
        case SHADER_SCANLINES:         frag = FRAG_SCANLINES;         break;
        case SHADER_LCD3X:             frag = FRAG_LCD3X;             break;
        default:                       frag = FRAG_SHARP_BILINEAR;    break;
    }
    shader_program = make_gl_program(VERT_SRC, frag);
    fprintf(stderr, "[drastouch] shader_program=%u\n", shader_program);
    if (!shader_program) { shader_mode = SHADER_NONE; return; }
    loc_texture      = p_glGetUniformLocation(shader_program, "u_texture");
    loc_texture_size = p_glGetUniformLocation(shader_program, "u_texture_size");
    loc_output_size  = p_glGetUniformLocation(shader_program, "u_output_size");
}

// ---------------------------------------------------------------------------
// Per-frame shader render pass
// ---------------------------------------------------------------------------

// Replace SDL_RenderCopy for a single DS screen texture with a GLES2 shader pass
static int run_shader_copy(SDL_Renderer *r, SDL_Texture *texture,
                           const SDL_Rect *srcrect, const SDL_Rect *dstrect) {
    // Actual source texture dimensions
    int tex_w = 0, tex_h = 0;
    SDL_QueryTexture(texture, NULL, NULL, &tex_w, &tex_h);
    if (tex_w == 0 || tex_h == 0) goto fallback;

    // Flush SDL's batched commands before issuing raw GL
    SDL_RenderFlush(r);

    // Convert dstrect from logical SDL coords to physical GL pixels
    int out_w, out_h;
    SDL_GetRendererOutputSize(r, &out_w, &out_h);
    float sx = (logical_width  > 0) ? (float)out_w / logical_width  : 1.0f;
    float sy = (logical_height > 0) ? (float)out_h / logical_height : 1.0f;
    int gl_w = (int)(dstrect->w * sx);
    int gl_h = (int)(dstrect->h * sy);
    // GL origin is bottom-left; SDL origin is top-left
    int gl_x = (int)(dstrect->x * sx);
    int gl_y = out_h - (int)(dstrect->y * sy) - gl_h;

    if (gl_w < 32 || gl_h < 32) goto fallback;

    // Bind source texture to GL_TEXTURE_2D via SDL
    GLfloat texw = 1.0f, texh = 1.0f;
    if (SDL_GL_BindTexture(texture, &texw, &texh) != 0) {
        static int bind_fail_logged = 0;
        if (!bind_fail_logged) {
            fprintf(stderr, "[drastouch] SDL_GL_BindTexture failed: %s\n", SDL_GetError());
            bind_fail_logged = 1;
        }
        goto fallback;
    }

    // Save GL state we will modify
    GLint saved_viewport[4], saved_program, saved_abuf, saved_blend, saved_scissor;
    p_glGetIntegerv(GL_VIEWPORT,             saved_viewport);
    p_glGetIntegerv(GL_CURRENT_PROGRAM,      &saved_program);
    p_glGetIntegerv(GL_ARRAY_BUFFER_BINDING, &saved_abuf);
    p_glGetIntegerv(GL_BLEND,                &saved_blend);
    p_glGetIntegerv(GL_SCISSOR_TEST,         &saved_scissor);
    // Our draw is always fully opaque; disable blending and clipping
    p_glDisable(GL_BLEND);
    p_glDisable(GL_SCISSOR_TEST);

    p_glViewport(gl_x, gl_y, gl_w, gl_h);
    p_glUseProgram(shader_program);
    if (loc_texture >= 0) p_glUniform1i(loc_texture, 0);
    if (loc_texture_size >= 0)
        p_glUniform2f(loc_texture_size, (float)tex_w, (float)tex_h);
    if (loc_output_size >= 0)
        p_glUniform2f(loc_output_size, (float)gl_w, (float)gl_h);

    // UV sub-rectangle within the source texture
    float u0 = 0.0f, v0 = 0.0f, u1 = texw, v1 = texh;
    if (srcrect) {
        u0 = (float)srcrect->x / tex_w * texw;
        v0 = (float)srcrect->y / tex_h * texh;
        u1 = (float)(srcrect->x + srcrect->w) / tex_w * texw;
        v1 = (float)(srcrect->y + srcrect->h) / tex_h * texh;
    }

    // SDL2/GLES2 stores textures with row-0 at the top in memory; GL has V=0 at bottom.
    // We flip V so the image appears right-way-up after the GL y-flipped viewport.
    // pos(x,y) | uv(u,v)
    GLfloat verts[] = {
        -1.0f, -1.0f,  u0, v1,   // bottom-left  -> texture bottom-left
         1.0f, -1.0f,  u1, v1,   // bottom-right -> texture bottom-right
        -1.0f,  1.0f,  u0, v0,   // top-left     -> texture top-left
         1.0f,  1.0f,  u1, v0,   // top-right    -> texture top-right
    };

    p_glBindBuffer(GL_ARRAY_BUFFER, 0);
    p_glEnableVertexAttribArray(0);
    p_glEnableVertexAttribArray(1);
    p_glVertexAttribPointer(0, 2, GL_FLOAT, GL_FALSE, 4 * sizeof(GLfloat), verts);
    p_glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, 4 * sizeof(GLfloat), verts + 2);
    p_glDrawArrays(GL_TRIANGLE_STRIP, 0, 4);
    // SDL2's GLES2 renderer caches whether attrib arrays 0/1 are enabled and skips
    // re-enabling them when it thinks they're already on.  Leaving them enabled here
    // keeps that cache consistent on libmali (opengles2 renderer).
    // SDL2's desktop OpenGL renderer does NOT cache this state — leaving attribs
    // enabled with stale stack pointers corrupts its subsequent rendering (black menu).
    if (gl_renderer_desktop) {
        p_glDisableVertexAttribArray(0);
        p_glDisableVertexAttribArray(1);
    }

    SDL_GL_UnbindTexture(texture);

    p_glUseProgram(saved_program);
    p_glViewport(saved_viewport[0], saved_viewport[1], saved_viewport[2], saved_viewport[3]);
    p_glBindBuffer(GL_ARRAY_BUFFER, saved_abuf);
    if (saved_blend)   p_glEnable(GL_BLEND);   else p_glDisable(GL_BLEND);
    if (saved_scissor) p_glEnable(GL_SCISSOR_TEST); else p_glDisable(GL_SCISSOR_TEST);
    return 0;

fallback:
    return real_SDL_RenderCopy(r, texture, srcrect, dstrect);
}

// ---------------------------------------------------------------------------
// SDL2 hooks
// ---------------------------------------------------------------------------

SDL_Window* SDL_CreateWindow(const char *title, int x, int y, int w, int h, Uint32 flags) {
    num_displays = SDL_GetNumVideoDisplays();
    int total_width = 0;
    int total_height = 0;
    int last_width = 0;
    int last_height = 0;

    // Change window to total screen size
    // Prevents empty spacing on dual displays
    for (int i = 0; i < num_displays; ++i) {
        SDL_Rect bounds;
        if (SDL_GetDisplayBounds(i, &bounds) == 0) {
            last_width = bounds.w;
            last_height = bounds.h;
            if (bounds.w + bounds.x > total_width)
                total_width += bounds.w;
            if (bounds.h + bounds.y > total_height)
                total_height += bounds.h;

            if (i == 0) {
                display0_rect = bounds;
            } else if (i == 1) {
                display1_rect = bounds;
                has_display_rects = 1;
            }
        }
    }

    // Record screen size for rect tracking/conversion
    phys_width = total_width;
    phys_height = total_height;

    // DraStic starts in the center of the native virtual screen
    last_x = 128;
    last_y = 96;

    // Correctly detect physical display orientation (stacked vs side-by-side)
    if (num_displays > 1) {
        if (phys_height > last_height) {
            xy_idx = 2; // Vertical stacked layout (e.g. RG-DS, AYN Thor)
        } else if (phys_width > last_width) {
            xy_idx = 1; // Horizontal side-by-side layout
        } else {
            xy_idx = 0;
        }
    }

    // Force SDL to create a borderless window (no titlebar/decorations)
    flags |= 0x00000010; // SDL_WINDOW_BORDERLESS

    // Set window size to full combined virtual size dynamically from startup
    return real_SDL_CreateWindow(title, 0, 0, phys_width, phys_height, flags);
}

void SDL_SetWindowSize(SDL_Window* window, int w, int h) {
    static int init_resize = 2;

    if (init_resize > 0) {
        real_SDL_SetWindowSize(window, w, h);
        init_resize -= 1;
    }

    // Force window size to fill AFTER DraStic does its weird init thing
    if (init_resize == 0) {
        real_SDL_SetWindowSize(window, phys_width, phys_height);
        init_resize = -1;
    } else if (init_resize == -1) {
        real_SDL_SetWindowSize(window, phys_width, phys_height); // Lock at full desktop height
    }

}

SDL_Renderer* SDL_CreateRenderer(SDL_Window* window, int index, Uint32 flags) {
    renderer = real_SDL_CreateRenderer(window, index, flags);
    if (renderer) {
        // Just in case it's already set
        SDL_RenderGetLogicalSize(renderer, &logical_width, &logical_height);
        SDL_RendererInfo info;
        if (SDL_GetRendererInfo(renderer, &info) == 0) {
            fprintf(stderr, "[drastouch] SDL renderer: %s (flags=0x%x)\n", info.name, info.flags);
            gl_renderer_desktop = (strcmp(info.name, "opengl") == 0);
        }
        init_shader_program();  // GLES2 context is live at this point
    }
    return renderer;
}

int SDL_RenderSetLogicalSize(SDL_Renderer* renderer, int w, int h) {
    int result = real_SDL_RenderSetLogicalSize(renderer, w, h);
    // Also store it here so run_shader_copy can convert logical→physical coords
    logical_width = w;
    logical_height = h;
    return result;
}

void SDL_RenderPresent(SDL_Renderer *r) {
    shader_frame_calls = 0;
    real_SDL_RenderPresent(r);
}

SDL_Texture* SDL_CreateTexture(SDL_Renderer *renderer, Uint32 format, int type, int w, int h) {
    SDL_Texture* texture = real_SDL_CreateTexture(renderer, format, type, w, h);
    // Identify DS screen and stylus textures
    if (type == SDL_TEXTUREACCESS_STREAMING) {
        if (w == 512 && h == 384) {
            ds_screen_width = 512;
            ds_screen_height = 384;
            if (!screens[0]) screens[0] = texture;
            else if (!screens[1]) screens[1] = texture;
        } else if (w == 256 && h == 192 && !screens[0]) {
            if (!screens[2]) screens[2] = texture;
            else if (!screens[3]) screens[3] = texture;
        }
    }
    if (w == 32 && h == 32) {
        if (!stylus_tex[0]) stylus_tex[0] = texture;
        else if (!stylus_tex[1]) stylus_tex[1] = texture;
    }
    return texture;
}

int SDL_RenderCopy(SDL_Renderer *renderer, SDL_Texture *texture, const SDL_Rect *srcrect, const SDL_Rect *dstrect) {
    SDL_Rect override_dst_storage;
    const SDL_Rect *final_dst = dstrect;

    int is_ds_screen = 0;
    for (int i = 0; i < 4; i++) {
        if (screens[i] && texture == screens[i]) {
            is_ds_screen = 1;
            break;
        }
    }

    // Only override the bottom screen layout to map to the secondary display
    if (is_ds_screen && has_display_rects && num_displays > 1 && logical_width > 0 && logical_height > 0 && dstrect) {
        int is_bottom_screen = 0;

        if (xy_idx == 2) { // Vertically stacked layout
            if (dstrect->y + dstrect->h / 2 >= logical_height / 2) {
                is_bottom_screen = 1;
            }
        } else if (xy_idx == 1) { // Horizontally side-by-side layout
            if (dstrect->x + dstrect->w / 2 >= logical_width / 2) {
                is_bottom_screen = 1;
            }
        }

        if (is_bottom_screen) {
            SDL_Rect target_bounds = display1_rect;

            int out_w = 0, out_h = 0;
            SDL_GetRendererOutputSize(renderer, &out_w, &out_h);

            float scale_x = (float)out_w / logical_width;
            float scale_y = (float)out_h / logical_height;
            float scale = (scale_x < scale_y) ? scale_x : scale_y;

            if (scale > 0.0f) {
                float vp_x = (out_w - logical_width * scale) / 2.0f;
                float vp_y = (out_h - logical_height * scale) / 2.0f;

                // Reverse-scale physical bounds back to SDL's logical space mapping
                override_dst_storage.x = (int)roundf(((float)target_bounds.x - vp_x) / scale);
                override_dst_storage.y = (int)roundf(((float)target_bounds.y - vp_y) / scale);
                override_dst_storage.w = (int)roundf((float)target_bounds.w / scale);
                override_dst_storage.h = (int)roundf((float)target_bounds.h / scale);

                final_dst = &override_dst_storage;
            }
        }
    }

    if ((screens[0] && texture == screens[0] && ds_screen_width == 512) ||
        (screens[3] && texture == screens[3] && ds_screen_width == 256)) {
        
        if (has_display_rects && num_displays > 1) {
            // Directly align the physical touchscreen area with the bounds of Display 1
            touch_rect_storage = display1_rect;
        } else {
            // Fallback to original conversion calculation if layout boundaries are uninitialized
            if (logical_width > 0 && logical_height > 0) {
                int output_w, output_h;
                SDL_GetRendererOutputSize(renderer, &output_w, &output_h);
                float scale_x = (float)output_w / logical_width;
                float scale_y = (float)output_h / logical_height;

                touch_rect_storage.x = (int)(final_dst->x * scale_x);
                touch_rect_storage.y = (int)(final_dst->y * scale_y);
                touch_rect_storage.w = (int)(final_dst->w * scale_x);
                touch_rect_storage.h = (int)(final_dst->h * scale_y);
            } else {
                // Fallback and hope they're right
                touch_rect_storage.x = final_dst->x;
                touch_rect_storage.y = final_dst->y;
                touch_rect_storage.w = final_dst->w;
                touch_rect_storage.h = final_dst->h;
            }
        }
        touch_rect = &touch_rect_storage;
    }

    // Make stylus fully transparent for actual touchscreens
    if (actual_touch && (texture == stylus_tex[0] || texture == stylus_tex[1]))
        SDL_SetTextureAlphaMod(texture, 0);

    // Apply pixel shader to DS screen textures when one is configured.
    // Cap at 2 shader passes per frame so menu overlays (drawn after the two NDS
    // screens) fall through to normal SDL rendering without breaking blending.
    // Skip when rendering into a texture target — viewport math uses screen size.
    if (shader_program && final_dst && shader_frame_calls < 2 &&
        SDL_GetRenderTarget(renderer) == NULL) {
        for (int i = 0; i < 4; i++) {
            if (screens[i] && texture == screens[i]) {
                shader_frame_calls++;
                return run_shader_copy(renderer, texture, srcrect, final_dst);
            }
        }
    }

    return real_SDL_RenderCopy(renderer, texture, srcrect, final_dst);
}

void mic_audio_callback(void* userdata, Uint8* stream, int len) {
    if (!mic_enabled) return;

    Sint16* samples = (Sint16*)stream;
    int sample_count = len / 2;

    // Calculate RMS amplitude
    float sum = 0.0f;
    for (int i = 0; i < sample_count; i++) {
        float sample = samples[i] / 32768.0f; // Normalize to [-1.0..1.0]
        sum += sample * sample;
    }
    float rms = sqrtf(sum / sample_count);

    // Build ambient baseline over first ~3 seconds
    if (mic_baseline_samples < 60) {
        mic_baseline = (mic_baseline * mic_baseline_samples + rms) / (mic_baseline_samples + 1);
        mic_baseline_samples++;
        return; // Don't trigger during calibration
    }

    mic_baseline = mic_baseline * 0.999f + rms * 0.001f;

    // Trigger only if significantly above baseline
    float trigger_level = mic_baseline + mic_threshold;
    int should_hold = (rms > trigger_level);
    if (should_hold && !mic_key_held) {
        // Noise detected, press Scroll Lock
        SDL_Event key_event = {0};
        key_event.type = SDL_KEYDOWN;
        key_event.key.state = SDL_PRESSED;
        key_event.key.keysym.scancode = SDL_SCANCODE_SCROLLLOCK;
        key_event.key.keysym.sym = SDLK_SCROLLLOCK;
        real_SDL_PushEvent(&key_event);
        mic_key_held = 1;
    } else if (!should_hold && mic_key_held) {
        // Noise dropped below threshold, release Scroll Lock
        SDL_Event key_event = {0};
        key_event.type = SDL_KEYUP;
        key_event.key.state = SDL_RELEASED;
        key_event.key.keysym.scancode = SDL_SCANCODE_SCROLLLOCK;
        key_event.key.keysym.sym = SDLK_SCROLLLOCK;
        real_SDL_PushEvent(&key_event);
        mic_key_held = 0;
    }
}

int SDL_PollEvent(SDL_Event* event) {
    // Loop required to filter events we don't want to pass along
    while (1) {
        int result = real_SDL_PollEvent(event);
        if (!result) return 0;

        switch (event->type) {
            case SDL_FINGERDOWN: {
                if (!actual_touch)
                    actual_touch = 1;

                int x = (int)(event->tfinger.x * phys_width);
                int y = (int)(event->tfinger.y * phys_height);

                if (!touch_rect) return 0;

                if (x < touch_rect->x || x > touch_rect->x + touch_rect->w ||
                    y < touch_rect->y || y > touch_rect->y + touch_rect->h) {
                    return 0; // Outside valid coords, don't convert
                }

                // Scale to native virtual touchscreen
                x = ((x - touch_rect->x) * 256) / touch_rect->w;
                y = ((y - touch_rect->y) * 192) / touch_rect->h;

                // Queue click for after jump
                event->type = SDL_MOUSEBUTTONDOWN;
                event->button.button = SDL_BUTTON_LEFT;
                event->button.state = SDL_PRESSED;
                event->button.x = x;
                event->button.y = y;
                real_SDL_PushEvent(event);

                // Jump to new position
                event->type = SDL_MOUSEMOTION;
                event->motion.x = x;
                event->motion.y = y;
                event->motion.xrel = x - last_x;
                event->motion.yrel = y - last_y;

                // Update to keep position accurate
                last_x = x;
                last_y = y;
                break;
            }
            case SDL_FINGERMOTION: {
                int x = (int)(event->tfinger.x * phys_width);
                int y = (int)(event->tfinger.y * phys_height);

                if (!touch_rect) return 0;

                if (x < touch_rect->x || x > touch_rect->x + touch_rect->w ||
                    y < touch_rect->y || y > touch_rect->y + touch_rect->h)
                    return 0;

                x = ((x - touch_rect->x) * 256) / touch_rect->w;
                y = ((y - touch_rect->y) * 192) / touch_rect->h;
                int xrel = x - last_x;
                int yrel = y - last_y;

                // Motion is also used when already clicked but not moving
                // Always update it
                event->type = SDL_MOUSEMOTION;
                event->motion.x = x;
                event->motion.y = y;
                event->motion.xrel = xrel;
                event->motion.yrel = yrel;

                last_x = x;
                last_y = y;
                break;
            }
            case SDL_FINGERUP: {
                event->type = SDL_MOUSEBUTTONUP;
                event->button.button = SDL_BUTTON_LEFT;
                event->button.state = SDL_RELEASED;
                event->button.x = last_x;
                event->button.y = last_y;
                break;
            }
        }
        return result;
    }
}

__attribute__((constructor))
static void init(void) {
    // Try to open the system's shared SDL2 library directly
    void* sdl_handle = dlopen("libSDL2-2.0.so.0", RTLD_LAZY | RTLD_GLOBAL);
    if (!sdl_handle) {
        sdl_handle = dlopen("libSDL2.so", RTLD_LAZY | RTLD_GLOBAL);
    }
    if (!sdl_handle) {
        // Fallback to standard dynamic linker chain
        sdl_handle = RTLD_NEXT;
    }

    // Resolve standard window and input functions
    real_SDL_CreateWindow = dlsym(sdl_handle, "SDL_CreateWindow");
    real_SDL_SetWindowSize = dlsym(sdl_handle, "SDL_SetWindowSize");
    real_SDL_CreateRenderer = dlsym(sdl_handle, "SDL_CreateRenderer");
    real_SDL_RenderSetLogicalSize = dlsym(sdl_handle, "SDL_RenderSetLogicalSize");
    real_SDL_CreateTexture = dlsym(sdl_handle, "SDL_CreateTexture");
    real_SDL_RenderCopy = dlsym(sdl_handle, "SDL_RenderCopy");
    real_SDL_PollEvent = dlsym(sdl_handle, "SDL_PollEvent");
    real_SDL_PushEvent = dlsym(sdl_handle, "SDL_PushEvent");
    real_SDL_RenderPresent = dlsym(sdl_handle, "SDL_RenderPresent");

    // Resolve audio subsystem functions
    real_SDL_WasInit = dlsym(sdl_handle, "SDL_WasInit");
    real_SDL_InitSubSystem = dlsym(sdl_handle, "SDL_InitSubSystem");
    real_SDL_OpenAudioDevice = dlsym(sdl_handle, "SDL_OpenAudioDevice");
    real_SDL_PauseAudioDevice = dlsym(sdl_handle, "SDL_PauseAudioDevice");
    real_SDL_CloseAudioDevice = dlsym(sdl_handle, "SDL_CloseAudioDevice");
    real_SDL_GetNumAudioDevices = dlsym(sdl_handle, "SDL_GetNumAudioDevices");
    real_SDL_GetAudioDeviceName = dlsym(sdl_handle, "SDL_GetAudioDeviceName");

    // Resolve environment variables for the shader
    const char *shader_str = getenv("DSHOOK_SHADER");
    if (shader_str) {
        if (strcmp(shader_str, "sharp-bilinear") == 0)
            shader_mode = SHADER_SHARP_BILINEAR;
        else if (strcmp(shader_str, "quilez") == 0)
            shader_mode = SHADER_QUILEZ;
        else if (strcmp(shader_str, "scanlines") == 0)
            shader_mode = SHADER_SCANLINES;
        else if (strcmp(shader_str, "lcd3x") == 0)
            shader_mode = SHADER_LCD3X;
        else if (strcmp(shader_str, "sharp-shimmerless") == 0)
            shader_mode = SHADER_SHARP_SHIMMERLESS;
    }

    // Resolve microphone logic safely
    const char* threshold_str = getenv("DSHOOK_MIC_THRESH");
    if (threshold_str) {
        mic_threshold = atof(threshold_str);
        if (mic_threshold > 0.0f) {
            
            // Safety Check: Verify all required SDL audio function pointers were actually resolved
            if (!real_SDL_WasInit || !real_SDL_InitSubSystem || !real_SDL_OpenAudioDevice ||
                !real_SDL_PauseAudioDevice || !real_SDL_CloseAudioDevice ||
                !real_SDL_GetNumAudioDevices || !real_SDL_GetAudioDeviceName || !real_SDL_PushEvent) {
                fprintf(stderr, "[drastouch] WARNING: System SDL audio function pointers could not be resolved. Microphone disabled.\n");
                mic_enabled = 0;
            } else {
                mic_enabled = 1;

                // Try to initialize the audio subsystem safely
                if (real_SDL_WasInit(SDL_INIT_AUDIO) == 0) {
                    if (real_SDL_InitSubSystem(SDL_INIT_AUDIO) < 0) {
                        fprintf(stderr, "[drastouch] WARNING: Failed to initialize SDL audio subsystem. Microphone disabled.\n");
                        mic_enabled = 0;
                    }
                }

                if (mic_enabled) {
                    int num_devices = real_SDL_GetNumAudioDevices(1);
                    const char* device_name = NULL;
                    for (int i = 0; i < num_devices; i++) {
                        const char* name = real_SDL_GetAudioDeviceName(i, 1);
                        if (name && (i == 0 || strstr(name, "Built-in"))) {
                            device_name = name;
                            break;
                        }
                    }

                    SDL_AudioSpec desired_spec = {0};
                    desired_spec.freq = 44100;
                    desired_spec.format = AUDIO_S16SYS;
                    desired_spec.channels = 1;
                    desired_spec.samples = 2048;
                    desired_spec.callback = mic_audio_callback;

                    SDL_AudioSpec obtained_spec;
                    mic_device = real_SDL_OpenAudioDevice(device_name, 1, &desired_spec, &obtained_spec, 0);

                    if (mic_device > 0) {
                        fprintf(stderr, "[drastouch] Microphone successfully started using device: %s\n", device_name ? device_name : "Default");
                        real_SDL_PauseAudioDevice(mic_device, 0);
                    } else {
                        fprintf(stderr, "[drastouch] WARNING: Failed to open capture device. Microphone disabled.\n");
                        mic_enabled = 0;
                    }
                }
            }
        }
    }
}

__attribute__((destructor))
static void cleanup(void) {
    if (mic_device > 0 && real_SDL_CloseAudioDevice) {
        real_SDL_CloseAudioDevice(mic_device);
    }
    if (shader_program && p_glDeleteProgram) {
        p_glDeleteProgram(shader_program);
        shader_program = 0;
    }
}

// Major thanks/credit to Shaun Inman for providing the basis of this hook library!
// Extra thanks to the Rocknix team (LyohaProto) for making this initial library.
// Updated to better handle Batocera nuances, sound handling, borderless window & varying screen sizes (Ayn Thor) - by @dmanlfc
