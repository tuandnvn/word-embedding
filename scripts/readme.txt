This archive contains the present readme file and the following perl
scripts:

*build_matrix_from_tuples.pl*
*compress_hapax_dimensions.pl*
*compute_cosines_of_pairs.pl*
*filter_by_field.pl*
*measure-length-on-dimension-subset.pl*
*ri-from-tuple-list.pl*
*sum_vectors.pl*
*svd_matrix_transformer.pl*

We use the perl scripts in this archive, together with command line
tools, to perform core operations on the labeled DM tensor, such as
matricization, cosine comparisons, random indexing compression, etc.

To see the documentation pertaining to a script, invoke it with the -h
option.

A typical pipeline might involve starting from the DM tensor we
provide on the DM website, pre-processing with gawk or similar tool
(in order to concatenate two of the three labels for matricization),
filtering with *filter_by_field.pl* to extract only elements of
interest, and using *build_matrix_from_tuples.pl* to generate a
matrix. If you are working with lots of target elements, and you are
going to use the cosine as your similarity measure, consider making
computations more efficient by passing the input through the
*compress_hapax_dimensions.pl* script before building the
matrix. Instead of generating a full matrix, you can create a reduced
matrix directly from the tuples using random indexing, by applying
*ri-from-tuple-list.pl* to the input.

In the next stage, you can, if you want, reduce the matrix using SVD
(*svd_matrix_transformer.pl*) -- which only makes sense if you did not
use random indexing when creating the matrix.

Next, you can use *compute_cosines_of_pairs.pl* to, well, compute
cosines of pairs of rows in your matrix and you can use
*sum_vectors.pl* to create centroids.

Finally, to measure the length of vectors that represent certain
elements after projection onto a subspace defined by a subset of the
labeled dimensions, you can feed the labeled tensor directly to the
*measure-length-on-dimension-subset.pl* script.

As we said above, to find out about the usage of the scripts run them
with the -h option.
