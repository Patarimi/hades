from dataclasses import dataclass


@dataclass
class Layer:
    data: int
    d_type: int = 0

    def __str__(self):
        return f"{self.data}/{self.d_type}"
