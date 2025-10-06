from datetime import datetime
from utils.validators import Validators

class InflacionCalculator:
    def __init__(self, gestor_indices):
        self.gestor_indices = gestor_indices
    
    def calcular_ajuste_inflacion(self, bien, ejercicio_actual, ejercicio_anterior, amortizacion_data):
        """
        Calcula el ajuste por inflación para un bien específico
        
        Args:
            bien: Objeto Bien
            ejercicio_actual: String DD/MM/AAAA
            ejercicio_anterior: String DD/MM/AAAA  
            amortizacion_data: Dict con datos de amortización histórica
            
        Returns:
            dict con valores ajustados por inflación
        """
        if not bien.es_amortizable:
            return self._crear_resultado_no_amortizable(bien)
        
        fecha_origen = bien.get_fecha_origen_bien()
        
        # Calcular coeficientes
        coef_actual, error_actual = self.gestor_indices.get_coeficiente(fecha_origen, ejercicio_actual)
        coef_anterior, error_anterior = self.gestor_indices.get_coeficiente(fecha_origen, ejercicio_anterior)
        
        # Verificar errores de índices faltantes
        errores = []
        if error_actual:
            errores.append(error_actual)
        if error_anterior:
            errores.append(error_anterior)
        
        if errores:
            return {
                'error': True,
                'mensaje': "; ".join(errores),
                'fechas_faltantes': self._extraer_fechas_de_errores(errores),
                'link_facpce': 'https://www.facpce.org.ar/indices-facpce/'
            }
        
        # Verificar si el bien se adquirió en el ejercicio actual
        bien_adquirido_ejercicio_actual = self._bien_adquirido_en_ejercicio(fecha_origen, ejercicio_anterior)
        
        # Calcular valores ajustados
        resultado = self._calcular_valores_ajustados(
            bien, coef_actual, coef_anterior, 
            amortizacion_data, bien_adquirido_ejercicio_actual
        )
        
        return resultado
    
    def _crear_resultado_no_amortizable(self, bien):
        """Resultado para bienes no amortizables"""
        return {
            'error': False,
            'valor_origen_historico': bien.valor_origen,
            'vo_ajustado_anterior': 0.0,
            'vo_ajustado_actual': bien.valor_origen,
            'ajuste_infl_vo_ejercicio': bien.valor_origen,
            'amort_acum_inicio_ajustada_anterior': 0.0,
            'amort_acum_inicio_ajustada_actual': 0.0,
            'ajuste_infl_amort_inicio_ejercicio': 0.0,
            'amort_ejercicio_ajustada': 0.0,
            'amort_acum_cierre_ajustada': 0.0,
            'valor_residual_ajustado': bien.valor_origen
        }
    
    def _bien_adquirido_en_ejercicio(self, fecha_origen, ejercicio_anterior):
        """Verifica si el bien se adquirió en el ejercicio actual"""
        try:
            fecha_origen_obj = datetime.strptime(fecha_origen, '%d/%m/%Y')
            ejercicio_anterior_obj = datetime.strptime(ejercicio_anterior, '%d/%m/%Y')
            return fecha_origen_obj > ejercicio_anterior_obj
        except ValueError:
            return False
    
    def _calcular_valores_ajustados(self, bien, coef_actual, coef_anterior, amortizacion_data, bien_nuevo):
        """Calcula todos los valores ajustados por inflación"""
        
        valor_origen_historico = bien.valor_origen
        
        # Valor de Origen Ajustado
        if bien_nuevo:
            vo_ajustado_anterior = 0.0
        else:
            vo_ajustado_anterior = valor_origen_historico * coef_anterior
        
        vo_ajustado_actual = valor_origen_historico * coef_actual
        ajuste_infl_vo_ejercicio = vo_ajustado_actual - vo_ajustado_anterior
        
        # Amortización Acumulada Inicio Ajustada
        amort_inicio_historica = amortizacion_data.get('amort_inicio', 0.0)
        
        if bien_nuevo:
            amort_acum_inicio_ajustada_anterior = 0.0
        else:
            amort_acum_inicio_ajustada_anterior = amort_inicio_historica * coef_anterior
        
        amort_acum_inicio_ajustada_actual = amort_inicio_historica * coef_actual
        
        # IMPORTANTE: Verificar que la amortización inicial no exceda el valor ajustado
        amort_acum_inicio_ajustada_anterior = min(amort_acum_inicio_ajustada_anterior, vo_ajustado_anterior)
        amort_acum_inicio_ajustada_actual = min(amort_acum_inicio_ajustada_actual, vo_ajustado_actual)
        
        ajuste_infl_amort_inicio_ejercicio = (amort_acum_inicio_ajustada_actual - 
                                            amort_acum_inicio_ajustada_anterior)
        
        # Amortización del Ejercicio Ajustada
        amort_ejercicio_historica = amortizacion_data.get('amort_ejercicio', 0.0)
        
        # Verificar si el bien ya está totalmente amortizado al inicio del ejercicio
        if amort_acum_inicio_ajustada_actual >= vo_ajustado_actual:
            # Bien totalmente amortizado, no hay amortización del ejercicio
            amort_ejercicio_ajustada = 0.0
        else:
            # Calcular amortización del ejercicio ajustada
            amort_ejercicio_ajustada = amort_ejercicio_historica * coef_actual
            
            # Asegurar que la amortización del ejercicio no exceda el valor residual disponible
            valor_residual_disponible = vo_ajustado_actual - amort_acum_inicio_ajustada_actual
            amort_ejercicio_ajustada = min(amort_ejercicio_ajustada, valor_residual_disponible)
        
        # Amortización Acumulada Cierre Ajustada
        amort_acum_cierre_ajustada = amort_acum_inicio_ajustada_actual + amort_ejercicio_ajustada
        
        # IMPORTANTE: Asegurar que nunca exceda el valor ajustado del bien
        amort_acum_cierre_ajustada = min(amort_acum_cierre_ajustada, vo_ajustado_actual)
        
        # Valor Residual Ajustado
        valor_residual_ajustado = vo_ajustado_actual - amort_acum_cierre_ajustada
        
        # Asegurar que el valor residual nunca sea negativo
        valor_residual_ajustado = max(0.0, valor_residual_ajustado)
        
        return {
            'error': False,
            'valor_origen_historico': round(valor_origen_historico, 2),
            'vo_ajustado_anterior': round(vo_ajustado_anterior, 2),
            'vo_ajustado_actual': round(vo_ajustado_actual, 2),
            'ajuste_infl_vo_ejercicio': round(ajuste_infl_vo_ejercicio, 2),
            'amort_acum_inicio_ajustada_anterior': round(amort_acum_inicio_ajustada_anterior, 2),
            'amort_acum_inicio_ajustada_actual': round(amort_acum_inicio_ajustada_actual, 2),
            'ajuste_infl_amort_inicio_ejercicio': round(ajuste_infl_amort_inicio_ejercicio, 2),
            'amort_ejercicio_ajustada': round(amort_ejercicio_ajustada, 2),
            'amort_acum_cierre_ajustada': round(amort_acum_cierre_ajustada, 2),
            'valor_residual_ajustado': round(valor_residual_ajustado, 2),
            'coef_actual': round(coef_actual, 6),
            'coef_anterior': round(coef_anterior, 6)
        }
    
    def _extraer_fechas_de_errores(self, errores):
        """Extrae fechas faltantes de mensajes de error"""
        fechas = []
        for error in errores:
            if "Falta índice para" in error:
                fecha = error.split("para ")[-1]
                fechas.append(fecha)
        return fechas
    
    def calcular_inflacion_lote(self, bienes, ejercicio_actual, ejercicio_anterior, amortizaciones_data):
        """Calcula inflación para una lista de bienes"""
        resultados = {}
        
        for bien in bienes:
            amort_data = amortizaciones_data.get(bien.id, {})
            resultados[bien.id] = self.calcular_ajuste_inflacion(
                bien, ejercicio_actual, ejercicio_anterior, amort_data
            )
        
        return resultados