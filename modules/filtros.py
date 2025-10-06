from utils.validators import Validators

class FiltroEjercicio:
    def __init__(self):
        pass
    
    def filtrar_bienes_por_ejercicio(self, bienes, ejercicio_liquidacion):
        if not ejercicio_liquidacion or not Validators.validar_fecha(ejercicio_liquidacion):
            return list(bienes)
        
        año_liquidacion = Validators.extraer_año_ejercicio(ejercicio_liquidacion)
        if not año_liquidacion:
            return list(bienes)
        
        bienes_filtrados = []
        for bien in bienes:
            if bien.ejercicio_alta <= año_liquidacion:
                bienes_filtrados.append(bien)

        return bienes_filtrados
