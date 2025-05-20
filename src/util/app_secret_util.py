from util.logging import log

# Simple util which works with older configs that dont supply the secret as a file
def secret_data(provided: str = None) -> str:
    logger = log()
    # Provided can either be the value, or if it ends with .txt it is a file that needs to be read
    if provided and provided.endswith(".txt"):
        logger.info(f"Reading secret data from file: {provided}")
        try:
            with open(provided, "r") as file:
                return file.read().strip()
        except FileNotFoundError:
            raise FileNotFoundError(f"File {provided} not found.")
    elif provided:
        logger.info(f"Using provided secret data: {provided}")
        return provided
    else:
        raise ValueError("No secret data provided.")