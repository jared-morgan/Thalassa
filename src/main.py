import pygame
from pathlib import Path
import timeit

from code.gui import GUI
from code.sounds import Sounds
from code.configs import Configs
from code.chatlogs import Chatlogs
from code.fray import Fray

class Main:
    def __init__(self):

        pygame.init()
        pygame.mixer.init()
        pygame.display.set_caption('Pirate Helper')
        

        self.crashed = False

        self.src_path = Path.cwd() / "src"
        # self.puzzles_image_path = self.src_dir / "media" / "global" / "puzzle_previews_small.png"
        # self.img_puzzles_image = pygame.image.load(self.puzzles_image_path)

        self.configs = Configs()

        self.pygame_display = pygame.display.set_mode((250, 600))
        self.clock = pygame.time.Clock()

        self.gui = GUI(self.src_path, self.configs.rumble_scaling)
        self.sounds = Sounds(self.src_path)
        self.chatlogs = Chatlogs()
        self.fray = Fray(self.src_path)
        self.gui.create_homun_colour_bars(self)

        self.maximum_players = [4, 4, 3, 3, 2]
        self.vampire_delay = 2800

        self.swabbies_on_board = 0
        self.plank_swabbie = False
        self.settings_menu_open = False
        
        self.reset_stats()


    def reset_stats(self):
        self.players_on_board = 0
        self.landed = True
        self.overrun = False
        self.frays_won = 0
        self.rumble_active = 0
        self.sf_active = 0
        self.looting_active = 0
        self.vargas_seen = False
        self.homu_colours = {"red": 0, "green": 0, "blue": 0, "yellow": 0}

        self.swabbie_alert_last_played = 0
        self.plank_swabbie_flash_speed = 500


    def process_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.crashed = True
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_c:
                    self.configs.mode = "CI"
                elif event.key == pygame.K_v:
                    self.configs.mode = "VL"
                elif event.key == pygame.K_r:
                    self.rumble_active = 0 if self.rumble_active else pygame.time.get_ticks()
                    self.sf_active, self.looting_active = 0, 0
                elif event.key == pygame.K_s:
                    self.sf_active = 0 if self.sf_active else pygame.time.get_ticks()
                    self.rumble_active, self.looting_active = 0, 0
                elif event.key == pygame.K_l:
                    self.looting_active = 0 if self.looting_active else pygame.time.get_ticks()
                    self.rumble_active, self.sf_active = 0, 0
                elif event.key in [pygame.K_0, pygame.K_KP0]: # Pressing either 0 removes the plank swabbie alert incase counter was opened part way through the CI
                    print(F"TEST")
                    self.plank_swabbie = False
                    self.swabbies_on_board = 0

            elif event.type == pygame.MOUSEBUTTONUP:
                mouse_pos = pygame.mouse.get_pos()
                self.fray.check_for_homun_click(main, mouse_pos, event.button)
                if self.gui.copy_button.is_clicked(mouse_pos):
                    self.fray.copy_homun_colours()
                if self.gui.reset_button.is_clicked(mouse_pos):
                    self.fray.reset_homun()


    
    def calculate_looting_timer(self):
        time_passed = pygame.time.get_ticks() - self.looting_active
        if time_passed > 120000: # 2 minutes
            self.looting_active = 0
            if self.configs.mode == "CI": 
                self.plank_swabbie_check()
        self.gui.update_time_passed_text(main, time_passed)

    
    def plank_swabbie_check(self):
        if self.swabbies_on_board == 0: 
            return
        
        player_count = self.players_on_board + self.swabbies_on_board
        try:
            max_players = self.maximum_players[self.frays_won]
        except:
            max_players = 2 # fray count larger than relevant indexes
    

        if player_count > max_players:
            self.plank_swabbie = True
        else:
            self.plank_swabbie = False

        if self.plank_swabbie:
            # if (pygame.time.get_ticks() // self.plank_swabbie_flash_speed) % 2 == 0: # Disabled because I don't want it to flash.
            #     plank_swabbie_colour = "red"
            # else:
            #     plank_swabbie_colour = "white"
            self.gui.update_plank_swabbie_text("red")
            
            if (pygame.time.get_ticks() - self.swabbie_alert_last_played > 6500) and self.configs.play_swabbie_warning_sound:
                self.sounds.play_sound("plank_swabbie")
                self.swabbie_alert_last_played = pygame.time.get_ticks()
        

    def run(self):
        
        while not self.crashed:

            self.gui.reset_gui(main)

            self.process_events()

            self.chatlogs.update_chatlogs(main)

            if self.chatlogs.new_lines:
                self.chatlogs.process_updated_chatlogs(main)

            if self.settings_menu_open:
                self.gui.update_settings_menu(main)

            elif self.looting_active:
                self.calculate_looting_timer()

            elif self.rumble_active:
                self.fray.update_rumble(main)

            elif self.sf_active and self.configs.mode == "CI": # Only care about this for homus
                self.fray.update_sf(main)


            self.gui.update_gui(main)

            pygame.display.update()
            self.clock.tick(self.configs.fps_cap)




        pygame.quit()


if __name__ == "__main__":
    main = Main()
    main.run()