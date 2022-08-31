import argparse
import logging
import os
import sys
from logging.handlers import RotatingFileHandler

from mage_game import controller, eventmanager, model, view

logger = logging.getLogger(__name__)


def _init_logger(args: argparse.Namespace) -> None:
    """
    Initializes the logger from a log path.

    :param log_path: the log path to dump logs
    """
    os.makedirs(args.log_path, exist_ok=True)
    log_file_path = os.path.join(args.log_path, "game.log")
    logging.basicConfig(
        handlers=[RotatingFileHandler(
            log_file_path,
            backupCount=10,
            maxBytes=1000000,
            encoding="utf-8"
        )],
        level=args.log_level,
        format='%(asctime)s,%(msecs)d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s',
        datefmt='%Y-%m-%d:%H:%M:%S',
    )
    logger.info(f"Initialized logger: files dumped to {args.log_path}")


def _run_with_crash_handling(game_model: model.GameEngine, log_path: str):
    """
    Runs the game while waiting for errors.

    :param game_model: the game engine that runs the game
    :param log_path: the path to the log to print in case of a crash
    """
    try:
        game_model.run()
    except Exception as e:
        logger.exception(e)
        print(f"Game crashed! Check logs: {log_path}")
        sys.exit(1)


def _process_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--log_level",
        type=str,
        required=False,
        choices=logging._nameToLevel.keys(),
        default="WARNING"
    )
    parser.add_argument(
        "--log_path",
        type=str,
        required=False,
        default=os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            "logs"
        )
    )
    args = parser.parse_args()
    return args


def run():
    """
    The main function that launches the game.
    """
    args = _process_arguments()
    _init_logger(args)
    event_manager = eventmanager.EventManager()
    game_model = model.GameEngine(event_manager)
    keyboard = controller.MouseAndKeyboard(event_manager, game_model)
    graphics = view.GraphicalView(event_manager, game_model)
    _run_with_crash_handling(game_model, args.log_path)


if __name__ == '__main__':
    run()
