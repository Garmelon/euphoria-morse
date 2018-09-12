import asyncio
import configparser
import logging
import re

import yaboli
from yaboli.utils import *


class Morse(yaboli.Module):
	DESCRIPTION = (
		"'morse' converts to and from morse code.\n"
		"In morse code, letters should be separated by spaces and words"
		" separated by a slash '/'. Example: .... . .-.. .-.. --- / - .... . .-. .\n"
		"Any other characters indicate the end of a morse code message."
		" 'morse' will attempt to translate all morse code messages it finds.\n"
	)
	COMMANDS = (
		"!demorse - convert the parent message from morse code\n"
		"!demorse <text> - convert the text from morse code\n"
		"!morse - convert the parent message into morse code\n"
		"!morse <text> - convert some text into morse code\n"
	)
	AUTHOR = "Created by @Garmy using github.com/Garmelon/yaboli\n"
	CREDITS = "Original bot by Leidenfrost.\n"

	SHORT_DESCRIPTION = "convert to and from morse code"
	SHORT_HELP =   "/me converts to and from morse code"

	LONG_DESCRIPTION = DESCRIPTION + COMMANDS          + CREDITS
	LONG_HELP        = DESCRIPTION + COMMANDS + AUTHOR + CREDITS

	MORSE_RE = r"[\.\-\/ ]+"

	TO_MORSE = {
		"a": ".-",
		"b": "-...",
		"c": "-.-.",
		"d": "-..",
		"e": ".",
		"f": "..-.",
		"g": "--.",
		"h": "....",
		"i": "..",
		"j": ".---",
		"k": "-.-",
		"l": ".-..",
		"m": "--",
		"n": "-.",
		"o": "---",
		"p": ".--.",
		"q": "--.-",
		"r": ".-.",
		"s": "...",
		"t": "-",
		"u": "..-",
		"v": "...-",
		"w": ".--",
		"x": "-..-",
		"y": "-.--",
		"z": "--..",
		"1": ".----",
		"2": "..---",
		"3": "...--",
		"4": "....-",
		"5": ".....",
		"6": "-....",
		"7": "--...",
		"8": "---..",
		"9": "----.",
		"0": "-----",
		".": ".-.-.-",
		",": "--..--",
		":": "---...",
		"?": "..--..",
		"'": ".----.",
		"-": "-....-",
		"/": "-..-.",
		"(": "-.--.",
		")": "-.--.-",
		'"': ".-..-.",
		"=": "-...-",
		"+": ".-.-.",
		"×": "-..-",
		"@": ".--.-.",
	}
	FROM_MORSE = {v: i for i, v in TO_MORSE.items()}

	async def on_command_general(self, room, message, command, argstr):
		await self.command_demorse(room, message, command, argstr)
		await self.command_morse(room, message, command, argstr)

	@classmethod
	def from_morse(cls, text):
		words = [word.strip() for word in text.split("/")]
		words_trans = []
		for word in words:
			letters = [letter for letter in word.split(" ") if letter]
			trans = [cls.FROM_MORSE.get(letter, "�") for letter in letters]
			words_trans.append("".join(trans))
		return " ".join(words_trans)

	def to_morse(cls, text):
		words = [word for word in text.split(" ") if word]
		words_trans = []
		for word in words:
			untranslated = ""
			result = []

			# preserve untranslatable sequences of letters
			for letter in word:
				trans = cls.TO_MORSE.get(letter.lower())
				if trans:
					if untranslated:
						result.append(untranslated)
						untranslated = ""
					result.append(trans)
				else:
					untranslated += letter
			if untranslated:
				result.append(untranslated)

			words_trans.append(" ".join(result))

		return " / ".join(words_trans)

	@yaboli.command("demorse")
	async def command_demorse(self, room, message, argstr):
		text = argstr.strip()

		if not text and message.parent:
				msg = await room.get_message(message.parent)
				text = msg.content.strip()

		if not text:
			await room.send("Can't demorse nothing.", message.mid)
			return

		whole = re.fullmatch(self.MORSE_RE, text.strip())
		if whole:
			translated = self.from_morse(whole.group(0))
			await room.send(translated, message.mid)
			return

		matches = re.findall(self.MORSE_RE, text)
		matches = [match for match in matches
		           if match.strip(" /") not in {"", ".", "-", "..."}]

		translated = [self.from_morse(match) for match in matches]

		if not translated:
			await room.send("No morse code found.", message.mid)
			return

		await room.send("\n".join(translated), message.mid)

	@yaboli.command("morse")
	async def command_morse(self, room, message, argstr):
		text = argstr.strip()

		if not text and message.parent:
				msg = await room.get_message(message.parent)
				text = msg.content.strip()

		if not text:
			await room.send("Can't morse nothing.", message.mid)
			return

		lines = text.split("\n")
		translated = [self.to_morse(line) for line in lines]
		await room.send("\n".join(translated), message.mid)

def main(configfile):
	logging.basicConfig(level=logging.INFO)

	config = configparser.ConfigParser(allow_no_value=True)
	config.read(configfile)

	nick = config.get("general", "nick")
	cookiefile = config.get("general", "cookiefile", fallback=None)
	module = Morse()

	bot = yaboli.ModuleBot(module, nick, cookiefile=cookiefile)

	for room, password in config.items("rooms"):
		if not password:
			password = None
		bot.join_room(room, password=password)

	asyncio.get_event_loop().run_forever()

if __name__ == "__main__":
	main("morse.conf")
