
def get_tsv_sens(stream):
    curr_sen = []
    for raw_line in stream:
        line = raw_line.strip()
        if not line or line.startswith('#'):
            if curr_sen:
                yield curr_sen
                curr_sen = []
        else:
            fields = line.split('\t')
            curr_sen.append(fields)

    if curr_sen:
        yield curr_sen
