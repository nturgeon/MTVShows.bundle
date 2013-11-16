MTVShows.bundle
===============

This is a Plex channel that produces videos for the MTV website for shows

IMPORTANT NOTE FOR MANAGEMENT AND DESIGN OF CHANNEL AND URL SERVICE
All the videos offered on MTV Netwsork websites have parts. The number of parts for any video must be determined ahead of time and at least
a range of number of parts must be hard coded into the URL service. These playlist have the word videolist in the URI used in the MRSS feed
accessed to find the video file locations of the videos associated with a particular page. Full episodes are video playlist, but playlists
can also be an associated froup of video clips like music videos or bunus clips.

A video clip playlist can contain a widely varying number of video clips. Full episodes may have 4 to 10 parts but a video clip 
playlist can have anywhere from one to 40 parts. These video playlist urls are accepted and processed by with URL service,
but unlike full episodes, only  the first video in the playlist will play since the number of parts cannot be determined or even estimated. 
Just like full episodes, these video playlist include a 7 digit number in the parameters of the URL and have the word "videolist"
instead of just "video" in the uri/mgid used in the MRSS feed url for accessing the video page. These video playlist urls are accepted 
and processed by with URL service, but only the first video in the playlist will play. Since it is impossible to determine 
the correct number of parts in URL service, we check for playlist urls in the channel and create a list of all the videos in 
that playlist to ensure all the videos will play.

