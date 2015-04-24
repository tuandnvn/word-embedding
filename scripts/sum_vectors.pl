#!/usr/bin/perl -w

use strict "vars";
use PDL;
use Getopt::Std;

my $usage;
{
$usage = <<"_USAGE_";
This script takes two input files, one with element-set pairs, the
other with vectors representing the elements, and returns, for each
set in the first file, a sum of the vectors of the elements in the
set.

The element-set file has one (tab- or space-delimited) element-set
pair per line (an element can occur with more than one vector). Lines
in the vector file are also tab- or space-delimited, have a first
field with an element, and the values of the vector representing the
element in the remaining field (it is assumed that all vectors have
the same number of dimensions). Vectors for elements that are not in
any set are ignored, and if an element in a set does not have a vector
in the vector file, it is also ignored (if a set is only made of
elements not in the vector file, it will end up having a zero vector
in the output).

If the option -n is passed, the vectors are normalized before summing.

The (tab-delimited) output has one set per line, followed by its
summed vector.

NB: The script requires PDL to be installed.

Usage:

sum_vectors.pl -h

sum_vectors.pl target-set-file vector-file > outfile

sum_vectors.pl -n target-set-file vector-file > outfile

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

getopts('hn',\%opts);

if ($opts{h}) {
    print $usage;
    exit;
}

my $normalize = 0;
if ($opts{n}) {
    $normalize = 1;
}

my $element_set_file = shift;
my $vector_file = shift;


my %set_list_of_element = ();
my %seen_pairs = ();
my %is_set = ();
open FILE1,$element_set_file or
    die "could not open $element_set_file";
while (<FILE1>) {
    chomp;
    s/\r//g;
    my ($element,$set) = split "[\t ]+",$_;
    if ($seen_pairs{$element}{$set}) {
	next;
    }
    push @{$set_list_of_element{$element}},$set;
    $seen_pairs{$element}{$set} = 1;
    $is_set{$set} = 1;
}
close FILE1;
%seen_pairs = ();

my %summed_vector = ();
my $d = 0;
open FILE2,$vector_file;
while (<FILE2>) {
    chomp;
    s/\r//g;
    my @F = split "[\t ]+",$_;
    if (!$d) {
	$d = $#F;
	# this is the number of dimensions, since there is
	# one extra item (the element)
    }
    my $element = shift @F;

    if (!defined($set_list_of_element{$element}[0])) {
	next;
    }
    foreach my $set (@{$set_list_of_element{$element}}) {
	if ($normalize) {
	    my $temp_raw =  pdl @F;
	    my $temp_length = sqrt(sum($temp_raw**2));
	    if ($temp_length == 0) {
		$summed_vector{$set} += $temp_raw;
	    }
	    else {
		$summed_vector{$set} += $temp_raw / $temp_length;
	    }
	    undef $temp_raw;
	}
	else {
	    $summed_vector{$set} += pdl @F;
	}
    }
}
close FILE2;

foreach my $set (keys %is_set) {
    if (!defined($summed_vector{$set})) {
	$summed_vector{$set} = zeroes($d);
    }
    print $set;
    my @temp_array = swcols($summed_vector{$set});
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


