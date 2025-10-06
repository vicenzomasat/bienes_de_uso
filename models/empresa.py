class EmpresaData:
    def __init__(self):
        self.razon_social = ''
        self.cuit = ''
        self.fecha_inicio = ''
        self.fecha_cierre = ''
        self.ejercicio_liquidacion = ''
        self.ejercicio_anterior = ''
        self.configurada = False
    
    def to_dict(self):
        return {
            'razon_social': self.razon_social,
            'cuit': self.cuit,
            'fecha_inicio': self.fecha_inicio,
            'fecha_cierre': self.fecha_cierre,
            'ejercicio_liquidacion': self.ejercicio_liquidacion,
            'ejercicio_anterior': self.ejercicio_anterior
        }
    
    # Métodos preparados para SQLite
    def to_sql_dict(self):
        return {
            'razon_social': self.razon_social,
            'cuit': self.cuit,
            'fecha_inicio': self.fecha_inicio,
            'fecha_cierre': self.fecha_cierre,
            'ejercicio_liquidacion': self.ejercicio_liquidacion,
            'ejercicio_anterior': self.ejercicio_anterior,
            'configurada': 1 if self.configurada else 0
        }
    
    @classmethod
    def from_sql_dict(cls, data):
        empresa = cls()
        empresa.razon_social = data['razon_social']
        empresa.cuit = data['cuit']
        empresa.fecha_inicio = data['fecha_inicio']
        empresa.fecha_cierre = data['fecha_cierre']
        empresa.ejercicio_liquidacion = data['ejercicio_liquidacion']
        empresa.ejercicio_anterior = data['ejercicio_anterior']
        empresa.configurada = bool(data['configurada'])
        return empresa
