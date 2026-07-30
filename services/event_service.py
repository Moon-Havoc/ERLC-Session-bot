"""Internal event service for SessionCore."""

from __future__ import annotations

from typing import Callable, Dict, List, Any, Set
from asyncio import Lock
import asyncio

from utils.logger import get_logger

logger = get_logger(__name__)


class Event:
    """Represents an internal event."""
    
    def __init__(self, name: str, data: Dict[str, Any]) -> None:
        """Initialize an event."""
        self.name = name
        self.data = data
        self.timestamp = asyncio.get_event_loop().time()


class EventListener:
    """Represents an event listener."""
    
    def __init__(self, event_name: str, callback: Callable[[Event], None], priority: int = 0) -> None:
        """Initialize an event listener."""
        self.event_name = event_name
        self.callback = callback
        self.priority = priority
        self.id = id(callback)


class EventService:
    """Internal event service for pub/sub pattern."""
    
    def __init__(self) -> None:
        """Initialize event service."""
        self._listeners: Dict[str, List[EventListener]] = {}
        self._lock = Lock()
    
    async def subscribe(
        self,
        event_name: str,
        callback: Callable[[Event], None],
        priority: int = 0
    ) -> EventListener:
        """Subscribe to an event."""
        async with self._lock:
            if event_name not in self._listeners:
                self._listeners[event_name] = []
            
            listener = EventListener(event_name, callback, priority)
            self._listeners[event_name].append(listener)
            
            # Sort by priority (higher priority first)
            self._listeners[event_name].sort(key=lambda x: x.priority, reverse=True)
            
            logger.debug(f"Subscribed to event: {event_name}")
            return listener
    
    async def unsubscribe(self, listener: EventListener) -> bool:
        """Unsubscribe from an event."""
        async with self._lock:
            if listener.event_name in self._listeners:
                try:
                    self._listeners[listener.event_name].remove(listener)
                    logger.debug(f"Unsubscribed from event: {listener.event_name}")
                    return True
                except ValueError:
                    pass
            return False
    
    async def publish(self, event_name: str, data: Dict[str, Any]) -> None:
        """Publish an event to all subscribers."""
        event = Event(event_name, data)
        
        async with self._lock:
            listeners = self._listeners.get(event_name, []).copy()
        
        if not listeners:
            logger.debug(f"No listeners for event: {event_name}")
            return
        
        # Execute all listeners
        for listener in listeners:
            try:
                await listener.callback(event)
            except Exception as e:
                logger.error(f"Error in event listener for {event_name}: {e}")
    
    async def publish_and_wait(
        self,
        event_name: str,
        data: Dict[str, Any],
        timeout: float = 5.0
    ) -> None:
        """Publish an event and wait for all listeners to complete."""
        event = Event(event_name, data)
        
        async with self._lock:
            listeners = self._listeners.get(event_name, []).copy()
        
        if not listeners:
            logger.debug(f"No listeners for event: {event_name}")
            return
        
        # Execute all listeners and wait for completion
        tasks = []
        for listener in listeners:
            try:
                task = asyncio.create_task(listener.callback(event))
                tasks.append(task)
            except Exception as e:
                logger.error(f"Error creating task for {event_name}: {e}")
        
        if tasks:
            await asyncio.wait(tasks, timeout=timeout)
    
    def get_listener_count(self, event_name: str) -> int:
        """Get the number of listeners for an event."""
        return len(self._listeners.get(event_name, []))
    
    def get_all_event_names(self) -> List[str]:
        """Get all event names that have listeners."""
        return list(self._listeners.keys())


# Global event service instance
event_service = EventService()

# Event name constants
EVENT_SESSION_STARTED = "session_started"
EVENT_SESSION_ENDED = "session_ended"
EVENT_VOTE_ADDED = "vote_added"
EVENT_BOOST_ADDED = "boost_added"
