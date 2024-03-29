from dataclasses import dataclass, field
from enum import Enum, auto
import skrf as rf


class ComponentType(Enum):
    L = auto()
    C = auto()
    V = auto()
    I = auto()  # noqa
    R = auto()
    T = auto()


PreFix = {-15: "f", -12: "p", -9: "n", -6: "µ", -3: "m", 0: "", 3: "k"}
Unit = {"L": "H", "C": "F", "V": "V", "I": "A", "R": "Ω", "T": "rad"}


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
        return f"{self.full_name()} {self.node[0]} {self.node[1]} {value}{Unit[str(self.type)]}"

    def readable_value(self) -> str:
        for n, p in PreFix.items():
            if self.value < 10 ** (n + 3):
                return f"{self.value*10**(-n):.3f} {p}"
        last = list(PreFix)[-1]
        return f"{self.value*10**last:.3f} {PreFix[last]}"

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
