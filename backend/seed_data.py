"""Seed script to add 10 example blog posts to the database"""
import httpx
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
import uuid
import os

QDRANT_HOST = os.getenv("QDRANT_HOST", "localhost")
QDRANT_PORT = int(os.getenv("QDRANT_PORT", 6333))
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")

COLLECTION_NAME = "blogposts"
VECTOR_SIZE = 768

EXAMPLE_POSTS = [
    {
        "title": "Getting Started with Python",
        "content": "Python is a versatile programming language that's perfect for beginners. It has a clean syntax and a vast ecosystem of libraries. In this post, we'll explore the basics of Python programming and why it's become one of the most popular languages in the world. Python's readability makes it an excellent choice for those just starting their coding journey.",
        "topic": "programming"
    },
    {
        "title": "The Future of AI in Healthcare",
        "content": "Artificial intelligence is revolutionizing healthcare in unprecedented ways. From diagnostic imaging to drug discovery, AI is helping doctors make better decisions faster. Machine learning algorithms can now detect diseases earlier than ever before, potentially saving millions of lives. The integration of AI in healthcare promises a future where personalized medicine becomes the norm.",
        "topic": "technology"
    },
    {
        "title": "10 Tips for Remote Work Productivity",
        "content": "Working from home has become the new normal for many professionals. To stay productive, establish a dedicated workspace, maintain regular hours, and take scheduled breaks. Communication with your team is crucial - use video calls to stay connected. Remember to separate work and personal life to avoid burnout.",
        "topic": "productivity"
    },
    {
        "title": "Understanding Blockchain Technology",
        "content": "Blockchain is more than just cryptocurrency. It's a distributed ledger technology that ensures transparency and security in transactions. Each block contains a cryptographic hash of the previous block, creating an immutable chain. This technology has applications in supply chain, voting systems, and digital identity verification.",
        "topic": "technology"
    },
    {
        "title": "Healthy Eating on a Budget",
        "content": "Eating healthy doesn't have to break the bank. Plan your meals ahead, buy seasonal produce, and cook at home more often. Batch cooking on weekends can save both time and money. Focus on whole grains, legumes, and vegetables which are nutritious and affordable. Your health is an investment worth making.",
        "topic": "lifestyle"
    },
    {
        "title": "Introduction to Machine Learning",
        "content": "Machine learning is a subset of AI that enables computers to learn from data without being explicitly programmed. There are three main types: supervised learning, unsupervised learning, and reinforcement learning. Common applications include recommendation systems, image recognition, and natural language processing. Start your ML journey with Python and scikit-learn.",
        "topic": "technology"
    },
    {
        "title": "The Art of Effective Communication",
        "content": "Good communication is essential in both personal and professional life. Listen actively, be clear and concise, and consider your audience. Non-verbal cues matter just as much as words. Practice empathy and try to understand different perspectives. Strong communication skills can open doors to new opportunities.",
        "topic": "personal development"
    },
    {
        "title": "Sustainable Living Tips",
        "content": "Small changes can make a big difference for our planet. Reduce single-use plastics, conserve water, and choose public transport when possible. Support local and sustainable businesses. Start composting and growing your own herbs. Every action counts in the fight against climate change.",
        "topic": "environment"
    },
    {
        "title": "Building REST APIs with FastAPI",
        "content": "FastAPI is a modern Python web framework for building APIs. It's fast, easy to use, and provides automatic documentation. Type hints enable data validation and better IDE support. Async support makes it perfect for high-performance applications. Get started by installing FastAPI and uvicorn, then define your endpoints.",
        "topic": "programming"
    },
    {
        "title": "The Psychology of Habits",
        "content": "Habits shape our daily lives more than we realize. The habit loop consists of cue, routine, and reward. To build good habits, start small and be consistent. Attach new habits to existing ones using habit stacking. Breaking bad habits requires identifying triggers and replacing the routine with healthier alternatives.",
        "topic": "personal development"
    }
]


def get_embedding(text: str):
    """Get embedding from Ollama"""
    response = httpx.post(
        f"{OLLAMA_HOST}/api/embeddings",
        json={"model": "nomic-embed-text", "prompt": text},
        timeout=30.0
    )
    return response.json()["embedding"]


def seed_database():
    qdrant = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)

    # Ensure collection exists
    collections = qdrant.get_collections().collections
    if not any(c.name == COLLECTION_NAME for c in collections):
        qdrant.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(size=VECTOR_SIZE, distance=Distance.COSINE),
        )

    points = []
    for post in EXAMPLE_POSTS:
        post_id = str(uuid.uuid4())
        embedding = get_embedding(f"{post['title']} {post['content']}")
        points.append(
            PointStruct(
                id=post_id,
                vector=embedding,
                payload={
                    "title": post["title"],
                    "content": post["content"],
                    "topic": post["topic"]
                }
            )
        )
        print(f"Prepared: {post['title']}")

    qdrant.upsert(
        collection_name=COLLECTION_NAME,
        points=points
    )
    print(f"\nSuccessfully seeded {len(points)} blog posts!")


if __name__ == "__main__":
    seed_database()
