import controller.game_controller as controller
import model.game_model as model
import view.game_view as view

if __name__ == '__main__':
    game_model = model.GameState()
    game_view = view.GameView()
    game_controller = controller.GameController(game_model, game_view)
    game_view.register_observer(game_controller)
    game_controller.run()
    