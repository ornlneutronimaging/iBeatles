def calculate_delta_lambda(distance_source_detector=0, frequency=60):
    return 3956. / ( float(distance_source_detector) * float(frequency) )