specification:
    float L "inductance value"
    float Q "quality factor"
    float Fw "working frequency"
    float Fesr "self resonant frequency"
parameter:
    float K1
    float K2
model:
    do = di + n*w + (n+1)*g
    da = (do+di)/2
    rho = (do - di) / (do + di)
    L = K1*n^2*da/(1*K2*rho)
    Q = 30
dimension:
    int n "turn number"
    float di "inner diameter"
    float w "trace width"
    float g "gap between trace"
geometry:
    insert hexagonal geometry
simulation:
    em: one_port
        L = imag(Z(1,1))/(2*pi*Fw)
        Q = imag(Z(1,1)) / real(Z(1, 1))
    spice:
