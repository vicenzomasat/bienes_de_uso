from datetime import datetime
from utils.validators import Validators

class AmortizacionCalculator:
    def __init__(self):
        pass
    
    def calcular_amortizacion(self, bien, ejercicio_liquidacion):
        """Calcula la amortización de un bien para un ejercicio específico"""
        if not bien.es_amortizable or bien.anos_amortizacion == 0:
            return {
                'amort_inicio': 0.0,
                'amort_ejercicio': 0.0,
                'amort_acumulada': 0.0,
                'valor_residual': bien.get_valor_base_calculo()
            }
        
        año_liquidacion = Validators.extraer_año_ejercicio(ejercicio_liquidacion)
        if not año_liquidacion:
            raise ValueError("Fecha de ejercicio inválida")
        
        return self._calcular_desde_origen(bien, ejercicio_liquidacion, año_liquidacion)

    def _calcular_desde_origen(self, bien, ejercicio_liquidacion, año_liquidacion):
        amort_anual = bien.valor_origen / bien.anos_amortizacion
        años_hasta_inicio = año_liquidacion - bien.ejercicio_alta
        
        if años_hasta_inicio <= 0:
            amort_inicio = 0.0
        else:
            años_amortizados = min(años_hasta_inicio, bien.anos_amortizacion)
            amort_inicio = amort_anual * años_amortizados
        
        años_transcurridos_total = (año_liquidacion - bien.ejercicio_alta) + 1
        
        if años_transcurridos_total <= 0:
            amort_ejercicio = 0.0
        elif años_transcurridos_total > bien.anos_amortizacion:
            amort_ejercicio = 0.0
        else:
            if bien.fecha_baja:
                try:
                    fecha_baja_obj = datetime.strptime(bien.fecha_baja, '%d/%m/%Y')
                    if fecha_baja_obj.year < año_liquidacion:
                        amort_ejercicio = 0.0
                    else:
                        amort_ejercicio = amort_anual
                except ValueError:
                    amort_ejercicio = amort_anual
            else:
                amort_ejercicio = amort_anual
        
        amort_acumulada = amort_inicio + amort_ejercicio
        amort_acumulada = min(amort_acumulada, bien.valor_origen)
        valor_residual = bien.valor_origen - amort_acumulada
        
        return {
            'amort_inicio': round(amort_inicio, 2),
            'amort_ejercicio': round(amort_ejercicio, 2),
            'amort_acumulada': round(amort_acumulada, 2),
            'valor_residual': round(valor_residual, 2)
        }
    
    def calcular_amortizaciones_lote(self, bienes, ejercicio_liquidacion):
        """Calcula amortizaciones para una lista de bienes"""
        resultados = {}
        for bien in bienes:
            try:
                resultados[bien.id] = self.calcular_amortizacion(bien, ejercicio_liquidacion)
            except Exception as e:
                resultados[bien.id] = {
                    'amort_inicio': 0.0,
                    'amort_ejercicio': 0.0,
                    'amort_acumulada': 0.0,
                    'valor_residual': bien.get_valor_base_calculo(),
                    'error': str(e)
                }
        return resultados
