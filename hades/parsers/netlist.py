from dataclasses import dataclass, field
from hades.models.tools import eng
from enum import Enum, auto
import skrf as rf


class ComponentType(Enum):
    L = auto()
    C = auto()
    V = auto()
    I = auto()  # noqa
    R = auto()
    T = auto()
    K = auto()


Unit = {"L": "H", "C": "F", "V": "V", "I": "A", "R": "Ω", "T": "rad", "K": ""}


@dataclass
class Component:
    """
    Represents a component.
    """

    type: ComponentType
    name: str
    value: float
    node: tuple[str, str]

    def __repr__(self) -> str:
        value = self.readable_value()
        return f"{self.full_name()} {self.node[0]} {self.node[1]} {value}"

    def readable_value(self) -> str:
        return f"{eng(self.value)}{Unit[self.type]}"

    def full_name(self):
        return str(self.type) + self.name

    def network(self, media: rf.media.Media):
        if "0" in self.node:
            if self.type == "C":
                sp = media.shunt_capacitor(self.value, name=self.full_name())
            elif self.type == "L":
                sp = media.shunt_inductor(self.value, name=self.full_name())
            else:
                raise ValueError("Unsupported type of components.")
        else:
            if self.type == "C":
                sp = media.capacitor(self.value, name=self.full_name())
            elif self.type == "L":
                sp = media.inductor(self.value, name=self.full_name())
            else:
                raise ValueError("Unsupported type of components.")
        return sp


@dataclass
class Netlist:
    """
    Represents a Netlist. The connexion graph is stored in circuit.
    The spice netlist can be generated using the spice function.
    """

    name: str
    circuit: list[Component] = field(default_factory=list)

    def append(self, other: Component):
        self.circuit.append(other)

    def spice(self):
        spice = f"#{self.name}\n"
        for comp in self.circuit:
            spice += f"{comp}\n"
        return spice
