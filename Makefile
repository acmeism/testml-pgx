export PERL5LIB=../pegex-pm/lib

COMPILE_COMMAND = perl -MPegex::Compiler -e \
    'print Pegex::Compiler->compile_file(shift)->to_

all: testml.pgx.yaml testml.pgx.json

testml.pgx.yaml: testml.pgx Makefile
	$(COMPILE_COMMAND)yaml' $< > $@

testml.pgx.json: testml.pgx Makefile
	$(COMPILE_COMMAND)json' $< > $@

clean:
	rm -f testml.pgx.*
