#!/usr/bin/perl -w

use strict "vars";
use Getopt::Std;

my $usage;
{
$usage = <<"_USAGE_";
Given a semantic space defined by a set of dimensions, this script
measures the length of a set of target elements on a subset of the
dimensions.

The script takes 3 input files:

- a file with (tab- or space-delimited) target-subset pairs, where
  both the target and the subset are strings, and subset is a code
  used to mark a set of dimensions (both target and subset can be
  repeated across pairs)

- a file with (tab- or space-delimited) dimension-subset pairs, where
  the dimension will be included in those used to measure length for
  the specified subset and the subset codes must be coherent with
  those in previous list (both dimensions and, of course, subset codes
  can be repeated across pairs)

- a file with (tab- or space-delimited) target-dimension-value triples

For each target-subset pair in the first file, we return, in the
output, the length of the target on the dimensions that belong to that
subset (for subset dimensions that do not occur with the target in the
third file, it is assumed that the target has 0 value on such
dimensions).

Usage:

measure-length-on-dimension-subset.pl -h

measure-length-on-dimension-subset.pl file1 file2 file3 > outfile

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

getopts('h',\%opts);

if ($opts{h}) {
    print $usage;
    exit;
}

my $target_subset_file = shift;
my $dimension_subset_file = shift;
my $target_dimensions_file = shift;

my %subsets_of_target = ();
my %length_of_target_on_subset_dimensions = ();

open FILE1, $target_subset_file
    or die "could not open $target_subset_file";
while (<FILE1>) {
    chomp;
    s/\r//g;
    my ($target,$subset) = split "[\t ]+",$_;
    if (defined($length_of_target_on_subset_dimensions{"$target\t$subset"})) {
	next;
    }
    push @{$subsets_of_target{$target}},$subset;
    $length_of_target_on_subset_dimensions{"$target\t$subset"} = 0;
}
close FILE1;



my %is_dimension_in_subset = ();
open FILE2, $dimension_subset_file
    or die "could not open $dimension_subset_file";
while (<FILE2>) {
    chomp;
    s/\r//g;
    my ($dimension,$subset) = split "[\t ]+",$_;
    $is_dimension_in_subset{$subset}{$dimension} = 1;
}
close FILE2;

open FILE3, $target_dimensions_file
    or die "could not open $target_dimensions_file";
while (<FILE3>) {
    chomp;
    s/\r//g;
    my ($target,$dimension,$value) = split "[\t ]+",$_;
    if (!defined($subsets_of_target{$target}[0])) {
	next;
    }
    foreach my $subset (@{$subsets_of_target{$target}}) {
	if ($is_dimension_in_subset{$subset}{$dimension}) {
	    $length_of_target_on_subset_dimensions{"$target\t$subset"} += 
		$value**2;
	}
    }
}
close FILE3;

foreach my $target_subset (keys %length_of_target_on_subset_dimensions) {
    printf("%s\t%.5f\n",$target_subset,
	   sqrt($length_of_target_on_subset_dimensions{$target_subset}));
}

