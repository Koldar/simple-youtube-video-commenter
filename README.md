Introduction
============

A small utility that just create a new comment on the comment section of a single video.
It is BY DESIGN simple, since I don't want developers to spam several video via several messages.


Usage
=====

You first need to authenticate yourself via a "client_secret.json"

```
simple-youtube-video-commenter --videoUrl "www.youtube.com/watch?v=edtfjh" --text "This is an awesome video!" 
```

When executing, you may be asked a google authentication. Follow the link printed and authenticate from the browser.
Then, you will be able to comment automatically for some time.

Getting started
===============

In order to start, you need to:

* Create a developer profile;
* Create a project;
* Setup a some credentials via *Credentials* section;
* Download the credentials: such a file should be named using the following pattern: `^client_secret.*\.json$`;
* Enable the *OAuth consent screen*;
* Go to library and enable the *Youtube Data API v3*; 