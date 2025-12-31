"""Shared utilities for BigQuery operations."""
import time


def retry_query_with_backoff(query_func, max_retries=3, initial_delay=2):
    """
    Retry a BigQuery query with exponential backoff.

    This handles the data latency issue where streaming data
    hasn't fully propagated to BigQuery yet.

    Args:
        query_func: Function that executes the query and returns results
        max_retries: Maximum number of retry attempts
        initial_delay: Initial delay in seconds (doubles each retry)

    Returns:
        Query results or None if all retries exhausted
    """
    delay = initial_delay

    for attempt in range(max_retries):
        try:
            result = query_func()
            if result is not None:
                if attempt > 0:
                    print(f"[BigQuery Retry] Data found after {attempt + 1} attempt(s)")
                return result

            # Data not found yet, wait before retrying
            if attempt < max_retries - 1:
                print(f"[BigQuery Retry] No data yet, waiting {delay}s before retry {attempt + 2}/{max_retries}...")
                time.sleep(delay)
                delay *= 2  # Exponential backoff
        except Exception as e:
            print(f"[BigQuery Retry] Query error on attempt {attempt + 1}: {str(e)[:100]}")
            if attempt < max_retries - 1:
                time.sleep(delay)
                delay *= 2
            else:
                raise

    return None
