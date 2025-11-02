export async function mockSendMessage(text: string): Promise<string> {
  // simulate processing delay
  await new Promise((r) => setTimeout(r, 1200));

  const replies = [
    "Interesting! Tell me more about that.",
    "Here’s something to think about 🤔",
    "I see your point — let's go deeper.",
    "That’s a cool idea! Want me to expand on it?",
    "Could you clarify what you mean a bit?",
  ];
  const random = replies[Math.floor(Math.random() * replies.length)];
  return `${random}\n\n(You said: "${text}")`;
}
