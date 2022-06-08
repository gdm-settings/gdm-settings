# Text Styling
bold       = '\033[1m'
dim        = '\033[2m'
italic     = '\033[3m'
underline  = '\033[4m'
blink      = '\033[5m'
blink_fast = '\033[6m'
invert     = '\033[7m'
hide       = '\033[8m'
strike     = '\033[9m'
overline   = '\033[53m'

underline_double = '\033[21m'

reset            = '\033[0m'
reset_bold_dim   = '\033[22m'
reset_italic     = '\033[23m'
reset_underline  = '\033[24m'
reset_blink      = '\033[25m'
reset_invert     = '\033[27m'
reset_hide       = '\033[28m'
reset_strike     = '\033[29m'
reset_overline   = '\033[55m'
reset_foreground = '\033[39m'
reset_background = '\033[49m'

reset_dim_bold   = reset_bold_dim


# Foreground Colors

black_foreground         = '\033[30m'

red_dark_foreground      = '\033[31m'
green_dark_foreground    = '\033[32m'
yellow_dark_foreground   = '\033[33m'
blue_dark_foreground     = '\033[34m'
magenta_dark_foreground  = '\033[35m'
cyan_dark_foreground     = '\033[36m'

grey_light_foreground    = '\033[37m'
grey_dark_foreground     = '\033[90m'

red_light_foreground     = '\033[91m'
green_light_foreground   = '\033[92m'
yellow_light_foreground  = '\033[93m'
blue_light_foreground    = '\033[94m'
magenta_light_foreground = '\033[95m'
cyan_light_foreground    = '\033[96m'

white_foreground         = '\033[97m'


# Background Colors

black_background         = '\033[40m'

red_dark_background      = '\033[41m'
green_dark_background    = '\033[42m'
yellow_dark_background   = '\033[43m'
blue_dark_background     = '\033[44m'
magenta_dark_background  = '\033[45m'
cyan_dark_background     = '\033[46m'

grey_light_background    = '\033[47m'
grey_dark_background     = '\033[100m'

red_light_background     = '\033[101m'
green_light_background   = '\033[102m'
yellow_light_background  = '\033[103m'
blue_light_background    = '\033[104m'
magenta_light_background = '\033[105m'
cyan_light_background    = '\033[106m'

white_background         = '\033[107m'


### Aliases ###

# Shortened dark/light foreground/background names

black_fg     = black_foreground

red_d_fg     = red_dark_foreground
green_d_fg   = green_dark_foreground
yellow_d_fg  = yellow_dark_foreground
blue_d_fg    = blue_dark_foreground
magenta_d_fg = magenta_dark_foreground
cyan_d_fg    = cyan_dark_foreground

grey_d_fg    = grey_dark_foreground
grey_l_fg    = grey_light_foreground

red_l_fg     = red_light_foreground
green_l_fg   = green_light_foreground
yellow_l_fg  = yellow_light_foreground
blue_l_fg    = blue_light_foreground
magenta_l_fg = magenta_light_foreground
cyan_l_fg    = cyan_light_foreground

white_fg     = white_foreground


black_bg     = black_background

red_d_bg     = red_dark_background
green_d_bg   = green_dark_background
yellow_d_bg  = yellow_dark_background
blue_d_bg    = blue_dark_background
magenta_d_bg = magenta_dark_background
cyan_d_bg    = cyan_dark_background

grey_d_bg    = grey_dark_background
grey_l_bg    = grey_light_background

red_l_bg     = red_light_background
green_l_bg   = green_light_background
yellow_l_bg  = yellow_light_background
blue_l_bg    = blue_light_background
magenta_l_bg = magenta_light_background
cyan_l_bg    = cyan_light_background

white_bg     = white_background

# Foreground colors assumed

red_dark     = red_dark_foreground
green_dark   = green_dark_foreground
yellow_dark  = yellow_dark_foreground
blue_dark    = blue_dark_foreground
magenta_dark = magenta_dark_foreground
cyan_dark    = cyan_dark_foreground

grey_dark    = grey_dark_foreground
grey_light    = grey_light_foreground

red_light     = red_light_foreground
green_light   = green_light_foreground
yellow_light  = yellow_light_foreground
blue_light    = blue_light_foreground
magenta_light = magenta_light_foreground
cyan_light    = cyan_light_foreground

# Foreground colors assumed + short dark/light names

red_d     = red_dark_foreground
green_d   = green_dark_foreground
yellow_d  = yellow_dark_foreground
blue_d    = blue_dark_foreground
magenta_d = magenta_dark_foreground
cyan_d    = cyan_dark_foreground

grey_d    = grey_dark_foreground
grey_l    = grey_light_foreground

red_l     = red_light_foreground
green_l   = green_light_foreground
yellow_l  = yellow_light_foreground
blue_l    = blue_light_foreground
magenta_l = magenta_light_foreground
cyan_l    = cyan_light_foreground

# Dark colors assumed (except grey)

black_foreground   = black_foreground
red_foreground     = red_dark_foreground
green_foreground   = green_dark_foreground
yellow_foreground  = yellow_dark_foreground
blue_foreground    = blue_dark_foreground
magenta_foreground = magenta_dark_foreground
cyan_foreground    = cyan_dark_foreground
grey_foreground    = grey_light_foreground
white_foreground   = white_foreground

black_background   = black_background
red_background     = red_dark_background
green_background   = green_dark_background
yellow_background  = yellow_dark_background
blue_background    = blue_dark_background
magenta_background = magenta_dark_background
cyan_background    = cyan_dark_background
grey_background    = grey_light_background
white_background   = white_background

# Dark colors assumed (except grey) + shortened foreground/background

black_fg   = black_foreground
red_fg     = red_dark_foreground
green_fg   = green_dark_foreground
yellow_fg  = yellow_dark_foreground
blue_fg    = blue_dark_foreground
magenta_fg = magenta_dark_foreground
cyan_fg    = cyan_dark_foreground
grey_fg    = grey_light_foreground
white_fg   = white_foreground

black_bg   = black_background
red_bg     = red_dark_background
green_bg   = green_dark_background
yellow_bg  = yellow_dark_background
blue_bg    = blue_dark_background
magenta_bg = magenta_dark_background
cyan_bg    = cyan_dark_background
grey_bg    = grey_light_background
white_bg   = white_background

# Dark foreground colors assumed (except grey, it is assumed light foreground)

black   = black_foreground
red     = red_dark_foreground
green   = green_dark_foreground
yellow  = yellow_dark_foreground
blue    = blue_dark_foreground
magenta = magenta_dark_foreground
cyan    = cyan_dark_foreground
grey    = grey_light_foreground
white   = white_foreground
