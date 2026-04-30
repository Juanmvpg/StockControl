"""
importador.py – Lógica para la importación avanzada mediante coordenadas
"""

import pathlib

def _col_letter_to_index(letter):
    """Convierte una letra de columna de Excel (ej. 'A', 'Z', 'AA') a índice entero base 0."""
    letter = str(letter).strip().upper()
    if not letter.isalpha():
        raise ValueError(f"Columna inválida: {letter}")
    idx = 0
    for char in letter:
        idx = idx * 26 + (ord(char) - ord('A')) + 1
    return idx - 1


def leer_datos(filepath, mapeo):
    import pandas as pd
    """
    Lee datos del archivo usando coordenadas absolutas personalizadas por cada campo.
    
    mapeo = {
      'nombre': {'col': 'B', 'inicio': 7, 'fin': None},
      'precio': {'col': 'D', 'inicio': 7, 'fin': 150},
      ...
    }
    """
    ext = pathlib.Path(filepath).suffix.lower()
    
    # Validaciones básicas de los mapeos
    if 'nombre' not in mapeo or not mapeo['nombre'].get('col'):
        raise ValueError("El campo 'Nombre' debe tener una columna asignada.")
        
    for campo, config in mapeo.items():
        if config.get('col'):
            # Convertir la letra de la columna a índice numérico base 0
            config['col_idx'] = _col_letter_to_index(config['col'])
            
            # Normalizar filas 
            try: config['inicio'] = int(config.get('inicio') or 1)
            except: config['inicio'] = 1
            
            try: config['fin'] = int(config.get('fin')) if config.get('fin') else None
            except: config['fin'] = None
    
    # Buscar cuál es la columna máxima que necesitamos cargar
    columnas_utilizadas = [c['col_idx'] for c in mapeo.values() if 'col_idx' in c]
    if not columnas_utilizadas:
        raise ValueError("No se configuró ninguna columna para importar.")
    
    col_max = max(columnas_utilizadas)
    cols_a_cargar = list(range(col_max + 1))
    
    try:
        # Cargamos el archivo completo como texto, sin asumir encabezados (header=None)
        if ext == '.csv':
            # Limitamos a usecols para ahorrar memoria
            df = pd.read_csv(filepath, header=None, usecols=cols_a_cargar, dtype=str)
        elif ext in ['.xlsx', '.xls']:
            df = pd.read_excel(filepath, header=None, usecols=cols_a_cargar, dtype=str)
        else:
            raise ValueError("Formato no soportado.")
            
        df = df.fillna("")
        
        # Encontrar cuál es la fila de inicio global más baja (para no procesar innecesariamente desde arriba)
        fila_min = min([c['inicio'] for c in mapeo.values() if 'col_idx' in c])
        
        # Iterar el dataset
        resultados = []
        
        for idx_row, row in df.iterrows():
            fila_real_excel = idx_row + 1 # el iterrows es 0-indexed
            
            if fila_real_excel < fila_min:
                continue # Aún no llegamos a la primera fila útil configurada
                
            item = {}
            valido_para_al_menos_uno = False
            
            for campo, config in mapeo.items():
                if 'col_idx' not in config:
                    continue
                    
                # Verificar rango de filas para este campo específico
                if fila_real_excel < config['inicio']:
                    item[campo] = ""
                    continue
                if config['fin'] and fila_real_excel > config['fin']:
                    item[campo] = ""
                    continue
                
                # Extraer el valor
                try: val = str(row.iloc[config['col_idx']]).strip()
                except: val = ""
                
                # Coversiones según el campo del sistema
                if campo in ('stock', 'minimo'):
                    try: item[campo] = int(val.replace(',', ''))
                    except: item[campo] = 0
                elif campo == 'precio':
                    try: 
                        item[campo] = float(val.replace('$', '').replace(',', ''))
                    except: 
                        item[campo] = 0.0
                else:
                    item[campo] = val
                    
                if val:
                    valido_para_al_menos_uno = True
                    
            # Solo si en esta fila pudimos leer algo (evita agregar dicts vacíos)
            # Y verificando que el Nombre no quede en blanco
            if valido_para_al_menos_uno and item.get("nombre"):
                resultados.append(item)
                
        return resultados
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise RuntimeError(f"Error procesando el archivo:\n{str(e)}")
