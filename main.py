from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import requests
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", "https://your-vercel-domain.vercel.app"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# Groq API configuration
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = os.getenv("GROQ_MODEL")
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"

# Supabase configuration
SUPABASE_URL = os.getenv("SUPABASE_URL", "https://atokpfpcgihugqjklkao.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "sb_secret_5A9CzRVMmERprF4yXIw9Cw_XbaBIwD2")

# Example keywords for multiple blogs
keywords = ["AI in Healthcare", "AI in Education", "AI in Marketing", "AI in Finance", "AI in Real Estate"]

def generate_blog_content_with_groq(topic: str) -> str:
    """Generate blog content using Groq API"""
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": GROQ_MODEL,
        "messages": [
            {
                "role": "system",
                "content": "You are a professional blog writer. Create engaging, informative, and well-structured blog content."
            },
            {
                "role": "user",
                "content": f"Write a comprehensive blog post about {topic}. Include an introduction, main points with examples, and a conclusion. Make it around 500-800 words."
            }
        ],
        "temperature": 0.7,
        "max_tokens": 1500
    }
    
    try:
        response = requests.post(GROQ_API_URL, headers=headers, json=payload)
        response.raise_for_status()
        
        result = response.json()
        return result["choices"][0]["message"]["content"]
    except requests.exceptions.RequestException as e:
        return f"Error generating content: {str(e)}"

@app.get("/generate-blogs")
def generate_blogs():
    generated_blogs = []

    for keyword in keywords:
        # 1️⃣ AI content generation using Groq API
        blog_content = generate_blog_content_with_groq(keyword)

        # 2️⃣ Save to DB (example with Supabase REST API)
        db_url = f"{SUPABASE_URL}/rest/v1/blogs"
        headers = {
            "apikey": SUPABASE_KEY,
            "Authorization": f"Bearer {SUPABASE_KEY}",
            "Content-Type": "application/json",
            "Prefer": "return=representation"
        }
        data = {
            "title": keyword,
            "content": blog_content
        }
        r = requests.post(db_url, headers=headers, json=data)
        if r.status_code == 201:
            generated_blogs.append(keyword)

    return {"success": True, "blogs_generated": generated_blogs}

@app.get("/generate-blog/{topic}")
def generate_single_blog(topic: str):
    """Generate a single blog post for a given topic"""
    blog_content = generate_blog_content_with_groq(topic)
    
    # Save to Supabase database
    db_url = f"{SUPABASE_URL}/rest/v1/blogs"
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=representation"
    }
    data = {
        "title": topic,
        "content": blog_content
    }
    
    try:
        r = requests.post(db_url, headers=headers, json=data)
        print(f"Supabase response status: {r.status_code}")
        print(f"Supabase response: {r.text}")
        if r.status_code == 201:
            return {
                "success": True,
                "topic": topic,
                "content": blog_content,
                "model_used": GROQ_MODEL,
                "saved_to_db": True
            }
        else:
            return {
                "success": True,
                "topic": topic,
                "content": blog_content,
                "model_used": GROQ_MODEL,
                "saved_to_db": False,
                "error": f"Database error: {r.status_code} - {r.text}"
            }
    except requests.exceptions.RequestException as e:
        return {
            "success": True,
            "topic": topic,
            "content": blog_content,
            "model_used": GROQ_MODEL,
            "saved_to_db": False,
            "error": f"Database connection error: {str(e)}"
        }

@app.get("/test-supabase")
def test_supabase():
    """Test Supabase connection"""
    db_url = f"{SUPABASE_URL}/rest/v1/blogs"
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json"
    }
    
    try:
        r = requests.get(db_url, headers=headers)
        return {
            "status": r.status_code,
            "response": r.text,
            "url": db_url,
            "key_preview": SUPABASE_KEY[:20] + "..." if len(SUPABASE_KEY) > 20 else SUPABASE_KEY
        }
    except requests.exceptions.RequestException as e:
        return {
            "error": str(e),
            "url": db_url,
            "key_preview": SUPABASE_KEY[:20] + "..." if len(SUPABASE_KEY) > 20 else SUPABASE_KEY
        }

@app.get("/")
def read_root():
    return {"status": "healthy", "message": "Blog API is running"}
