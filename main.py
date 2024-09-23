import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
# Limpieza del dataset de valores nulos o vacios

#df = pd.read_csv('data.csv')

#df_clean = df.dropna()

#df_clean.to_csv('data_clean.csv', index=False)

#print(f"Filas antes de la limpieza: {len(df)}")
#print(f"Filas después de la limpieza: {len(df_clean)}")

# Aca se muestra el grafo

#df_clean = pd.read_csv('data_clean.csv')

#df_limited = df_clean.head(1500)

# Crear el grafo
#G = nx.Graph()

#for index, row in df_limited.iterrows():
#    song = row['Song']
#    G.add_node(song)  # Añadir nodo con el nombre de la canción

#plt.figure(figsize=(12, 12))
#pos = nx.spring_layout(G, k=0.15, iterations=20)  # Ajustar el layout para una mejor visualización
#nx.draw(G, pos, with_labels=True, node_size=1000, node_color="skyblue", font_size=8, font_color="black", font_weight='bold')
#plt.title("Nodos de canciones (sin conexiones)")
#plt.show()
