import os
import json
import pdfplumber
from docx import Document
import requests
from bs4 import BeautifulSoup
from google import genai
from google.genai.types import Content, Part
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from datetime import datetime
import re

# ----------------------------
# Gemini API Configuration
# ----------------------------
GEMINI_API_KEY = "AIzaSyAuSprjUEoavVr38OacNUw4gMG-qOif2_Q"
client = genai.Client(api_key=GEMINI_API_KEY)

# ----------------------------
# File Paths
# ----------------------------
QA_PAIRS_FILE = "Al_qa_pairs.json"
HISTORY_FILE = "Al_chat_history.json"


# ----------------------------
# Time-Based Greeting
# ----------------------------
def get_time_based_greeting():
    """Return greeting based on current time"""
    hour = datetime.now().hour

    if 5 <= hour < 12:
        return "Good morning! ☀️"
    elif 12 <= hour < 17:
        return "Good afternoon! 🌤️"
    elif 17 <= hour < 21:
        return "Good evening! 🌆"
    else:
        return "Good night! 🌙"


# ----------------------------
# Text Extraction Functions
# ----------------------------
def extract_text_from_pdf(pdf_path):
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text

# ----------------------------
# Smart Text Chunking
# ----------------------------
def chunk_text_intelligently(text, chunk_size=10000, overlap=500):
    """
    Split text into overlapping chunks intelligently
    - Prefers splitting at paragraph boundaries
    - Maintains context with overlap
    - Handles very large documents
    """
    # Clean text
    text = re.sub(r'\n{3,}', '\n\n', text)  # Remove excessive newlines

    # Split into paragraphs
    paragraphs = text.split('\n\n')

    chunks = []
    current_chunk = ""

    for para in paragraphs:
        para = para.strip()
        if not para:
            continue

        # If adding this paragraph exceeds chunk size
        if len(current_chunk) + len(para) > chunk_size and current_chunk:
            chunks.append(current_chunk.strip())

            # Start new chunk with overlap (last few sentences)
            sentences = current_chunk.split('. ')
            overlap_text = '. '.join(sentences[-3:]) if len(sentences) >= 3 else current_chunk[-overlap:]
            current_chunk = overlap_text + "\n\n" + para
        else:
            current_chunk += "\n\n" + para if current_chunk else para

    # Add final chunk
    if current_chunk.strip():
        chunks.append(current_chunk.strip())

    return chunks


