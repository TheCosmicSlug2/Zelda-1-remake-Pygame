from physics import Physics

class Entity:
    def __init__(self) -> None:

        self.physics = Physics()

        # C'est peut être chiant parce que si y'a bcp d'ennemis, on peut avoir bcp d'instances de cette classe, mais à voir 
