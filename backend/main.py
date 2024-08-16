from maths import maths_subjective_pipeline
from utils.helpers import create_pdf
from logger import setup_logging


if __name__ == "__main__":
    logger = setup_logging()
    logger.info("The logging has started!!!")
    question = "What is Graph theory? What are all the elements and theorems are there in graph theory? Explain an example for each theorem in detail."
    response = maths_subjective_pipeline(question)
    print(response)
    create_pdf(str(response))
    