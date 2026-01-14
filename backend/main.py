from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
import httpx
import uuid
from pydantic import BaseModel
from typing import Optional, List
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

QDRANT_HOST = os.getenv("QDRANT_HOST", "localhost")
QDRANT_PORT = int(os.getenv("QDRANT_PORT", 6333))
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")

qdrant = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)

COLLECTION_NAME = "blogposts"
VECTOR_SIZE = 768  # nomic-embed-text dimension

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


class BlogPost(BaseModel):
    id: Optional[str] = None
    title: str
    content: str
    topic: str


class TopicRequest(BaseModel):
    topic: str


def ensure_collection():
    collections = qdrant.get_collections().collections
    if not any(c.name == COLLECTION_NAME for c in collections):
        qdrant.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(size=VECTOR_SIZE, distance=Distance.COSINE),
        )


def get_embedding(text: str) -> List[float]:
    """Get embedding from Ollama"""
    response = httpx.post(
        f"{OLLAMA_HOST}/api/embeddings",
        json={"model": "nomic-embed-text", "prompt": text},
        timeout=30.0
    )
    return response.json()["embedding"]


def is_collection_empty() -> bool:
    """Check if the collection has any points"""
    result = qdrant.scroll(
        collection_name=COLLECTION_NAME,
        limit=1,
        with_payload=False,
        with_vectors=False
    )
    return len(result[0]) == 0


def seed_database():
    """Seed the database with example posts"""
    print("Seeding database with example posts...")
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
        print(f"  Prepared: {post['title']}")

    qdrant.upsert(
        collection_name=COLLECTION_NAME,
        points=points
    )
    print(f"Successfully seeded {len(points)} blog posts!")


@app.on_event("startup")
async def startup():
    ensure_collection()
    if is_collection_empty():
        seed_database()


@app.get("/api/posts/delete/{post_id}")
async def delete_post(post_id: str):
    qdrant.delete(
        collection_name=COLLECTION_NAME,
        points_selector=[post_id]
    )
    return {"status": "deleted", "id": post_id}


@app.get("/api/posts")
async def get_all_posts():
    """Get all blog posts"""
    result = qdrant.scroll(
        collection_name=COLLECTION_NAME,
        limit=100,
        with_payload=True,
        with_vectors=False
    )
    posts = []
    for point in result[0]:
        posts.append({
            "id": point.id,
            "title": point.payload.get("title", ""),
            "content": point.payload.get("content", ""),
            "topic": point.payload.get("topic", "")
        })
    return posts


@app.get("/api/posts/{post_id}")
async def get_post(post_id: str):
    """Get a single blog post"""
    result = qdrant.retrieve(
        collection_name=COLLECTION_NAME,
        ids=[post_id],
        with_payload=True
    )
    if not result:
        return {"error": "Post not found"}
    point = result[0]
    return {
        "id": point.id,
        "title": point.payload.get("title", ""),
        "content": point.payload.get("content", ""),
        "topic": point.payload.get("topic", "")
    }


@app.post("/api/posts/update")
async def update_post(post: BlogPost):
    if not post.id:
        return {"error": "Post ID required"}

    embedding = get_embedding(f"{post.title} {post.content}")

    qdrant.upsert(
        collection_name=COLLECTION_NAME,
        points=[
            PointStruct(
                id=post.id,
                vector=embedding,
                payload={
                    "title": post.title,
                    "content": post.content,
                    "topic": post.topic
                }
            )
        ]
    )
    return {"status": "updated", "id": post.id}


@app.post("/api/posts")
async def create_post(post: BlogPost):
    """Create a new blog post"""
    post_id = str(uuid.uuid4())
    embedding = get_embedding(f"{post.title} {post.content}")

    qdrant.upsert(
        collection_name=COLLECTION_NAME,
        points=[
            PointStruct(
                id=post_id,
                vector=embedding,
                payload={
                    "title": post.title,
                    "content": post.content,
                    "topic": post.topic
                }
            )
        ]
    )
    return {"status": "created", "id": post_id}


@app.get("/api/posts/search/{query}")
async def search_posts(query: str):
    """Search blog posts by text"""
    embedding = get_embedding(query)

    results = qdrant.query_points(
        collection_name=COLLECTION_NAME,
        query=embedding,
        limit=10
    )

    posts = []
    for point in results.points:
        posts.append({
            "id": point.id,
            "title": point.payload.get("title", ""),
            "content": point.payload.get("content", ""),
            "topic": point.payload.get("topic", ""),
            "score": point.score
        })
    return posts


@app.post("/api/generate")
async def generate_post(request: TopicRequest):
    topic = request.topic

    prompt = f"""Write a blog post about {topic}.
    The post should have a title and content.
    Make it engaging and informative.
    Format: put the title on the first line, then the content after a blank line."""

    response = httpx.post(
        f"{OLLAMA_HOST}/api/generate",
        json={
            "model": "llama3.2",
            "prompt": prompt,
            "stream": False
        },
        timeout=120.0
    )

    result = response.json()
    generated_text = result.get("response", "")

    lines = generated_text.strip().split("\n")
    title = lines[0].replace("#", "").strip() if lines else "Untitled"
    content = "\n".join(lines[2:]) if len(lines) > 2 else generated_text

    return {
        "title": title,
        "content": content,
        "topic": topic
    }


@app.get("/api/health")
async def health():
    return {"status": "ok"}
