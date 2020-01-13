import os

if __name__ == "__main__":
    os.system("java -jar lavalink.jar")

import subprocess
subprocess.call(['java', '-jar', 'lavalink.jar'])


#Put this in bot.py if music is being used
#try:
#    bot.load_extension('cogs.music')
#    print("Loaded music")
#except Exception as e:
#    exc = f'{type(e).__name__}: {e}'
#    print(f'Failed to  load extension {extension}\n{exc}')
