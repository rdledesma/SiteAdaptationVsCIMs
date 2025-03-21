import itertools

lats = [-23.5844, -24.7288, -22.103936]
lons = [-64.5066, -65.4095, -65.599923]
alts = [401, 1233, 3500]

lats_init = [-23.55, -24.74, -22.10]
lons_init = [-64.55, -65.45, -65.50]
sites = ['YU','SA','LQ']

# Coordenadas iniciales
#lat_init, lon_init = -24.75, -65.45
resolucion = 0.1

# Función para calcular los vecinos de orden k
def calcular_vecinos_orden_k(lat, lon, resolucion, k):
    vecinos = set()
    
    # Crear un rango de movimientos desde -k hasta k
    movimientos = range(-k, k+1)
    
    # Generar todas las combinaciones posibles de movimientos que suman exactamente k en magnitud
    for dx, dy in itertools.product(movimientos, repeat=2):
        if abs(dx) + abs(dy) == k:
            vecino_lat = lat + dx * resolucion
            vecino_lon = lon + dy * resolucion
            vecinos.add((round(vecino_lat, 5), round(vecino_lon, 5)))
    
    return vecinos








class Site():
    def __init__(self, cod):
        self.cod = cod
        idx = sites.index(cod)
        self.lat = lats[idx] 
        self.long = lons[idx] 
        self.alt = alts[idx]
        self.idx = idx

    
    
    def getNeighbors(self, order):
        # Orden k
        k = order
        lat_init = lats_init[self.idx]
        lon_init = lons_init[self.idx]
        
        # Calcular los vecinos de orden k
        vecinos_k1 = calcular_vecinos_orden_k(lat_init, lon_init, resolucion, k)
       
        
        return [f"{x[0]}_{x[1]}" for x in vecinos_k1]
    
    
    
