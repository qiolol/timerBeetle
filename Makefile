# Set a prefix (unless one's already set):
PREFIX  ?= /usr/local

# Directories to install into
BINDIR   = $(PREFIX)/bin
LIBDIR   = $(PREFIX)/lib/timerBeetle
DATADIR =  $(PREFIX)/share/timerBeetle

.PHONY: install uninstall clean

# Generate the launcher with the real runtime paths baked into the launcher
# template.
# 
# (No `DESTDIR` here; these are the paths as seen on the target system.)
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

	# Launcher (0755 = executable, on `PATH`; installed WITHOUT the `.sh`)
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
