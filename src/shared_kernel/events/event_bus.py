"""
Minimal in-process event bus. OPTIONAL — see ARCHITECTURE.md critic note #5.
If this costs your team more than ~2 hours to wire in, skip it and call use cases
directly through their ports instead. This is decoupling sugar, not a requirement.
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Callable
from collections import defaultdict


@dataclass(frozen=True)
class DomainEvent:
    occurred_at: datetime = field(default_factory=datetime.utcnow)


class EventBus:
    def __init__(self) -> None:
        self._subscribers: dict[type, list[Callable]] = defaultdict(list)

    def subscribe(self, event_type: type, handler: Callable) -> None:
        self._subscribers[event_type].append(handler)

    def publish(self, event: DomainEvent) -> None:
        for handler in self._subscribers[type(event)]:
            handler(event)  # deliberately synchronous — see note above


# Example events a context might define and publish (create these in the owning context's
# domain layer, not here — this file only hosts the mechanism):
#   EntityExtracted(DomainEvent)
#   RelationshipInferred(DomainEvent)
#   GraphUpdated(DomainEvent)
