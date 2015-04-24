#!/usr/bin/perl -w

use strict "vars";
use PDL;
use Getopt::Std;


my $usage;
{
$usage = <<"_USAGE_";
This script takes as input a list of (tab- or space-)delimited string
pairs and a matrix where each row has the row label (a string) as
first field, and the remaining fields constitute the vector
representing the row label in the vector space of interest (fields are
tab- or space-delimited).

Output is, for each pair in input, a tab-delimited line with the two
strings followed by their cosine computed using the vectors in the
matrix. If one or both the elements in the pair are not in the matrix,
we return a 0 cosine (but we send a warning to STDERR if -v option is
specified). We also return 0 as the cosine of anything with a 0
vector. If a pair is repeated in the input, we repeat its output.

Usage:

compute_cosines_of_pairs.pl -h

compute_cosines_of_pairs.pl pair-list matrix > cos-list

NB: The script requires the PDL module.

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


my %opts = ();

getopts('hv',\%opts);

if ($opts{h}) {
    print $usage;
    exit;
}


my $target_file = shift;
my $vector_file = shift;

my %target_items = ();
open TARGETS,$target_file
    or die "could not open $target_file";
while (<TARGETS>) {
    chomp;
    s/\r//;
    my ($i,$j) = split "[\t ]+",$_;
    $target_items{$i} = 1;
    $target_items{$j} = 1;
}
close TARGETS;

if ($opts{v}) {
    print STDERR "target items read in\n";
}

# store normalized vectors
my %vectors = ();

# debug
my $vector_counter = 0;

open VECTORS,$vector_file
    or die "could not open $vector_file";
while (<VECTORS>) {
    chomp;

    my @F = split "[\t ]+",$_;
    my $item = shift @F;

    if (!(defined($target_items{$item}))) {
	next;
    }
    
    my $temp_raw =  pdl @F;
    my $temp_length = sqrt(sum($temp_raw**2));
    if ($temp_length != 0) {
	$vectors{$item} =  $temp_raw / $temp_length;
    }
    else {
	$vectors{$item} = $temp_raw;
    }

    undef($temp_raw);

    @F = ();

    if ($opts{v}) {
	$vector_counter++;
	print STDERR "$vector_counter in memory\n";
    }
}
close VECTORS;

%target_items = ();

if ($opts{v}) {
    print STDERR "matrix read and normalized vectors constructed\n";
}


# measure distance of pairs

open TARGETS,$target_file
    or die "could not open $target_file the second time around";
while (<TARGETS>) {
    chomp;
    s/\r//;
    my ($item1,$item2) = split "[\t ]+",$_;
    my $cosine = 0;

    if ( (!(defined($vectors{$item1}))) ||
	 (!(defined($vectors{$item2}))) ) {
	if ($opts{v}) {
	    print STDERR "either $item1 or $item2 or both were not in matrix\n";
	}
    }
    else {
	$cosine = sum($vectors{$item1}*$vectors{$item2});
    }
    printf("%s\t%s\t%.5f\n",$item1,$item2,$cosine);
    
}
close TARGETS;

%vectors = ();

if ($opts{v}) {
    print STDERR "done\n";
}
