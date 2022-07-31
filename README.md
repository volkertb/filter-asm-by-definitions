# filter-asm-by-definitions.py

## What is this?

I needed a tool that could automatically preprocess MASM-compatible assembly files and "filter" the code by the
definitions defined in `IFDEF` directives and the like.

## How could this be useful?

The underlying reason why I needed this is that I'm playing with the source code of some DOS sound drivers, notably
[DIGPAK](https://github.com/jratcliff63367/digpak) and [AIL/32](https://github.com/Wohlstand/ail32-sandbox), both of
which have "combined" source files for various device-specific drivers. I want to use the driver source for a specific
sound device as a basis for developing new drivers for more modern sound devices. I expect that filtering out the
sources for the other devices will eliminate noise, and make the code easier to understand and to work with.

Perhaps there are already tools out there for this, or the Microsoft and
[Open Watcom assemblers or linkers](https://github.com/open-watcom/open-watcom-v2) already have some kind of
preprocessing option that already does this, but I couldn't find such options or existing tools, even after some
extensive on-line searching. So I wrote this script. I hope it will proof useful to others too. 🙂

## How do I use it?

I've tested it with the AIL/32 driver sources (originally open-sourced by John Miles), specifically for the Pro Audio
Spectrum (PAS) driver.

You can use [Wohlstand's WASM fork of the AIL/32 sources](https://github.com/Wohlstand/ail32-sandbox), and try the
script on those sources as follows:

```shell
./filter-asm-by-definitions.py dmasnd32.asm --encoding=IBM437 -DPAS -PDPMI -PINT21
```

The `encoding` option is to specify that the source files have Code page 437 encoding, which was typical of source code
in the MS-DOS days. When this option is omitted, the script will assume UTF-8 encoding. the `-D` option is used for
specifying the definitions to use as filter, just like the `-D` option that you would pass to MASM or WASM. You can
specify more than one of these. If you wish to "preserve" certain definitions (as in: keep these as switchable options,
like in the original source file), you can do so with one or more `-P` options. 

## How well does it work?

NOTE: there is not guarantee that this driver supports every possible corner case! I haven't tested it with other
assembly sources yet. Pull Requests for improvement are always welcome.

## I found a problem with this script, or I have a feature request.

Feel free to create an issue on the GitHub page of this project. However, I make no promises on response time, or
whether I will get around to responding to it all. My time is precious, and I have so many hobby projects I prefer to
work on. I hope you understand. Again, pull requests are welcome. 🙂
