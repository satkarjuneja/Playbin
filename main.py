from player import Player
from ui import UI
from analyzer import Audio_Processing 


def main():
    AP=Audio_Processing()
    player = Player(AP)
    ui = UI(player)
    ui.run()


if __name__ == "__main__":
    main()