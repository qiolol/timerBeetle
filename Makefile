# Why even install this? Well, if you link the script to `/usr/local/bin`, where
# it's potentially run by root, the script should be owned by root too
# (otherwise, non-root users can write to it, injecting instructions that are
# later run as root, which could be pretty bad). But, if the script's repo is
# owned by root, you've got Git/editor headaches since you need root permissions
# to do anything in it. The proper, secure way is to copy it to `/usr/local/bin`
# and make the copy owned by root. However, the script needs asset files (an
# icon and an alarm sound)! So we need to copy those too. "Copying lots of stuff
# with proper ownership and permissions" is known as "installing", so we might
# as well have an installer! This is that installer. (It could also be a wheel
# installed by `pip`, but who needs that when you can use `make` instead?!)

# Set a prefix (unless one's already set):
PREFIX  ?= /usr/local
# Directories to install into
BINDIR   = $(PREFIX)/bin
LIBDIR   = $(PREFIX)/lib/timerBeetle
DATADIR =  $(PREFIX)/share/timerBeetle
# Comporting to the sacred FHS (and assuming `PREFIX` is `/usr/local`), this
# will install the script thusly:  
#     - `/usr/local/bin/timerBeetle`: launcher on `PATH` which runs the script
#     - `/usr/local/lib/timerBeetle/timerBeetle.py`: script (NOT run directly)
#     - `/usr/local/share/timerBeetle/assets/*`: image and sound files

.PHONY: install uninstall clean

# Generate the launcher by replacing the launcher template's dummy paths with
# the real runtime paths via `sed` and then stripping the `.sh.in` extension
# (with the fish thing at the end, where `$<` and `$@` are Make variables).
timerBeetle: timerBeetle.sh.in
	sed -e 's|@LIBDIR@|$(LIBDIR)|g' \
	    -e 's|@DATADIR@|$(DATADIR)|g' \
	    $< > $@

# Copies all files with correct permissions to their installed destinations.
install: timerBeetle
	# Code (0644 = readable, NOT executable cuz the launcher runs the code!)
	install -d "$(DESTDIR)$(LIBDIR)"
	install -m 0644 timerBeetle.py "$(DESTDIR)$(LIBDIR)/"

	# Assets (0644 = readable, not executable); kept under `assets/` to
	# mirror the repo layout, matching `TIMERBEETLE_ASSETS` in the launcher.
	install -d "$(DESTDIR)$(DATADIR)/assets"
	install -m 0644 assets/icon.png        "$(DESTDIR)$(DATADIR)/assets/"
	install -m 0644 assets/alarm_sound.wav "$(DESTDIR)$(DATADIR)/assets/"

	# Generated launcher, already extensionless (0755 = exe'able on `PATH`)
	install -d "$(DESTDIR)$(BINDIR)"
	install -m 0755 timerBeetle "$(DESTDIR)$(BINDIR)/timerBeetle"

# Removes all files copied during installation.
uninstall:
	rm -f  "$(DESTDIR)$(BINDIR)/timerBeetle"
	rm -rf "$(DESTDIR)$(LIBDIR)"
	rm -rf "$(DESTDIR)$(DATADIR)"

# Removes build artifacts (the generated launcher).
clean:
	rm -f timerBeetle
	
# To test this:
# ```
# make clean && make DESTDIR=/tmp/stage install
# find /tmp/stage                               # Verify the tree
# cat /tmp/stage/usr/local/bin/timerBeetle      # Verify baked-in paths
# ```
