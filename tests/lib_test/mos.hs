dimension:
    int n "finger number"
    double w "finger width"
    double l "finger length"
    double a_ext "active extension on gate"
    double g_ext "gate extension on active"
geometry:
    active
        Rec 0 g_ext n*l+(n+1)*a_ext w
    gate
        Rep 1 n a_ext Rec a_ext 0 l 2*g_ext+w
