#!/usr/bin/perl -w

use strict "vars";
use Getopt::Std;
use String::Random qw(random_string);


my $usage;
{
$usage = <<"_USAGE_";
This script takes as input a file in format (tab- or space-)delimited
format:

row_el col_el score

and sends to output a stream where:

- if a col_el is shared by at least two row_el, the corresponding
  input lines are reproduced as is in the output;

- whereas each row_el gets a single line for all the unique col_els it
  occurs with, where the cumulative line col_el is a unique random
  code (unique with respect to the other cumulative col_els, we do not
  check that it is also different from the input col_els, but this is
  highly unlikely), and the score is the squared root of the sum of
  squares of the scores of the row_el with all the unique col_els.

The rationale for using the squared root of the sum of squares is that
in this way, when computing the cosine between two row_el, the
cumulative score will contribute to the length computation exactly as
the separate elements would (while the corresponding component of the
dot product will always be 0).

With option -v, progress information is printed to STDERR.

The script creates a temporary randomly-named directory, and if it
dies before finishing this temp directory will not be canceled.

Note that the

Usage:

compress_hapax_dimensions.pl -h

compress_hapax_dimensions.pl input > output

compress_hapax_dimensions.pl -v input > output

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



my $temp_dir = random_string("cccccccccccccccccccc");
# if a file named that already exists (unlikely!) we try with another random
# name
while (-e $temp_dir) {
    $temp_dir = random_string("cccccccccccccccccccc");
}
`mkdir $temp_dir`;

if ($opts{v}) {
    print STDERR "reading the input\n";
}
# we make copy of in so that we can use the script in a pipe with - as input
open INSTUFF,">$temp_dir/in";
open COLS,">$temp_dir/raw.cols";
while (<>) {
    print INSTUFF $_;
    chomp;
    s/\r//g;
    my @F = split "[\t ]+",$_;
    print COLS $F[1],"\n";
}
close INSTUFF;
close COLS;

if ($opts{v}) {
    print STDERR "counting columns and extracting unique ones\n";
}
`sort -T $temp_dir $temp_dir/raw.cols | uniq -c | gawk '\$1==1{print \$2}' > $temp_dir/unique.cols`;
`rm -f $temp_dir/raw.cols`;

if ($opts{v}) {
    print STDERR "reading unique columns in memory\n";
}

my %is_unique = ();
open UNICOLS,"$temp_dir/unique.cols";
while (<UNICOLS>) {
    chomp;
    $is_unique{$_} = 1;
}
close UNICOLS;
`rm -f $temp_dir/unique.cols`;

if ($opts{v}) {
    print STDERR "producing output\n";
}

my %cumulative_score = ();
open INSTUFF,"$temp_dir/in";
while (<INSTUFF>) {
    chomp;
    s/\r//g;
    my @F = split "[\t ]+",$_;
    if ($is_unique{$F[1]}) {
	$cumulative_score{$F[0]} += $F[2]**2;
    }
    else {
	print join "\t",@F;
	print "\n";
    }
}
close INSTUFF;
`rm -f $temp_dir/in`;
%is_unique = ();

	
if ($opts{v}) {
    print STDERR "printing the cumulative scores\n";
}

my $id = 1;
foreach my $row_el (keys %cumulative_score) {
    my $random_string = random_string("ccccc") . $id;
    printf "%s\t%s\t%.4f\n", $row_el,$random_string,sqrt($cumulative_score{$row_el});
    $id++;
}

`rm -fr $temp_dir`;


if ($opts{v}) {
    print STDERR "done!\n";
}

#  LocalWords:  getopts
