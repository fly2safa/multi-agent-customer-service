# Typing Sound Effects

This directory contains keyboard typing sound effects for the AI agent streaming responses.

## Sound Files Needed

Place the following sound files in this directory:

### 1. **billing-typing.mp3** (or .wav)
- Sound for Billing Agent responses
- Suggested: Soft mechanical keyboard click
- Duration: ~50-100ms

### 2. **technical-typing.mp3** (or .wav)
- Sound for Technical Agent responses
- Suggested: Modern laptop keyboard click
- Duration: ~50-100ms

### 3. **policy-typing.mp3** (or .wav)
- Sound for Policy Agent responses
- Suggested: Vintage typewriter click
- Duration: ~50-100ms

## Where to Find Free Typing Sounds

### Recommended Free Sound Resources:

1. **Freesound.org**
   - https://freesound.org/
   - Search: "keyboard click", "typing", "mechanical keyboard"
   - License: CC0 or CC-BY (attribution)

2. **Zapsplat**
   - https://www.zapsplat.com/
   - Category: Sound Effects > Computer/Keyboard
   - Free with attribution

3. **Mixkit**
   - https://mixkit.co/free-sound-effects/
   - Free for commercial use

4. **BBC Sound Effects**
   - https://sound-effects.bbcrewind.co.uk/
   - Free for personal/educational use

### Quick Setup Instructions:

1. Download 3 different typing sounds (or use the same sound 3 times)
2. Rename them to:
   - `billing-typing.mp3`
   - `technical-typing.mp3`
   - `policy-typing.mp3`
3. Place them in this directory
4. Restart the dev server

### Sound Specifications:

- **Format**: MP3 or WAV
- **Duration**: 50-150ms (short click)
- **File Size**: < 50KB each
- **Sample Rate**: 44.1kHz or 48kHz
- **Bit Rate**: 128kbps minimum

### Fallback

If no sounds are provided, the application will function normally without audio feedback.

### Testing Your Sounds

After adding the files:
1. Start the frontend: `npm run dev`
2. Open browser console (F12)
3. Check for audio loading errors
4. Test by asking any question to an agent
5. Adjust volume using the in-app volume control

---

**Note**: This feature enhances user experience with audible feedback during AI streaming responses. Each agent has a distinct sound to provide audio differentiation.

