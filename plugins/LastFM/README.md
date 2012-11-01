supybot-lastfm
==============

low = grey or brown
super = red
medium = purple
high = green
very high = yellow
very low = light grey

A plugin for supybot that displays various information about a LastFM ID in IRC.

Usage
-----

Showing now playing information:
```
[09:53:33] $np
[09:53:34] KRF listened to “Behind Closed Doors” by Rise Against [The Sufferer & The Witness] more than 1 days ago
```

Showing profile information:
```
[09:53:36] $profile
[09:53:37] KRF (realname: Kevin Funk) registered on May 28, 2006; 23 years old / m; Country: Germany; Tracks played: 32870
```

Showing recent tracks:
```
[10:29:16] $lastfm recenttracks
[10:29:17] KRF’s recenttracks: Zebrahead – The Set-Up, Good Charlotte – Girls & Boys, The All-American Rejects – Another Heart Calls, Angels & Airwaves – Do It For Me Now, Bowling For Soup – The Bitch Song, Yellowcard – Down On My Head, Sum 41 – Confusion And Frustration In Modern Times, Sum 41 – With Me, Goldfinger – Bro, The Offspring – Americana (with a total number of 11 entries)
```

Showing help:
```
[10:28:29] $help lastfm
[10:28:29] (lastfm method [id]) — Lists LastFM info where method is in [friends, neighbours, profile, recenttracks, tags, topalbums, topartists, toptracks]. Set your LastFM ID with the set method (default is your current nick) or specify id to switch for one call.
```

Development
-----------

Feel free to suggest enhancements, I'm happy to receive code contributions

The files `__init__.py` and `plugin.py` provide some documentation.
