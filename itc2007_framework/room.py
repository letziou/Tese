from dataclasses import dataclass

@dataclass(frozen=True)
class Room:
    number: int     # Identifier of the room
    capacity: int   # Capacity of the room
    penalty: int    # Penalty of the room

    def __hash__(self):
        return hash(self.number)
    
    def __eq__(self, other):
        if not isinstance(other, Room):
            return False
        return self.number == other.number

    def __str__(self) -> str:
        return f"Room(id={self.number}, capacity={self.capacity}, penalty={self.penalty})"
