from game import Game
from state_manager import StateManager

if __name__ == "__main__":
    #Game().start()
    state_manager = StateManager()
    state_manager.start()
    state_manager.main_game_loop()

