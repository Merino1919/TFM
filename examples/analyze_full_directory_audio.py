# Load the .env file 
from dotenv import load_dotenv
load_dotenv()

import warnings

# Eliminate the warnings
warnings.filterwarnings("ignore", category="DeprecationWarning")

from birdnetlib.batch import DirectoryAnalyzer
from birdnetlib.analyzer import Analyzer


def on_analyze_complete(recording):
    print(f"\nArchivo: {recording.path}")
    
    if recording.detections:
        # Usamos max() con una función lambda para encontrar el de mayor 'confidence'
        mejor_deteccion = max(recording.detections, key=lambda x: x['confidence'])
        
        print("--- Detección con mayor confianza ---")
        print("Ave: ", mejor_deteccion['common_name'])
        print("Confianza: ", mejor_deteccion['confidence'])
        print("Nombre científico: ", mejor_deteccion['scientific_name'])
    else:
        print("No se encontraron detecciones.")


def on_error(recording, error):
    print("An exception occurred: {}".format(error))
    print(recording.path)


print("Starting Analyzer")
analyzer = Analyzer()


print("Starting Watcher")
directory = "C:/Users/34656/OneDrive/Escritorio/Research/TFM Test/RAG/data/audio"
batch = DirectoryAnalyzer(
    directory,
    analyzers=[analyzer],
    min_conf=0.4
)

batch.on_analyze_complete = on_analyze_complete
batch.on_error = on_error
batch.process()