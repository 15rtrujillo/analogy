This is a very rudamentary text comparison tool that I use to check assignment submissions in my classes. It works by simply comparing the tokens from each file and reporting assignments that are too similar so I can manually review them.

This works best on plain text files (like code file submissions) but I've also added support for Word documents by utilizing a handly function I found online. Maybe one day I'll add support for PDFs, too, but I usually don't get a lot of those as submissions.

I would like to improve the way I do the text comparison. Right now, it can be circumvented way too easily by simply adding an extra or removing a token. This is particularly disasterous if this modification happens early on in the file. I will need to look into other text-comparison tools and see how they get around this issue.

For now though, this will suffice to catch the "dumb" cheaters.