import re


def extract_field(regex, msg):
    # print(regex)
    a = re.search(regex[0], msg)
    if a:
        return a.group(regex[1])
    else:
        return None


dsp_regex = {
    'location': ('Location:(<\/strong>)? (.*)(<br \/> <strong>|\\\\r\\\\n)Size:', 2),
    'rent': ('Rent:(<\/strong>)? \\\\xc2\\\\xa3(\d*\.?\d*) (psf)?', 2),
    'size': ('Size:(<\/strong>)? (.*)\\\\r\\\\nRent:', 2),
    'size_min': ('Size:(<\/strong>)? (\d{1,3}(,\d{3})*(\.\d+)?) (\\\\xe2\\\\x80\\\\x93|-|\\\\x96|&ndash;)', 2),
    'size_max': ('Size:(<\/strong>)? \d{1,3}(,\d{3})*(\.\d+)? (\\\\xe2\\\\x80\\\\x93|-|\\\\x96|&ndash;) '
                 '(\d{1,3}(,\d{3})*(\.\d+)?)', 5),
    'date_posted': ('Date posted:(<\/strong>)? (.*)(\\\\r\\\\n|<br /> <strong>)Lease:', 2),
    'lease': ('Lease:(<\/strong>)? (.*)(<br \/> <strong>|\\\\r\\\\n)Rates:', 2),
    'rates': ('Rates:(<\/strong>)? \\\\xc2\\\\xa3(\d{1,3}(,\d{3})*(\.\d+)?)', 2),
    'service': ('Service:(<\/strong>)? \\\\xc2\\\\xa3(\d{1,3}(,\d{3})*(\.\d+)?)', 2)
    }


acq_regex = {
    'areas': ('Location:<\/strong> (.*)(<br \/> <strong>|\\\\r\\\\n)Size:', 1),
    'size': ('Size:<\/strong> (.*) <br \/> <strong>Date posted:', 1),
    'size_min': ('Size:(<\/strong>)? (\d{1,3}(,\d{3})*(\.\d+)?) (\\\\xe2\\\\x80\\\\x93|-|\\\\x96|&ndash;)', 2),
    'size_max': ('Size:(<\/strong>)? \d{1,3}(,\d{3})*(\.\d+)? (\\\\xe2\\\\x80\\\\x93|-|\\\\x96|&ndash;) '
                 '(\d{1,3}(,\d{3})*(\.\d+)?)', 5),
    'date_posted': ('Date posted:<\/strong> (.*)<\/div>', 1)
    }