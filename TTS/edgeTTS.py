import asyncio
from edge_tts import Communicate


async def text_to_speech(text, output_file="output.mp3"):
    communicate = Communicate(text, voice="zh-CN-XiaoxiaoNeural")
    await communicate.save(output_file)
    print(f"语音已保存到 {output_file}")

text = """In our lives, we constantly seek friends who understand us. Nowadays, it is often debated whether modern technology is making people more sociable or less sociable. In my opinion, modern technology has made people more sociable for several reasons.
Firstly, mobile phones and social media platforms allow us to connect with others more easily. For example, by checking someone’s social media profile, you can learn about their hobbies and preferences. If you like a girl, for instance, you can find out her favorite things and choose a suitable gift. This thoughtful gesture might help you build a closer relationship with her. In this way, technology facilitates meaningful connections that might not happen in traditional face-to-face interactions.
Secondly, online gaming and virtual communities provide opportunities to meet like-minded people. Many individuals, especially those who prefer staying at home, can connect with others through online games or interest-based forums. For instance, players from different countries can bond over shared goals in a game, creating friendships that cross geographical boundaries. However, it is also important to be cautious when forming online friendships to avoid encountering harmful individuals.
Lastly, technology enables us to find people who share professional interests. For example, as a programmer, I often participate in online programming communities. These platforms allow me to exchange ideas with fellow programmers and seek help for challenging projects. Without modern technology, such connections would be difficult to establish.
In conclusion, I believe modern technology has made it easier for people to be sociable. It provides effective ways to connect with others, whether through personal interests, hobbies, or professional goals. Compared to traditional methods, these new forms of communication are more convenient and inclusive."""
asyncio.run(text_to_speech(text))
