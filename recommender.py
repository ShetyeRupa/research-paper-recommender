"""
Research Paper Recommender - Core AI Engine
Uses Sentence-BERT embeddings for semantic similarity search
"""
import numpy as np
from typing import List, Dict, Optional
from sentence_transformers import SentenceTransformer
import faiss
import pickle
import os

class PaperRecommender:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """
        Initialize recommender with Sentence-BERT model
        
        Model: all-MiniLM-L6-v2
        - 384-dimensional embeddings
        - Fast inference (0.5s per 100 papers)
        - No GPU required
        - Good balance of speed and accuracy
        """
        print(f"Loading embedding model: {model_name}")
        self.model = SentenceTransformer(model_name)
        self.embedding_dim = 384  # Dimension for all-MiniLM-L6-v2
        self.papers = []  # Store paper metadata
        self.index = None  # FAISS index for fast similarity search
        self.embeddings_cache = []  # Store embeddings
        
    def add_papers(self, papers: List[Dict]) -> int:
        """
        Add papers to the index
        
        Args:
            papers: List of paper dicts with 'text' or 'abstract' field
        
        Returns:
            Number of papers added
        """
        for paper in papers:
            # Use abstract if available, otherwise use full text
            text_to_embed = paper.get("abstract", paper.get("full_text", paper.get("text", "")))
            
            if text_to_embed and len(text_to_embed) > 50:
                # Generate embedding
                embedding = self.model.encode(text_to_embed[:1000])  # Limit to 1000 chars for speed
                self.embeddings_cache.append(embedding)
                self.papers.append({
                    "id": len(self.papers),
                    "title": paper.get("title", "Untitled"),
                    "authors": paper.get("authors", "Unknown"),
                    "year": paper.get("year", ""),
                    "abstract": text_to_embed[:500],
                    "file_name": paper.get("file_name", ""),
                    "full_text": paper.get("full_text", "")[:2000]
                })
        
        # Rebuild FAISS index
        self._build_index()
        
        return len(papers)
    
    def _build_index(self):
        """Build FAISS index for fast similarity search"""
        if not self.embeddings_cache:
            self.index = None
            return
        
        embeddings_array = np.array(self.embeddings_cache).astype('float32')
        
        # Normalize for cosine similarity (FAISS inner product = cosine after L2 normalization)
        faiss.normalize_L2(embeddings_array)
        
        # Create index
        self.index = faiss.IndexFlatIP(self.embedding_dim)  # Inner Product (cosine after norm)
        self.index.add(embeddings_array)
        
        print(f"Index built with {self.index.ntotal} papers")
    
    def recommend(self, query_text: str, top_k: int = 5, min_score: float = 0.3) -> List[Dict]:
        """
        Recommend papers based on query text
        
        Args:
            query_text: The user's writing (current section they are working on)
            top_k: Number of recommendations to return
            min_score: Minimum similarity score (0-1) to include
        
        Returns:
            List of recommended papers with similarity scores
        """
        if not self.index or len(self.papers) == 0:
            return []
        
        # Encode query
        query_embedding = self.model.encode(query_text[:1000]).astype('float32').reshape(1, -1)
        
        # Normalize query
        faiss.normalize_L2(query_embedding)
        
        # Search
        scores, indices = self.index.search(query_embedding, min(top_k * 2, len(self.papers)))
        
        # Format results
        recommendations = []
        for score, idx in zip(scores[0], indices[0]):
            if idx >= 0 and idx < len(self.papers) and score >= min_score:
                paper = self.papers[idx].copy()
                paper["similarity_score"] = round(float(score), 3)
                paper["relevance"] = self._get_relevance_label(score)
                recommendations.append(paper)
                
                if len(recommendations) >= top_k:
                    break
        
        return recommendations
    
    def _get_relevance_label(self, score: float) -> str:
        """Convert similarity score to human-readable label"""
        if score >= 0.7:
            return "Highly Relevant"
        elif score >= 0.5:
            return "Relevant"
        elif score >= 0.3:
            return "Somewhat Relevant"
        else:
            return "Low Relevance"
    
    def save_index(self, path: str):
        """Save index and papers to disk"""
        if self.index:
            faiss.write_index(self.index, f"{path}.index")
        with open(f"{path}.pkl", 'wb') as f:
            pickle.dump({
                'papers': self.papers,
                'embeddings_cache': self.embeddings_cache
            }, f)
    
    def load_index(self, path: str):
        """Load index and papers from disk"""
        if os.path.exists(f"{path}.index"):
            self.index = faiss.read_index(f"{path}.index")
        if os.path.exists(f"{path}.pkl"):
            with open(f"{path}.pkl", 'rb') as f:
                data = pickle.load(f)
                self.papers = data['papers']
                self.embeddings_cache = data['embeddings_cache']
    
    def clear(self):
        """Clear all papers and index"""
        self.papers = []
        self.embeddings_cache = []
        self.index = None


