"""
Async handler for Streamlit to avoid event loop conflicts
"""

import asyncio
import concurrent.futures
import logging
import threading
from typing import Any, Coroutine

logger = logging.getLogger(__name__)


class StreamlitAsyncHandler:
    """
    Handles async operations in Streamlit to avoid event loop conflicts.
    """
    
    def __init__(self):
        self._executor = None
        self._loop = None
        
    def _get_executor(self):
        """Get or create a thread pool executor."""
        if self._executor is None:
            self._executor = concurrent.futures.ThreadPoolExecutor(
                max_workers=2,
                thread_name_prefix="streamlit-async"
            )
        return self._executor
        
    def _run_in_new_loop(self, coro: Coroutine) -> Any:
        """Run a coroutine in a new event loop in a separate thread."""
        def run_coro():
            # Create a new event loop for this thread
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                return loop.run_until_complete(coro)
            finally:
                loop.close()
                
        return run_coro()
        
    def run_async(self, coro: Coroutine, timeout: int = 60) -> Any:
        """
        Run an async coroutine safely in Streamlit context.
        
        Args:
            coro: The coroutine to run
            timeout: Timeout in seconds
            
        Returns:
            The result of the coroutine
        """
        logger.info(f"🔄 Running async operation with timeout: {timeout}s")
        
        try:
            # Check if there's already an event loop running
            try:
                current_loop = asyncio.get_running_loop()
                if current_loop.is_running():
                    logger.info("🔍 Detected existing event loop, using ThreadPoolExecutor")
                    
                    # Use ThreadPoolExecutor to run in a separate thread with new loop
                    executor = self._get_executor()
                    future = executor.submit(self._run_in_new_loop, coro)
                    result = future.result(timeout=timeout)
                    
                    logger.info("✅ Async operation completed successfully")
                    return result
                else:
                    # Loop exists but not running, safe to use asyncio.run
                    logger.info("🔍 Event loop exists but not running, using asyncio.run")
                    result = asyncio.run(coro)
                    logger.info("✅ Async operation completed successfully")
                    return result
                    
            except RuntimeError as e:
                if "no running event loop" in str(e).lower():
                    # No event loop running, safe to use asyncio.run
                    logger.info("🔍 No existing event loop, using asyncio.run")
                    result = asyncio.run(coro)
                    logger.info("✅ Async operation completed successfully")
                    return result
                else:
                    # Other RuntimeError, re-raise
                    raise
                
        except concurrent.futures.TimeoutError:
            logger.error(f"⏰ Async operation timed out after {timeout}s")
            raise TimeoutError(f"Operation timed out after {timeout} seconds")
        except Exception as e:
            logger.error(f"💥 Async operation failed: {e}")
            raise
            
    def cleanup(self):
        """Clean up resources."""
        if self._executor:
            logger.info("🧹 Cleaning up async handler")
            self._executor.shutdown(wait=True)
            self._executor = None


# Global instance for Streamlit
streamlit_async_handler = StreamlitAsyncHandler()
