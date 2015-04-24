'''
Created on Feb 5, 2015

@author: Tuan Do
'''
import numpy


class InternalIndex(object):
    '''
    classdocs
    '''


    def __init__(self, clusters):
        '''
        clusters = [ array of Clusters ]
        '''
        self.clusters = clusters
    
    def get_davies_bouldin_index(self):
        
        clusters_distances = numpy.zeros((len(self.clusters), len(self.clusters)))
        
        min_diff_from_zero = 1000000000000000000000
        for i in xrange(len(self.clusters)):
            for j in xrange(len(self.clusters)):
                clusters_distances[i, j] = self.clusters[i].get_distance(self.clusters[j])
                if clusters_distances[i, j] != 0 and min_diff_from_zero > clusters_distances[i, j] :
                    min_diff_from_zero = clusters_distances[i, j]
        
        accumlation = 0
        for i in xrange(len(self.clusters)):
            max_val = 0
            for j in xrange(len(self.clusters)):
                if i != j :
                    centroid_distance = clusters_distances[i, j]
                    if centroid_distance == 0:
                        centroid_distance = min_diff_from_zero
                    current_val = (InternalIndex.get_average_dist_centroid(self.clusters[i]) /
                                   + InternalIndex.get_average_dist_centroid(self.clusters[j])) / centroid_distance
                    if current_val > max_val:
                        max_val = current_val
            accumlation += max_val
                    
        self.index = accumlation / len(self.clusters)
    
    @staticmethod
    def get_average_dist_centroid(cluster):
        aggregate = cluster[0]
        for i in xrange(1, len(cluster)):
            aggregate += cluster[i]
            
        centroid = aggregate / len(cluster)
        distances = [cluster.distance_function(centroid, item) for item in cluster]
        average_dist_centroid = numpy.average(distances)
        
        return average_dist_centroid
    
    def get_dunn_index(self):
        pass