# Example: Create a sample paper library for demonstration
def create_sample_papers() -> List[Dict]:
    """Create sample research papers for testing the recommender"""
    return [
        {
            "title": "Modeling and Analyzing Taxi Congestion Premium in Congested Cities",
            "authors": "Yuan et al.",
            "year": "2017",
            "abstract": "Traffic congestion is a significant problem in many major cities. Getting stuck in traffic, the mileage per unit time that a taxicab travels will decline significantly. Congestion premium has become an increasingly important income source for taxi drivers. This paper develops a taxi price equilibrium model to investigate the adjustment mechanism of congestion premium on optimizing the taxi driver's income and balancing supply and demand.",
            "file_name": "taxi_congestion_premium.pdf"
        },
        {
            "title": "Extracting Commuter-Specific Destination Hotspots from Trip Destination Data",
            "authors": "Keler et al.",
            "year": "2020",
            "abstract": "Taxi trajectories from urban environments allow inferring various information about transport service qualities and commuter dynamics. This paper compares destination hotspots of boro taxi and Citi Bike users in NYC. The authors introduce a spatiotemporal assigning procedure for areas of influence around static bike sharing stations.",
            "file_name": "commuter_hotspots.pdf"
        },
        {
            "title": "Seeking in Ride-on-Demand Service: A Reinforcement Learning Model with Dynamic Price Prediction",
            "authors": "Guo et al.",
            "year": "2024",
            "abstract": "This paper focuses on the seeking route recommendation problem that aims at increasing driver revenue by recommending profitable seeking routes to drivers of vacant cars with the help of dynamic prices. The authors design a dynamic price prediction model and adopt a reinforcement learning model for route recommendation.",
            "file_name": "ride_on_demand_rl.pdf"
        },
        {
            "title": "Big Data Trip Classification on NYC Taxi and Uber Sensor Network",
            "authors": "Sun et al.",
            "year": "2018",
            "abstract": "This paper uses big data technologies to analyze taxi and Uber trips in New York City. The authors classify regions into three categories based on which service dominates: Yellow taxi, Green taxi, or Uber. Logistic regression achieves over 85% accuracy.",
            "file_name": "big_data_trip_classification.pdf"
        },
        {
            "title": "Changing Demand for New York Yellow Cabs During the COVID-19 Pandemic",
            "authors": "Manley et al.",
            "year": "2021",
            "abstract": "This paper explores the changed spatiotemporal nature of mobility demand during COVID-19. Through comparative analysis of NYC taxi records, the authors observe how relative demand for taxis displaced across land use zones and concentrated during daylight hours.",
            "file_name": "covid_taxi_demand.pdf"
        },
        {
            "title": "Forecasting NYC Yellow Taxi Ridership Decline: A Time Series Analysis",
            "authors": "Singh",
            "year": "2022",
            "abstract": "This study analyzes and forecasts daily passenger counts for NYC yellow taxis during 2017-2019. Using ARIMA models, the analysis reveals strong seasonal patterns with a consistent linear decline of approximately 200 passengers per day.",
            "file_name": "taxi_ridership_forecast.pdf"
        },
        {
            "title": "Effects of Congestion Surcharges: From Ridership to Competition and Safety",
            "authors": "Weber et al.",
            "year": "2023",
            "abstract": "This paper examines the effects of a 2019 congestion surcharge on for-hire-vehicle and taxi usage in NYC. Using difference-in-differences method, the authors find a significant decline in rides originating from the charged area (11%) and a parallel reduction in collisions (5%) and injuries (9%).",
            "file_name": "congestion_surcharges.pdf"
        }
    ]
    return sample_papers