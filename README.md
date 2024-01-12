## Inspiration
As engineering students, socializing can be hard. Maintaining eye contact can also be hard. That's why we worked very hard this weekend to make it slightly less hard.
## What it does
Using complex algorithms, GazeGuide is capable of precisely assessing the quality of the conversation you are having, providing helpful tips if it's not going well. Designed for individuals who struggle with communication, GazeGuide guarantees valuable tips and advice, ultimately leading to improved conversations, more friends, and a happier life.

## How we built it
We've merged Adhawk's eye-tracking glasses with Cohere's LLM SDK to craft an amusing twist on social interactions. Here's how we did it:
1. **Adhawk's Glasses**: we use the glasses to track eye movements and communicate with the glasses using the python SDK.
2. **Cohere's LLM**: This SDK generates witty comments based on eye contact behavior.
It's all in good fun, adding laughter to chats!

## Challenges we ran into
The setup of the hardware was quite confusing sometimes and the values read by the eye trackers sometimes seemed inconsistent and shifted despite minimal movement, which required a bit of problem-solving to work around. Working around the lack of a camera was both difficult and interesting as well.

## Accomplishments that we're proud of
1. **3D Wizardry**: We geeked out on quaternions and 3D coordinates for super precise data handling.
2. **No-Camera Vision**: We ditched regular cameras and CV - think "seeing" in a whole new way!
3. **Rolling with Punches**: Setbacks? Yep, we had 'em. But we didn't sweat it. Windows, Mac, and hardware hiccups - we faced 'em all and still kept the vibe alive.
4. **Hack Completion**: We actually managed to finish the hackathon project! Learned tons about teamwork and creative problem-solving along the way.

## What's next for GazeGuide
Improving the gaze on face detection system and integrating the comments/alerts with mobile devices like phones or watches to make reminders more accessible
