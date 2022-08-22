import eventmanager
import model
import view
import controller

def run():
    event_manager = eventmanager.EventManager()
    gamemodel = model.GameEngine(event_manager)
    keyboard = controller.MouseAndKeyboard(event_manager, gamemodel)
    graphics = view.GraphicalView(event_manager, gamemodel)
    gamemodel.run()

if __name__ == '__main__':
    run()
