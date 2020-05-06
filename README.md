# Bernard - Discord bot and Head of Behavior

Bernard is my all-purpose Discord bot, built to do whatever I want it, him, to do. Feel free to run your own instance or re-use code (released under the BSD-3-Clause license) if you like.

Features are relatively self-contained in extensions with the more-broadly interesting bits contained in submodules that point to other repositories. To get a complete copy of this repository, including submodules, you'll have to run
```
git clone --recurse-submodules https://github.com/ryanvolz/bernard
```
To run your own instance, provide your bot token as the `DISCORD_TOKEN` environment variable and execute the `bernard.py` script:
```
DISCORD_TOKEN=<token> python bernard.py
```
