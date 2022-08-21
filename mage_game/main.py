import eventmanager
import model
import view
import controller

def run():
    evManager = eventmanager.EventManager()
    gamemodel = model.GameEngine(evManager)
    keyboard = controller.MouseAndKeyboard(evManager, gamemodel)
    graphics = view.GraphicalView(evManager, gamemodel)
    gamemodel.run()

if __name__ == '__main__':
    run()
