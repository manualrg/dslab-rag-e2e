import logging
from src import utils, conf

def main():
    logger = logging.getLogger(__name__)
    logger.info("Application started")
    print("Hello from dslab-rag-e2e!")

    conf.example()

    utils.example()



if __name__ == "__main__":
    utils.setup_logging()
    main()
