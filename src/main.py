from mangum import Mangum
from .app import create_fast_api_app
from src.utils.logger import logger

app = create_fast_api_app()

logger.debug("Initializing Mangum lambda handler")
handler = Mangum(app=app)
