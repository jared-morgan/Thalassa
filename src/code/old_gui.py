from pathlib import Path
import pygame
import math

class Button:
    def __init__(self, x, y, width, height, text, font, button_colour=(255, 255, 255), text_colour=(31, 31, 31), border_radius=10, border_width=0):
        self.rect = pygame.Rect(x, y, width, height)
        self.colour = button_colour
        self.text = text
        self.font = font
        self.text_colour = text_colour
        self.border_radius = border_radius
        self.border_width = border_width

        self.text_surface = self.font.render(self.text, True, self.text_colour)
        self.text_rect = self.text_surface.get_rect(centerx=self.rect.centerx)

        # The font is slightly too high otherwise
        font_height = self.font.get_height() -4
        self.text_rect.y = self.rect.y + (self.rect.height - font_height) // 2 

    def draw(self, surface):
        pygame.draw.rect(surface, self.colour, self.rect, border_radius=self.border_radius, width=self.border_width)
        surface.blit(self.text_surface, self.text_rect)

    def is_clicked(self, mouse_pos):
        return self.rect.collidepoint(mouse_pos)
    
class Tab:
    def __init__(self, x, y, width, height, text, font, tab_colour=(255, 255, 255), text_colour=(31, 31, 31), border_radius=10, border_width=0):
        self.rect = pygame.Rect(x, y, width, height)
        self.colour = tab_colour
        self.text = text
        self.font = font
        self.text_colour = text_colour
        self.border_radius = border_radius
        self.border_width = border_width

        self.text_surface = self.font.render(self.text, True, self.text_colour)
        self.text_rect = self.text_surface.get_rect(centerx=self.rect.centerx)

        # The font is slightly too high otherwise
        font_height = self.font.get_height() -4
        self.text_rect.y = self.rect.y + (self.rect.height - font_height) // 2

