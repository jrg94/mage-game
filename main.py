import logging
import os
from logging.handlers import RotatingFileHandler

from mage_game import controller, eventmanager, model, view

logger = logging.getLogger(__name__)


def _init_logger():
    os.makedirs(os.path.join(os.path.abspath(
        os.path.dirname(__file__)), "logs"), exist_ok=True)
    log_path = os.path.join(os.path.abspath(
        os.path.dirname(__file__)), "logs", "game.log")
    logging.basicConfig(
        handlers=[RotatingFileHandler(
            log_path, backupCount=10, maxBytes=1000000, encoding="utf-8")],
        level=logging.DEBUG,
        format='%(asctime)s,%(msecs)d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s',
        datefmt='%Y-%m-%d:%H:%M:%S',
    )
    logger.info(f"Initialized logger: files dumped to {log_path}")


def run():
    _init_logger()
    event_manager = eventmanager.EventManager()
    gamemodel = model.GameEngine(event_manager)
    keyboard = controller.MouseAndKeyboard(event_manager, gamemodel)
    graphics = view.GraphicalView(event_manager, gamemodel)
    gamemodel.run()


if __name__ == '__main__':
    run()
