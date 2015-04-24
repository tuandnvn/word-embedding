#!/usr/bin/perl -w

use strict "vars";
use Getopt::Std;
use Math::Random qw (random_binomial random_uniform_integer);
use Time::HiRes qw(gettimeofday );
use PDL;

my $usage;
{
$usage = <<"_USAGE_";

This script takes as input a list of tuples in (tab- or
space-delimited) format:

row-element col-element score

It is assumed that the tuples are ordered so that all lines containing
the same col-element are adjacent in the list.

The script transforms the input into a row-element-by-random-dimension
matrix applying the random indexing method (Sahlgren, 2005).

It sends to standard output one tab-delimited line for each input row
element (not necessarily in the same order as in input), with the
corresponding reduced representation values:

row-element i1 i2 ... id

where each iN is a value for a random dimension, and d is specified
number of dimensions (10000 by default, or use -d option).

Note that there is no guarantee that the indices representing
different col-elements are unique.

Optionally, if the -r option is passed followed by a filename, a file
with the corresponding file name is generated, containing, for each
input col element, a (tab-delimited) line with:

col-element i1 i2 ... id

that are the random indices used to construct the matrix sent to
standard output.

The following options can be specified:

-d: number of dimensions of vectors (default: 10000)

-h: print this documentation and exit

-p: probability of a dimension having a non-zero value when a context
 vector is initialized (default: .005)

-r ranind-file: if this option is specified, random indices are
 printed out to a file called ranind-file

-v[1|2]: if set to 1, prints a progress report, if set to 2 prints
  timing information and the progress report (2 level is only intended
  for debugging purposes)

Some usage examples:

ri-from-tuple-list.pl -h | more

ri-from-tuple-list.pl tuples.txt > ri-mat.txt

ri-from-tuple-list.pl -r rind.txt tuples.txt tuples.txt > ri-mat.txt

ri-from-tuple-list.pl -r rind.txt -u freq-items.txt -d 1800 tuples.txt > ri-mat.txt


Notice that the script relies on the following non-standardly
distributed Perl modules: Math::Random and PDL.

Copyright 2009, Marco Baroni

This program is free software. You may copy or redistribute it under
the same terms as Perl itself.

_USAGE_
}
{
    my $blah = 1;
# this useless block is here because here document confuses
# emacs
}


################## sub-routines ##################

my %opts = ();

getopts('d:hp:r:u:v:',\%opts);

if ($opts{h}) {
    print $usage;
    exit;
}

# if v(erbose) is 1
# print progress report every 10k processed lines
# if it is 2, report timing of ri generation

# timing stuff
my $t1;
my $t2;

my $progress = 0;
my $verbose;
if (!$opts{v}) {
    $verbose = 0;
}
elsif ($opts{v}==1) {
    $verbose = 1;
}
elsif ($opts{v}==2) {
    $verbose = 2;
}
else {
    die "v option only takes values 1 and 2, not $verbose";
}

# random index dimensions
my $d = 10000;
if ($opts{d}) {
    $d = $opts{d};
    if (int($d) != $d || $d < 1) {
	die "dimensions should be a positive integer number, not $d";
    }
}

# probability of a non-zero element of index
my $nonzero_prob = .005;
if ($opts{p}) {
    $nonzero_prob = $opts{p};
    if ($nonzero_prob > 1 || $nonzero_prob < 0) {
	die "illegal probability $nonzero_prob";
    }
}

# if specified, an output file to print the random indices to
my $random_index_file;
if ($opts{r}) {
    $random_index_file = $opts{r};
    if (-e $random_index_file) {
	die "file $random_index_file already exists";
    }
    open RIFILE,">$random_index_file"
	or die "could not open $random_index_file for writing";
}
# just in case, since we are going to use this variable
# also to test whether we need to print random indices
else {
    undef($random_index_file);
}


################## main loop ##################

# history_vectors is a hash to store the ri-based representations of the row
# elements
my %history_vectors = ();
# a variable to hold the current random index
my $ri;
# a variable to keep track of col el of previous line, to see if we
# need to generate a new ri or not
my $prev_col_el = "";
while (<>) {
    chomp;
    # we expect row-el col-el score
    my ($row_el,$col_el,$score) = split "[\t ]+",$_;
    # if this is new col-el, we undefine previous ri and generate a new one
    # (we also print it if we have an open ri file)
    if ($col_el ne $prev_col_el) {
	undef($ri);

	$ri =  generate_random_index();

	# we must print random index if asked to
	if (defined($random_index_file)) {
	    print RIFILE $col_el,"\t";
	    print RIFILE join "\t",swcols($ri);
	    print RIFILE "\n";
	}

	# finally, it's time to update the prov col el to current one!
	$prev_col_el = $col_el;
    }

    # we add the random index, multiplied by the score, to the history
    # vector of the row
    $history_vectors{$row_el} += $score * $ri;

    # a counter to print a report in verbose mode
    $progress++;
    if ($verbose && !($progress % 100000)) {
	print STDERR "$progress tuples processed\n";
    }

}


################## final steps after main loop ##################

# we must undefine the last ri
undef($ri);
# we must close the random index file, if it had been opened
if (defined($random_index_file)) {
    close RIFILE;
}

if ($verbose) {
    print STDERR "now printing output\n";
}

# last but not least, print the history vectors!
foreach my $row_el (keys %history_vectors) {
    print $row_el;
    my @temp_array = swcols($history_vectors{$row_el});
    foreach my $value (@temp_array) {
	if ($value == 0) {
	    print "\t",$value;
	}
	else {
	    printf "\t%.4f",$value;
	}
    }
    print "\n";
    undef @temp_array;
}


if ($verbose) {
    print STDERR "finished\n";
}


################## sub-routines ##################

# generate_random_index
# function that returns a piddle object with a non-0 random index
sub generate_random_index {
    my @index = ();
    my $nonzero_count = 0;

    if ($verbose==2) {
	$t1 = gettimeofday();
    }
    while ($nonzero_count == 0) {
	$nonzero_count = random_binomial(1,$d,$nonzero_prob);
    }
    if ($verbose==2) {
	$t2 = gettimeofday();
	printf STDERR ("nonzero: %.20f\n",$t2-$t1);
	$t1 = gettimeofday();
    }

    my $pos_count = random_binomial(1,$nonzero_count,0.5);

    if ($verbose==2) {
	$t2 = gettimeofday();
	printf STDERR ("positive: %.20f\n",$t2-$t1);
	$t1 = gettimeofday();
    }

    @index = (0) x $d;
    my $i=0;
    while ($i<$pos_count) {
	my $position = random_uniform_integer(1,0,$d-1);
	while ($index[$position]) {
	    $position = random_uniform_integer(1,0,$d-1);
	}
	$index[$position] = 1;
	$i++;
    }
    $i=0;
    while ($i<($nonzero_count-$pos_count)) {
	my $position = random_uniform_integer(1,0,$d-1);
	while ($index[$position]) {
	    $position = random_uniform_integer(1,0,$d-1);
	}
	$index[$position] = -1;
	$i++;
    }
    if ($verbose==2) {
	$t2 = gettimeofday();
	printf STDERR ("indexpop: %.20f\n",$t2-$t1);
    }

    return pdl @index;
}
