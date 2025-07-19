class Corpo_Celeste:
    def __init__(
        self,
        massa,
        raio,
        color,
        name,
        pos_x,
        pos_y,
        vel_x=0.0,
        vel_y=0.0,
    ):
        self.massa = massa
        self.raio = raio
        self.color = color
        self.name = name
        self.pos_x = float(pos_x)
        self.pos_y = float(pos_y)
        self.vel_x = float(vel_x)
        self.vel_y = float(vel_y)
        self.trace = []

    # essa funcao é pro equacoes_movimento
    # x, y, vx, vy = estado
    def return_estado(self):
        info = [self.pos_x, self.pos_y, self.vel_x, self.vel_y]
        return info

    def return_pos(self):
        info = [self.pos_x, self.pos_y]
        return info

    def return_vel(self):
        info = [self.vel_x, self.vel_y]
        return info

    def return_name(self):
        name = self.name
        return name
