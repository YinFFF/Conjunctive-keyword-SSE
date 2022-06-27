CC = gcc
INCPATHS = -I/usr/local/include -Iflint
CFLAGS = -g -Wall -fopenmp -std=c11 -O3 $(INCPATHS)
LDLIBS = -lflint -lgmp -lmpfr -lm -lssl -lcrypto
LDPATH = -L/usr/local/lib -Lflint

CHARM = charm
CHARM_MAC = charm_mac
FHIPE = fhipe
BUILD = $(FHIPE)/build
FLINT_DIR = flint
FLINT_BUILD = flint_build
EXE = $(FHIPE)/gen_matrices

SRC = cryptorand.c gen_matrices.c

OBJPATHS = $(patsubst %.c,$(BUILD)/%.o, $(SRC))

all: $(OBJPATHS) $(EXE)

obj: $(OBJPATHS)


$(BUILD):
	mkdir -p $(BUILD)

flint_config:
	cd $(FLINT_DIR) && ./configure --disable-shared && make -j

$(FLINT_BUILD):
	cd flint && make -j

$(CHARM): FORCE
	cd charm && ./configure.sh --install=. && make

$(CHARM_MAC): FORCE
	cd charm && ./configure.sh --install=. --enable-darwin && make



$(BUILD)/%.o: $(FHIPE)/%.c | $(BUILD)
	$(CC) $(CFLAGS) -o $@ -c $<

install: flint_config $(CHARM) $(OBJPATHS) $(EXE)

install-mac: flint_config $(CHARM_MAC) $(OBJPATHS) $(EXE)

$(EXE): $(OBJPATHS)
	$(CC) $(CFLAGS) -o $@ $(LDPATH) $(OBJPATHS) $(LDLIBS)

clean:
	rm -rf $(BUILD) $(EXE) *~

uninstall:
	make clean && cd flint && make clean && cd ../charm && make clean

FORCE:

