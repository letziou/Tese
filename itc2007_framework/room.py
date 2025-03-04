from dataclasses import dataclass

@dataclass(frozen=True) # Makes the attributes immutable
class Room:
    number: int     # identifier of the room
    capacity: int   # capacity of the room
    penalty: int    # penalty of the room

    def __str__(self) -> str:
        return f"Room(id={self.number}, capacity={self.capacity}, penalty={self.penalty})"