# ----------------------------
# Auto-Calculate QA Count
# ----------------------------
def calculate_optimal_qa_count(text):
    """
    Automatically calculate optimal number of Q&A pairs based on text size
    Rules:
    - 1 Q&A pair per ~300 words (increased from 500 for better coverage)
    - Minimum 10 pairs
    - Maximum 150 pairs (increased for large documents)
    """
    word_count = len(text.split())
    char_count = len(text)

    # Calculate based on word count (1 pair per 300 words)
    optimal_count = max(10, min(150, word_count // 300))

    print(f"\n📊 Document Analysis:")
    print(f"   Characters: {char_count:,}")
    print(f"   Words: {word_count:,}")
    print(f"   Optimal Q&A pairs: {optimal_count}")

    return optimal_count


# ----------------------------
# QA Pair Generation with Gemini (Chunked)
# ----------------------------
def generate_qa_pairs_from_chunks(chunks, total_pairs):
    """Generate Q&A pairs from multiple chunks"""
    print(f"\n🤖 Processing {len(chunks)} chunks...")

    all_qa_pairs = []
    pairs_per_chunk = max(5, total_pairs // len(chunks))

    for idx, chunk in enumerate(chunks, 1):
        print(f"\n📄 Processing Chunk {idx}/{len(chunks)}...")

        # Adjust pairs for last chunk to meet total
        if idx == len(chunks):
            remaining = total_pairs - len(all_qa_pairs)
            pairs_per_chunk = max(remaining, 5)

        prompt = f"""
You are an expert at creating question-answer pairs from documents.

From the following text, generate {pairs_per_chunk} diverse question-answer pairs that cover the main topics and details.

Requirements:
1. Create questions that are specific and answerable from the text
2. Include both simple and complex questions
3. Cover different aspects of the content
4. Answers should be informative but concise (2-4 sentences)
5. Format as JSON array: [{{"question": "...", "answer": "..."}}, ...]

Text:
{chunk}

Generate the Q&A pairs in JSON format:
"""

        try:
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt
            )

            response_text = response.text.strip()

            # Extract JSON from markdown code blocks if present
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0].strip()

            qa_pairs = json.loads(response_text)
            all_qa_pairs.extend(qa_pairs)
            print(f"   ✅ Generated {len(qa_pairs)} pairs from this chunk")

        except Exception as e:
            print(f"   ⚠️ Error in chunk {idx}: {e}")
            continue

    print(f"\n✅ Total Q&A pairs generated: {len(all_qa_pairs)}")
    return all_qa_pairs


# ----------------------------
# QA Database Management
# ----------------------------
def load_qa_pairs():
    """Load existing Q&A pairs from file"""
    return  []
    if not os.path.exists(QA_PAIRS_FILE):
        return []

    with open(QA_PAIRS_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data


def save_qa_pairs(qa_pairs):
    """Save Q&A pairs to file (append mode)"""
    existing_pairs = load_qa_pairs()

    # Add metadata to new pairs
    for pair in qa_pairs:
        pair['timestamp'] = datetime.now().isoformat()
        pair['id'] = len(existing_pairs) + qa_pairs.index(pair) + 1

    # Append new pairs
    existing_pairs.extend(qa_pairs)

    with open(QA_PAIRS_FILE, "w", encoding="utf-8") as f:
        json.dump(existing_pairs, f, ensure_ascii=False, indent=2)

    print(f"💾 Saved {len(qa_pairs)} new Q&A pairs. Total: {len(existing_pairs)}")


# ----------------------------
# Semantic Search with TF-IDF (Multilingual Support)
# ----------------------------
class QARetriever:
    def __init__(self, qa_pairs):
        self.qa_pairs = qa_pairs
        # Removed stop_words to support Malayalam/Manglish
        self.vectorizer = TfidfVectorizer(
            max_features=500,
            ngram_range=(1, 2),
            # No stop_words - supports all languages
        )

        if qa_pairs:
            questions = [pair['question'] for pair in qa_pairs]
            self.question_vectors = self.vectorizer.fit_transform(questions)

    def search(self, query, top_k=5):
        """Find top-k most relevant Q&A pairs for the query"""
        if not self.qa_pairs:
            return []

        query_vector = self.vectorizer.transform([query])
        similarities = cosine_similarity(query_vector, self.question_vectors)[0]

        # Get top-k indices
        top_indices = np.argsort(similarities)[-top_k:][::-1]

        results = []
        for idx in top_indices:
            if similarities[idx] > 0:  # Only include relevant results
                results.append({
                    'qa_pair': self.qa_pairs[idx],
                    'score': float(similarities[idx])
                })

        return results


# ----------------------------
# Chat History Management
# ----------------------------
def save_history(chat_history):
    """Save chat history to file"""
    json_data = []
    for content in chat_history:
        json_data.append({
            "role": content.role,
            "parts": [{"text": part.text} for part in content.parts if part.text]
        })
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(json_data, f, ensure_ascii=False, indent=2)


def load_history():
    """Load chat history from file"""
    if not os.path.exists(HISTORY_FILE):
        return []
    with open(HISTORY_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    contents = []
    for item in data:
        parts = [Part(text=p['text']) for p in item.get('parts', []) if p.get('text')]
        if parts:
            contents.append(Content(role=item['role'], parts=parts))
    return contents


# ----------------------------
# Main Chatbot Function
# ----------------------------
def run_advanced_chatbot():
    print("=" * 70)
    print("🚀 Advanced RAG Chatbot with Smart Chunking & Multilingual Support")
    print("=" * 70)
    print("\n📚 Options:")
    print("1: Add Knowledge")
    # print("2: Add Knowledge from Word (DOCX)")
    # print("3: Add Knowledge from URL")
    # print("4: Add Knowledge from TXT/CSV")
    print("2: Start Chat (Use Existing Knowledge Base)")
    print("3: View Knowledge Base Stats")
    print("=" * 70)

    choice = input("\n👉 Choose an option: ").strip()

    # Handle knowledge addition
    if choice in ["1", "2", "3", "4"]:
        print("\n📖 Extracting text from source...")

        if choice == "1":
            path = input("Enter PDF path: ").strip()
            text = extract_text_from_pdf(path)
        # elif choice == "2":
        #     path = input("Enter DOCX path: ").strip()
        #     text = extract_text_from_docx(path)
        # elif choice == "3":
        #     url = input("Enter URL: ").strip()
        #     text = extract_text_from_url(url)
        # elif choice == "4":
        #     path = input("Enter TXT/CSV path: ").strip()
        #     text = extract_text_from_txt(path)

        if not text.strip():
            print("❌ No text extracted!")
            return

        print(f"✅ Extracted {len(text)} characters")

        # AUTOMATIC QA COUNT CALCULATION
        num_pairs = calculate_optimal_qa_count(text)

        print(f"\n⚙️ Auto-calculated: {num_pairs} Q&A pairs will be generated")
        confirm = input("📝 Proceed with this count? (Y/n): ").strip().lower()

        if confirm and confirm != 'y':
            print("❌ Operation cancelled")
            return

        # SMART CHUNKING for large documents
        print("\n🔧 Applying smart chunking strategy...")
        chunks = chunk_text_intelligently(text, chunk_size=10000, overlap=500)
        print(f"✅ Split into {len(chunks)} intelligent chunks")

        # Generate Q&A pairs from all chunks
        qa_pairs = generate_qa_pairs_from_chunks(chunks, num_pairs)

        if qa_pairs:
            save_qa_pairs(qa_pairs)
            print("\n✅ Knowledge base updated successfully!")
            print("💡 You can now start chatting (choose option 5)")
        else:
            print("❌ Failed to generate Q&A pairs")

        return

    # View stats
    elif choice == "3":
        qa_pairs = load_qa_pairs()
        print(f"\n📊 Knowledge Base Statistics:")
        print(f"   Total Q&A Pairs: {len(qa_pairs)}")
        if qa_pairs:
            print(f"   First added: {qa_pairs[0].get('timestamp', 'N/A')}")
            print(f"   Last added: {qa_pairs[-1].get('timestamp', 'N/A')}")
        return

    # Start chat
    elif choice == "2":
        qa_pairs = load_qa_pairs()
        if not qa_pairs:
            print("\n❌ No knowledge base found! Please add knowledge first (options 1-4)")
            return
        print(f"\n✅ Loaded {len(qa_pairs)} Q&A pairs")
        print("🔍 Initializing multilingual search engine...")

        retriever = QARetriever(qa_pairs)

        # Time-based greeting
        greeting = get_time_based_greeting()

        print("\n" + "=" * 70)
        print("💬 Chat Started!")
        print("=" * 70)
        print(f"Bot: {greeting}")
        print("     I'm your AI assistant with specialized knowledge.")
        print("     Ask me anything about the domain!")
        print("     Type 'exit' to quit.\n")

        chat_history = load_history()

        while True:
            user_input = input("You: ").strip()

            if user_input.lower() in ["exit", "quit", "bye"]:
                save_history(chat_history)
                print("\n" + "=" * 70)
                print("👋 Thank you for chatting!")
                print("🙏 Hope it was helpful. Have a great day! Bye! 😊")
                print("=" * 70)
                break

            if not user_input:
                continue

            # Retrieve top 5 relevant Q&A pairs
            print("\n🔍 Searching knowledge base...")
            search_results = retriever.search(user_input, top_k=5)

            if not search_results:
                print("Bot: Sorry, I couldn't find relevant information. 😔")
                print("     Could you rephrase your question?\n")
                continue

            print(f"✅ Found {len(search_results)} relevant matches\n")

            # Build context from top results
            context_parts = []
            for i, result in enumerate(search_results, 1):
                qa = result['qa_pair']
                score = result['score']
                context_parts.append(
                    f"Q{i}: {qa['question']}\n"
                    f"A{i}: {qa['answer']}\n"
                    f"(Relevance: {score:.2f})"
                )

            context = "\n\n".join(context_parts)

            # Generate response using Gemini with retrieved context
            prompt = f"""
You are a helpful AI assistant with domain-specific knowledge.

Based on the following relevant Q&A pairs from the knowledge base, answer the user's question.

Knowledge Base Context (Top 5 Matches):
{context}

User Question: {user_input}

Instructions:
1. Synthesize information from the provided Q&A pairs
2. Give a natural, conversational answer in English
3. Be helpful and friendly
4. If the question isn't fully covered, say so honestly
5. Don't just repeat the Q&A pairs verbatim - create an original response

Answer:
"""

            try:
                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=prompt
                )
                answer = response.text.strip()

                print(f"Bot: {answer}\n")

                # Update chat history
                chat_history.append(Content(role="user", parts=[Part(text=user_input)]))
                chat_history.append(Content(role="model", parts=[Part(text=answer)]))

            except Exception as e:
                print(f"❌ Error: {e}\n")
    else:
        print("⚠️ Invalid choice!")


# ----------------------------
# Entry Point
# ----------------------------
if __name__ == "__main__":
    run_advanced_chatbot()

