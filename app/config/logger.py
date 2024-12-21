import logging
from pathlib import Path



class LoggerSetup:
    def __init__(self, directory:Path):
        self.directory = directory # путь к папке где дует сам файл
        self.log_file = self.directory/'app.log'# путь с файлов в конце
        self.logger = None
        self._ensure_directory_and_file()
    
    def _ensure_directory_and_file(self):
        """
        если такой дириктории нету directory:Path - создай
        если такой папки нету self.directory/'app.log' - создай
        """
        if not self.directory.exists():
            self.directory.mkdir(parents=True, exist_ok=True)
        
        if not self.log_file.exists():
            self.log_file.touch
    
    def setup_logger(self)->logging.Logger:
        if self.logger is None:
            #устанавливаем формат логов
            formating = f'%(levelname)s - %(asctime)s  -%(filename)s - %(message)s'
            formatter = logging.Formatter(formating)

            #открывает указынный файл и записывает туда логи
            handler = logging.FileHandler(self.log_file)
            handler.setFormatter(formatter)

            
            self.logger = logging.getLogger('global_log')
            self.logger.setLevel(logging.INFO)

            if not self.logger.hasHandlers():
                self.logger.addHandler(handler)
        
        return self.logger

path = Path(__file__).absolute().parent.parent
logger_setup = LoggerSetup(path)
logger = logger_setup.setup_logger()

