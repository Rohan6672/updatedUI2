"""FastAPI application setup and lifecycle management."""

from contextlib import asynccontextmanager
import os
import asyncio
import logging
from typing import Any, AsyncGenerator

from fastapi import FastAPI, Path
from fastapi.middleware.cors import CORSMiddleware

from src.config.load_config import load_config

from src.routers import discover_trends
from src.utils.setup_log import setup_logger

# Initialize logger
logger = setup_logger()
config_data = load_config()


def handle_exception(loop, context):
    """Handle unhandled asyncio exceptions, specifically Google GenAI client errors."""
    exception = context.get('exception')
    if exception and isinstance(exception, AttributeError):
        if '_async_httpx_client' in str(exception):
            # Suppress Google GenAI client cleanup errors
            logger.debug(f"Suppressed Google GenAI client error: {exception}")
            return
    
    # For other exceptions, log them normally
    logger.error(f"Unhandled asyncio exception: {context}")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, Any]:
    """Handles application startup and shutdown events."""
    logger.info("=== APPLICATION STARTUP ===")
    logger.info("Application startup...")
    
    # Set up asyncio exception handler
    loop = asyncio.get_event_loop()
    loop.set_exception_handler(handle_exception)
    logger.info("Exception handler configured.")
    
    try:
        output_dir = config_data.get("output_folder", {}).get("OUTPUT_DIR", "src/data/outputs")
        # Convert to absolute path to ensure it's created in the right location
        output_dir = os.path.abspath(output_dir)
        os.makedirs(output_dir, exist_ok=True)
        logger.info(f"Output directory ensured: {output_dir}")
    except ConnectionError as e:
        logger.critical(f"CRITICAL FAILURE: Could not initialize Redis pool: {e}")
        raise RuntimeError("Failed Redis connection") from e

    logger.info("Application startup complete.")
    logger.info("=== APPLICATION READY ===")
    yield

    logger.info("=== APPLICATION SHUTDOWN ===")
    logger.info("Application shutdown...")
    logger.info("Application shutdown complete.")
    logger.info("=== APPLICATION STOPPED ===")


def create_app() -> FastAPI:
    """Application factory: Creates and configures the FastAPI instance."""
    logger.info("=== CREATING FASTAPI APPLICATION ===")
    app_instance = FastAPI(
        title="Sephora Trends API",
        description="Beauty trends research and analysis API",
        version="1.0.0",
        lifespan=lifespan,
    )
    logger.info("FastAPI instance created.")

    logger.info("Configuring CORS middleware...")
    app_instance.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    logger.info("CORS middleware configured.")

    logger.info("Including discover_trends router...")
    app_instance.include_router(discover_trends.router)
    logger.info("Discover trends router included successfully.")
    
    logger.info("=== APPLICATION CREATED ===")
    return app_instance


app = create_app()


@app.get("/", tags=["Health"])
async def read_root():
    """Root endpoint for health check."""
    return {"status": "ok"}


