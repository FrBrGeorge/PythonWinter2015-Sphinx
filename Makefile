CTARGETS=docs

all:
	make -C docs html

clean:
	for C in $(CTARGETS); do $(MAKE) -C $$C clean; done

