from flask import Flask, request, jsonify
import openai
from pytube import Channel
import instaloader

openai.api_key = "your-openai-api-key"

app = Flask(__name__)

def analyze_youtube(channel_url):
    c = Channel(channel_url)
    titles = [video.title for video in c.videos[:5]]
    descriptions = [video.description for video in c.videos[:5]]
    return " ".join(titles + descriptions)

def analyze_instagram(username):
    L = instaloader.Instaloader()
    profile = instaloader.Profile.from_username(L.context, username)
    posts = profile.get_posts()
    captions = [post.caption for post in list(posts)[:5] if post.caption]
    return " ".join(captions)

def generate_email(content, platform):
    prompt = f"""
    You are a professional video editor AI. Analyze this {platform} content:

    {content}

    Find problems or improvement areas (like pacing, branding, thumbnails, storytelling). Then write a professional, friendly outreach email offering editing service. Mention a portfolio at https://editor-kaushik.my.canva.site/.
    """
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
    )
    return response['choices'][0]['message']['content']

@app.route('/analyze', methods=['POST'])
def analyze():
    data = request.get_json()
    link = data.get("link")

    try:
        if "youtube.com" in link or "youtu.be" in link:
            content = analyze_youtube(link)
            email = generate_email(content, "YouTube")
        elif "instagram.com" in link:
            username = link.rstrip("/").split("/")[-1]
            content = analyze_instagram(username)
            email = generate_email(content, "Instagram")
        else:
            return jsonify({"error": "Unsupported platform"}), 400
        return jsonify({"email": email})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
