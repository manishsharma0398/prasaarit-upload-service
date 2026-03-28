from mangum import Mangum

from src.utils.logger import logger

from .app import create_fast_api_app

app = create_fast_api_app()

logger.debug("Initializing Mangum lambda handler")
handler = Mangum(app=app)
