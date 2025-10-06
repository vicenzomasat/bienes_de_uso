class Bien:
    def __init__(self, id=1, descripcion="", tipo_bien="", es_amortizable=True,
                 anos_amortizacion=5, ejercicio_alta=2024, fecha_ingreso="01/01/2024",
                 fecha_baja=None, valor_origen=0.0):
        self.id = id
        self.descripcion = descripcion
        self.tipo_bien = tipo_bien
        self.es_amortizable = es_amortizable
        self.anos_amortizacion = anos_amortizacion if es_amortizable else 0
        self.ejercicio_alta = ejercicio_alta
        self.fecha_ingreso = fecha_ingreso
        self.fecha_baja = fecha_baja
        self.valor_origen = valor_origen
        
        # Campos calculados (se llenan dinámicamente)
        self.amortizacion_data = {}
        self.inflacion_data = {}
    
    def get_fecha_origen_bien(self):
        """Retorna la fecha de origen (histórica) para cálculos de inflación"""
        return self.fecha_ingreso
    
    def get_valor_base_calculo(self):
        return self.valor_origen
    
    def get_amort_acum_inicial(self):
        return 0.0
    
    def to_dict_historico(self):
        """Datos para vista histórica"""
        return {
            'ID': self.id,
            'Descripción': self.descripcion,
            'Tipo de Bien': self.tipo_bien,
            'Años': self.anos_amortizacion,
            'Ejercicio': self.ejercicio_alta,
            'F.Ingreso': self.fecha_ingreso,
            'F.Baja': self.fecha_baja or '',
            'Valor Origen': self.valor_origen
        }
    
    def to_dict_ajustado(self):
        """Datos para vista ajustada por inflación"""
        base = {
            'ID': self.id,
            'Descripción': self.descripcion,
            'Tipo de Bien': self.tipo_bien,
            'F.Ingreso': self.fecha_ingreso,
            'Valor Origen Histórico': self.valor_origen
        }
        
        # Agregar datos de inflación si existen
        if hasattr(self, 'inflacion_data') and self.inflacion_data:
            base.update(self.inflacion_data)
        
        return base
    
    # Métodos preparados para SQLite
    def to_sql_dict(self):
        """Convierte el bien a formato para SQLite"""
        return {
            'id': self.id,
            'descripcion': self.descripcion,
            'tipo_bien': self.tipo_bien,
            'es_amortizable': 1 if self.es_amortizable else 0,
            'anos_amortizacion': self.anos_amortizacion,
            'ejercicio_alta': self.ejercicio_alta,
            'fecha_ingreso': self.fecha_ingreso,
            'fecha_baja': self.fecha_baja,
            'valor_origen': self.valor_origen
        }
    
    @classmethod
    def from_sql_dict(cls, data):
        """Crea un bien desde datos de SQLite"""
        return cls(
            id=data['id'],
            descripcion=data['descripcion'],
            tipo_bien=data['tipo_bien'],
            es_amortizable=bool(data['es_amortizable']),
            anos_amortizacion=data['anos_amortizacion'],
            ejercicio_alta=data['ejercicio_alta'],
            fecha_ingreso=data['fecha_ingreso'],
            fecha_baja=data['fecha_baja'],
            valor_origen=data['valor_origen']
        )
