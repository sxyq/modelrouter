"""Training-matrix dimensions retained from the saved V2.1 indexes."""

FULL_LAYERS = {
    'B01': ['L1'], 'B02': ['L2'], 'B03': ['L3'], 'B04': ['L4'],
    'B05': ['L1', 'L2'], 'B06': ['L1', 'L2', 'L3'],
    'B07': ['L1', 'L2', 'L3', 'L4'],
}

FULL_COMBOS = {
    'C01': (['S1'], [1]), 'C02': (['S2'], [1]), 'C03': (['S3'], [1]),
    'C04': (['S1', 'S2'], [1, 1]), 'C05': (['S1', 'S2'], [2, 1]),
    'C06': (['S1', 'S2'], [1, 2]), 'C07': (['S1', 'S3'], [1, 1]),
    'C08': (['S1', 'S3'], [2, 1]), 'C09': (['S1', 'S3'], [1, 2]),
    'C10': (['S2', 'S3'], [1, 1]), 'C11': (['S2', 'S3'], [2, 1]),
    'C12': (['S2', 'S3'], [1, 2]),
    'C13': (['S1', 'S2', 'S3'], [1, 1, 1]),
    'C14': (['S1', 'S2', 'S3'], [2, 1, 1]),
    'C15': (['S1', 'S2', 'S3'], [1, 2, 1]),
    'C16': (['S1', 'S2', 'S3'], [1, 1, 2]),
}

FULL_QUALITY = {'QA': {'Q1'}, 'QB': {'Q1', 'Q2'}, 'QC': {'Q2'}}

FULL_POLICIES = {'PA': 'natural', 'PB': 'independent_unit_balanced', 'PC': 'source_target_balanced'}

MATRIX_TARGETS = {
    'S1': ['human_pairwise_preference'],
    'S2': ['observed_action', 'observed_success', 'observed_failure'],
    'S3': ['prefix_reuse_opportunity', 'output_token_length', 'request_response_tokens',
           'call_quota_units', 'cache_read_tokens', 'call_output_tokens'],
}

MATRIX_ALLOWED_SOURCES = {'TRA-001', 'TRA-002', 'ROUTE-004', 'CACHE-001', 'TIME-001', 'OWN-002'}