class GUI:
    def __init__(self, src_path: Path, rumble_scaling):
        

        self.colours = {"black": (31, 31, 31),
                        "white": (255, 255, 255),
                        "blue": (50, 50, 180),
                        "grey": (160, 160, 160),
                        "yellow": (255, 255, 84),
                        "gold": (235, 161, 52),
                        "red": (255, 0, 0),
                        "green": (0, 128, 0),
                        "purple": (128, 0, 128),
                        "orange": (255, 165, 0),
                        "very_black": (0, 0, 0),
                        }


        Roboto_regular = src_path / Path("media", "cmuntt.ttf")
        self.my_font_84 = pygame.font.Font(Roboto_regular, 84)
        self.my_font_48 = pygame.font.Font(Roboto_regular, 48)
        self.my_font_32 = pygame.font.Font(Roboto_regular, 32)
        self.my_font_22 = pygame.font.Font(Roboto_regular, 22)
        
        self.rumble_scaling = rumble_scaling
        self.my_font_rumble = pygame.font.Font(Roboto_regular, int(math.floor(self.rumble_scaling * 1.2)))
        self.my_font_rumble_small = pygame.font.Font(Roboto_regular, int(math.floor(self.rumble_scaling * 0.8)))
        self.rumble_width = 10
        self.rumble_height = 21

        mode_list = ["CI", "VL", "WW", "EV"]
        self.modes = {}
        for mode in mode_list:
            self.modes[mode] = self.my_font_32.render(mode, True, self.colours["grey"])

        self.looting_timer = self.my_font_84.render("0", True, self.colours["white"])
        
        self.plank_swabbie_text = self.my_font_32.render("Plank Swabbie!", True, self.colours["white"])

        self.copy_button = Button(5, 135, 65, 30, "Copy", self.my_font_22, button_colour=self.colours["white"], text_colour=self.colours["white"], border_width=1)
        self.reset_button = Button(75, 135, 75, 30, "Reset", self.my_font_22, button_colour=self.colours["white"], text_colour=self.colours["white"], border_width=1)
        
        
    def create_homun_colour_bars(self, main):
        homun_start_y = 170
        homun_start_x = 5
        homun_bar_width = 95
        homun_bar_height = 20
        
        offset = 0
        self.homun_colour_bars = {}
        for colour in main.fray.homun_count:
            rect = pygame.Rect(homun_start_x, homun_start_y + offset * homun_bar_height, homun_bar_width, homun_bar_height)
            self.homun_colour_bars[colour] = rect
            offset += 1
        
        homun_start_y += 0 # if I want to offset it later
        homun_start_x += 30 + homun_bar_width

        offset = 0
        self.homun_true_bars = {}
        for colour in main.fray.homun_true_count:
            rect = pygame.Rect(homun_start_x, homun_start_y + offset * homun_bar_height, homun_bar_width, homun_bar_height)
            self.homun_true_bars[colour] = rect
            offset += 1


    def update_mode_text(self, new_mode):
        for mode in self.modes.keys():
            colour = self.colours["white"] if mode == new_mode else self.colours["grey"]
            self.modes[mode] = self.my_font_32.render(mode, True, colour)

    
    def reset_gui(self, main):
        main.pygame_display.fill(self.colours["black"])


    def update_gui(self, main):
        mode_x_offset = 40
        mode_x = 0
        for mode in self.modes.values():
            main.pygame_display.blit(mode, (mode_x, 0))
            mode_x += mode_x_offset
        if main.looting_active:
            main.pygame_display.blit(self.looting_timer, (0, 50))
        if main.plank_swabbie:
            main.pygame_display.blit(self.plank_swabbie_text, (0, 30))
        if main.rumble_active or main.sf_active:
            main.pygame_display.blit(self.fray_time, (0, 50))
        if main.rumble_active:
            if main.configs.mini_rumble:
                main.pygame_display.blit(self.mini_rumble_groups, (0, 110))
            else:
                pass
        if main.sf_active and main.configs.mode == "CI":
            for colour, rect in self.homun_colour_bars.items():
                pygame.draw.rect(main.pygame_display, self.colours[colour], rect)
                text = self.my_font_22.render(str(main.fray.homun_count[colour]), True, self.colours["white"])
                main.pygame_display.blit(text, (rect.x + 100, rect.y-2))

            for colour, rect in self.homun_true_bars.items():
                pygame.draw.rect(main.pygame_display, self.colours[colour], rect)
                text = self.my_font_22.render(str(main.fray.homun_true_count[colour]), True, self.colours["white"])
                main.pygame_display.blit(text, (rect.x + 100, rect.y-2))

            self.copy_button.draw(main.pygame_display)  
            self.reset_button.draw(main.pygame_display)          


    
    def update_time_passed_text(self, main, time_passed):
        if main.configs.timer_decimals == 0: # if timer decimals is 0, round to nearest second
            time_passed = str(round(time_passed / 1000))
        else:
            time_passed = str(round(time_passed / 1000, main.configs.timer_decimals))
        self.looting_timer = self.my_font_84.render(time_passed, True, self.colours["white"])


    def update_plank_swabbie_text(self, colour):
        self.plank_swabbie_text = self.my_font_32.render("Plank Swabbie!", True, self.colours[colour]) # I don't think I want it to flash anymore


    def update_fray_time(self, fray_minutes, fray_seconds, fray_type):
        if fray_type == "rumble" and fray_seconds > 49:
            colour = "red"
        else:
            colour = "white"
        self.fray_time = self.my_font_84.render(f"{fray_minutes:02}:{fray_seconds:02}", True, self.colours[colour])

    
    def update_mini_rumble_groups(self, groups: str):
        self.mini_rumble_groups = self.my_font_84.render(groups, True, self.colours["white"])

    
    def draw_rumble_table(self, main, rumble_mins, rumble_dictionary):
        
        rumble_table_start = [self.rumble_scaling*2+2, 150]

        pygame.draw.rect(main.pygame_display, self.colours["white"], (rumble_table_start[0], rumble_table_start[1], (self.rumble_width*self.rumble_scaling)+4, (self.rumble_height*self.rumble_scaling)+4), 1)  # (x, y, width, height), 2 is the thickness
        pygame.draw.rect(main.pygame_display, self.colours["grey"], (rumble_table_start[0]+1, rumble_table_start[1]+1, (self.rumble_width*self.rumble_scaling)+2, (self.rumble_height*self.rumble_scaling)+2), 1)
        punch_start_location = [rumble_table_start[0]+2, rumble_table_start[1]+2 + (20 * self.rumble_scaling)]
        greyscale_colour = self.colours["grey"]
        colourful_colour = self.colours["yellow"]

        for groups in rumble_dictionary[rumble_mins]:
            
            
            drop_off = rumble_dictionary[rumble_mins][groups]["drop_off"]
            length = rumble_dictionary[rumble_mins][groups]["rows"]
            difference = rumble_dictionary[rumble_mins][groups]["difference"]
            width =  rumble_dictionary[rumble_mins][groups]["base_width"]

            if 7 < length < 19:
                text_colour = colourful_colour
                block_colour = colourful_colour
                colourful_colour = self.colours["yellow"] if colourful_colour == self.colours["gold"] else self.colours["gold"]
            else:
                text_colour = self.colours["grey"]
                block_colour = greyscale_colour
                greyscale_colour = self.colours["grey"] if greyscale_colour == self.colours["white"] else self.colours["white"]
            
            punch_text = self.my_font_rumble.render(str(groups), True, text_colour)
            drop_off_text = self.my_font_rumble_small.render(str(drop_off), True, self.colours["black"])
            punch_start_location[1] -= difference * self.rumble_scaling
            
            if main.configs.rumble_bars_as_natural_width:
                pygame.draw.rect(main.pygame_display, block_colour, (punch_start_location[0], punch_start_location[1], (self.rumble_width*self.rumble_scaling*width/9), (difference*self.rumble_scaling)))
            else:
                pygame.draw.rect(main.pygame_display, block_colour, (punch_start_location[0], punch_start_location[1], (self.rumble_width*self.rumble_scaling), (difference*self.rumble_scaling)))
            if groups > 9:
                main.pygame_display.blit(punch_text, (punch_start_location[0] - (self.rumble_scaling * 1.5), punch_start_location[1]))
            else:
                main.pygame_display.blit(punch_text, (punch_start_location[0] - (self.rumble_scaling * 0.85), punch_start_location[1]))
            if main.configs.show_drop_off_numbers:
                main.pygame_display.blit(drop_off_text, (punch_start_location[0] + (self.rumble_scaling * 0.1), punch_start_location[1]))