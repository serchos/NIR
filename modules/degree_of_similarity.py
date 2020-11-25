def degree_of_similarity(distance_CT, distance_max):
    similarity = round((1 - distance_CT/distance_max), 6)
    
    return similarity

def degree_of_similarity_in_percent(distance_CT, distance_max):
    similarity_in_percent = degree_of_similarity(distance_CT, distance_max) * 100
    
    return similarity_in_percent
    
# print(degree_of_similarity_in_percent(10, 58.31))