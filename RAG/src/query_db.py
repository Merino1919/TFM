import chromadb

def query_database(embeddings, n_results=5):
    """
    Consulta la colección de ChromaDB y devuelve los documentos más similares a un embedding dado,
    ordenados por distancia de menor a mayor.
    """
   # Conectar al cliente persistente
    client = chromadb.PersistentClient(
        path=r"C:\Users\34656\OneDrive\Escritorio\Research\TFM\RAG\data\chromadb"
    )

    # Cargar la colección
    collection = client.get_collection("aves_ibericas")

    # Realizar la consulta
    try:
        results = collection.query(
            query_embeddings=embeddings,
            n_results=n_results
        )
    except Exception as e:
        print(f"Error durante la consulta a la base de datos: {e}")
        return []

    # Extraer datos
    distances = results["distances"][0]
    metadatas = results["metadatas"][0]
    documents = results["documents"][0]

    # Combinar y ordenar por similitud
    ordered_results = sorted(zip(distances, metadatas, documents), key=lambda x: x[0])
    return ordered_results

