"""Service container for dependency injection."""

from __future__ import annotations

from typing import Optional, Dict, Any, TypeVar, Type, Callable
from database import Database
from services.config_service import ConfigService
from services.branding import BrandingService
from services.session_service import SessionService
from services.event_service import EventService
from services.statistics_service import StatisticsService
from services.audit_service import AuditService
from utils.logger import get_logger

logger = get_logger(__name__)

T = TypeVar('T')


class ServiceContainer:
    """Lightweight dependency injection container for long-lived services."""
    
    def __init__(self) -> None:
        """Initialize service container."""
        self._services: Dict[str, Any] = {}
        self._singletons: Dict[str, Any] = {}
        self._initialized = False
    
    def register(self, name: str, factory: Callable[[], T], singleton: bool = True) -> None:
        """Register a service with the container."""
        if name in self._services:
            logger.warning(f"Service '{name}' already registered, overwriting")
        
        self._services[name] = {
            'factory': factory,
            'singleton': singleton
        }
        logger.debug(f"Registered service: {name}")
    
    def get(self, name: str) -> Optional[T]:
        """Get a service from the container."""
        if name not in self._services:
            logger.error(f"Service '{name}' not registered")
            return None
        
        service_config = self._services[name]
        
        if service_config['singleton']:
            if name not in self._singletons:
                self._singletons[name] = service_config['factory']()
                logger.debug(f"Created singleton instance: {name}")
            return self._singletons[name]
        else:
            return service_config['factory']()
    
    def get_singleton(self, name: str) -> Optional[T]:
        """Get a singleton service from the container."""
        return self.get(name)
    
    def has(self, name: str) -> bool:
        """Check if a service is registered."""
        return name in self._services
    
    def initialize(self) -> None:
        """Initialize all singleton services."""
        if self._initialized:
            logger.warning("Service container already initialized")
            return
        
        logger.info("Initializing service container...")
        
        # Initialize all singleton services
        for name, config in self._services.items():
            if config['singleton'] and name not in self._singletons:
                try:
                    self._singletons[name] = config['factory']()
                    logger.debug(f"Initialized service: {name}")
                except Exception as e:
                    logger.error(f"Failed to initialize service '{name}': {e}")
        
        self._initialized = True
        logger.info("Service container initialized")
    
    def shutdown(self) -> None:
        """Shutdown all services that support cleanup."""
        logger.info("Shutting down service container...")
        
        # Shutdown services in reverse order of registration
        for name in reversed(list(self._services.keys())):
            if name in self._singletons:
                service = self._singletons[name]
                if hasattr(service, 'shutdown'):
                    try:
                        import asyncio
                        if asyncio.iscoroutinefunction(service.shutdown):
                            # Run async shutdown
                            loop = asyncio.get_event_loop()
                            loop.run_until_complete(service.shutdown())
                        else:
                            service.shutdown()
                        logger.debug(f"Shutdown service: {name}")
                    except Exception as e:
                        logger.error(f"Failed to shutdown service '{name}': {e}")
        
        self._singletons.clear()
        self._initialized = False
        logger.info("Service container shutdown complete")


# Global service container instance
service_container = ServiceContainer()


def initialize_container() -> None:
    """Initialize the global service container with all services."""
    from database import database
    
    # Register database (singleton)
    service_container.register('database', lambda: database, singleton=True)
    
    # Register ConfigService (singleton)
    service_container.register('config_service', lambda: ConfigService(), singleton=True)
    
    # Register BrandingService (singleton)
    service_container.register('branding_service', lambda: BrandingService(), singleton=True)
    
    # Register EventService (singleton)
    service_container.register('event_service', lambda: EventService(), singleton=True)
    
    # Register SessionService (singleton)
    service_container.register('session_service', lambda: SessionService(), singleton=True)
    
    # Register StatisticsService (singleton)
    service_container.register('statistics_service', lambda: StatisticsService(), singleton=True)
    
    # Register AuditService (singleton)
    service_container.register('audit_service', lambda: AuditService(), singleton=True)
    
    # Initialize all singletons
    service_container.initialize()


def get_container() -> ServiceContainer:
    """Get the global service container."""
    return service_container
