from hades.devices.device import generate, Step
from hades.devices.inductor import Specifications, Inductor

spec = Specifications(L=1e-9, f_0 = 1e9)

generate(Inductor("test", "sky130"), spec, stop=Step.dimensions)
