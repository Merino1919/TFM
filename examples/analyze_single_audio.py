import warnings

# Eliminate the warnings
warnings.filterwarnings("ignore")

# Load the birndetlib library
from birdnetlib import Recording
from birdnetlib.analyzer import Analyzer

# Load the .env variables
from dotenv import load_dotenv
load_dotenv()

# Load and initialize the BirdNET-Analyzer models.
analyzer = Analyzer()

recording = Recording(
    analyzer,
    "C:/Users/34656/OneDrive/Escritorio/Research/TFM Test/RAG/data/audio/Abubilla_malgache.mp3",
    min_conf=0.25,
)
recording.analyze()
print(recording.detections)

'''
[{'common_name': 'Madagascar Hoopoe', 'scientific_name': 'Upupa marginata', 'start_time': 0.0, 'end_time': 3.0, 'confidence': 0.9839948415756226, 'label': 'Upupa marginata_Madagascar Hoopoe'}, 
{'common_name': 'European Turtle-Dove', 'scientific_name': 'Streptopelia turtur', 'start_time': 0.0, 'end_time': 3.0, 'confidence': 0.9675302505493164, 'label': 'Streptopelia turtur_European Turtle-Dove'}, 
{'common_name': 'African Collared-Dove', 'scientific_name': 'Streptopelia roseogrisea', 'start_time': 0.0, 'end_time': 3.0, 'confidence': 0.2994099259376526, 'label': 'Streptopelia roseogrisea_African Collared-Dove'}, 
{'common_name': 'Lineated Foliage-gleaner', 'scientific_name': 'Syndactyla subalaris', 'start_time': 3.0, 'end_time': 6.0, 'confidence': 0.4385871887207031, 'label': 'Syndactyla subalaris_Lineated Foliage-gleaner'}, 
{'common_name': 'Madagascar Hoopoe', 'scientific_name': 'Upupa marginata', 'start_time': 6.0, 'end_time': 9.0, 'confidence': 0.985684871673584, 'label': 'Upupa marginata_Madagascar Hoopoe'}, 
{'common_name': 'European Turtle-Dove', 'scientific_name': 'Streptopelia turtur', 'start_time': 6.0, 'end_time': 9.0, 'confidence': 0.375683069229126, 'label': 'Streptopelia turtur_European Turtle-Dove'}, 
{'common_name': 'Pied Crow', 'scientific_name': 'Corvus albus', 'start_time': 12.0, 'end_time': 15.0, 'confidence': 0.6039532423019409, 'label': 'Corvus albus_Pied Crow'}]
'''

