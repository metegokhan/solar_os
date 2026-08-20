#include <assert.h>
#include <stdio.h>
#include <string.h>

#include "solar_os_keys.h"
#include "solar_os_tui_widgets.h"

static void test_viewport(void)
{
    solar_os_tui_viewport_t viewport = {.cursor = 0, .top = 0};
    assert(solar_os_tui_viewport_key(&viewport, SOLAR_OS_KEY_DOWN, 10, 3, false));
    assert(viewport.cursor == 1 && viewport.top == 0);
    assert(solar_os_tui_viewport_key(&viewport, SOLAR_OS_KEY_PAGE_DOWN, 10, 3, false));
    assert(viewport.cursor == 4 && viewport.top == 2);
    assert(solar_os_tui_viewport_key(&viewport, SOLAR_OS_KEY_END, 10, 3, false));
    assert(viewport.cursor == 9 && viewport.top == 7);
    assert(!solar_os_tui_viewport_key(&viewport, SOLAR_OS_KEY_DOWN, 10, 3, false));
    assert(solar_os_tui_viewport_key(&viewport, SOLAR_OS_KEY_DOWN, 10, 3, true));
    assert(viewport.cursor == 0 && viewport.top == 0);
}

static void test_layout(void)
{
    solar_os_tui_screen_layout_t layout;
    assert(solar_os_tui_layout_compute(20, 40, 1, 1, 1, &layout));
    assert(layout.title.row == 0 && layout.title.width == 40);
    assert(layout.tabs.row == 1 && layout.tabs.height == 1);
    assert(layout.body.row == 2 && layout.body.height == 15);
    assert(layout.status.row == 17 && layout.input.row == 18 && layout.help.row == 19);
    assert(!solar_os_tui_layout_compute(5, 40, 1, 1, 1, &layout));
}

static void test_input(void)
{
    char text[32] = "a\xc3\xa4" "b";
    solar_os_tui_input_state_t state = {.cursor = strlen(text), .view = 0};
    assert(solar_os_tui_input_key(text, sizeof(text), &state,
                                  SOLAR_OS_KEY_LEFT, 2) == SOLAR_OS_TUI_INPUT_NONE);
    assert(state.cursor == 3);
    assert(solar_os_tui_input_key(text, sizeof(text), &state, '\b', 2) ==
           SOLAR_OS_TUI_INPUT_CHANGED);
    assert(strcmp(text, "ab") == 0 && state.cursor == 1);
    assert(solar_os_tui_input_key(text, sizeof(text), &state, 'X', 2) ==
           SOLAR_OS_TUI_INPUT_CHANGED);
    assert(strcmp(text, "aXb") == 0 && state.cursor == 2);
    strcpy(text, "one two");
    state.cursor = strlen(text);
    state.view = 0;
    assert(solar_os_tui_input_key(text, sizeof(text), &state,
                                  SOLAR_OS_KEY_CTRL_LEFT, 8) == SOLAR_OS_TUI_INPUT_NONE);
    assert(state.cursor == 4);
    assert(solar_os_tui_input_key(text, sizeof(text), &state,
                                  SOLAR_OS_KEY_CTRL_RIGHT, 8) == SOLAR_OS_TUI_INPUT_NONE);
    assert(state.cursor == strlen(text));
    text[0] = (char)0xc3;
    text[1] = '\0';
    state.cursor = 0;
    assert(solar_os_tui_input_key(text, sizeof(text), &state,
                                  SOLAR_OS_KEY_DELETE, 2) ==
           SOLAR_OS_TUI_INPUT_CHANGED);
    assert(text[0] == '\0');
    assert(solar_os_tui_input_key(text, sizeof(text), &state,
                                  SOLAR_OS_KEY_ENTER, 2) == SOLAR_OS_TUI_INPUT_SUBMIT);
}

int main(void)
{
    test_viewport();
    test_layout();
    test_input();
    puts("tui_widgets_test: ok");
    return 0;
}
