import logging
import time
from functools import wraps
from django.conf import settings

logger = logging.getLogger('events')

def log_view_performance(func):
    """
    Decorator to log view performance metrics including elapsed time
    """
    @wraps(func)
    def wrapper(view_instance, request, *args, **kwargs):
        # Get view class name and method
        view_name = view_instance.__class__.__name__
        method = request.method
        
        # Start timing
        start_time = time.time()
        
        # Log request start
        logger.info(
            f"VIEW_START: {view_name} | Method: {method} | "
            f"User: {request.user.username if request.user.is_authenticated else 'Anonymous'} | "
            f"Path: {request.path} | Args: {args} | Kwargs: {kwargs}"
        )
        
        try:
            # Execute the view
            response = func(view_instance, request, *args, **kwargs)
            
            # Calculate elapsed time
            elapsed_time = time.time() - start_time
            
            # Log successful completion
            logger.info(
                f"VIEW_SUCCESS: {view_name} | Method: {method} | "
                f"Status: {response.status_code} | "
                f"Elapsed: {elapsed_time:.3f}s | "
                f"User: {request.user.username if request.user.is_authenticated else 'Anonymous'}"
            )
            
            return response
            
        except Exception as e:
            # Calculate elapsed time for failed request
            elapsed_time = time.time() - start_time
            
            # Log error
            logger.error(
                f"VIEW_ERROR: {view_name} | Method: {method} | "
                f"Error: {str(e)} | "
                f"Elapsed: {elapsed_time:.3f}s | "
                f"User: {request.user.username if request.user.is_authenticated else 'Anonymous'} | "
                f"Path: {request.path}",
                exc_info=True
            )
            
            # Re-raise the exception
            raise
    
    return wrapper

def log_queryset_performance(queryset, operation="fetch"):
    """
    Log queryset performance metrics
    """
    start_time = time.time()
    
    try:
        # Execute the queryset
        result = list(queryset) if operation == "fetch" else queryset
        
        # Calculate elapsed time
        elapsed_time = time.time() - start_time
        
        # Log performance
        logger.debug(
            f"QUERYSET_{operation.upper()}: Model: {queryset.model.__name__} | "
            f"Count: {len(result) if operation == 'fetch' else 'N/A'} | "
            f"Elapsed: {elapsed_time:.3f}s | "
            f"Query: {str(queryset.query)}"
        )
        
        return result
        
    except Exception as e:
        elapsed_time = time.time() - start_time
        logger.error(
            f"QUERYSET_{operation.upper()}_ERROR: Model: {queryset.model.__name__} | "
            f"Error: {str(e)} | "
            f"Elapsed: {elapsed_time:.3f}s",
            exc_info=True
        )
        raise

def log_business_action(action, details=None, user=None):
    """
    Log business logic actions
    """
    user_info = user.username if user else 'Anonymous'
    
    message = f"BUSINESS_ACTION: {action} | User: {user_info}"
    if details:
        message += f" | Details: {details}"
    
    logger.info(message)

def log_validation_error(serializer_name, errors, user=None):
    """
    Log validation errors
    """
    user_info = user.username if user else 'Anonymous'
    
    logger.warning(
        f"VALIDATION_ERROR: Serializer: {serializer_name} | "
        f"User: {user_info} | "
        f"Errors: {errors}"
    )
